"""Pure helpers for the 60-tab benchmark — no pytest dependency.

Imported by both `conftest.py` and `test_60_tab_steady_state.py`.
"""

from __future__ import annotations

import contextlib
import json
import os
import socket
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import psutil
import requests

HERE = Path(__file__).resolve().parent
DEFAULT_URLS = HERE / "urls.txt"
WARMUP_SECONDS = float(os.environ.get("BENCHMARK_WARMUP_SECONDS", "30"))
STEADY_SECONDS = float(os.environ.get("BENCHMARK_STEADY_SECONDS", "60"))
SAMPLE_INTERVAL = float(os.environ.get("BENCHMARK_SAMPLE_INTERVAL", "1.0"))
STARTUP_GRACE_SECONDS = 15.0


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def read_urls() -> list[str]:
    src = Path(os.environ.get("BENCHMARK_URLS_FILE", DEFAULT_URLS))
    return [
        ln.strip()
        for ln in src.read_text().splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]


@dataclass
class PhlinkBenchProcess:
    proc: object  # subprocess.Popen, untyped here to keep this module pure
    profile: Path
    devtools_port: int

    @property
    def devtools_base(self) -> str:
        return f"http://127.0.0.1:{self.devtools_port}"


def wait_for_devtools(port: int, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            r = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=1.0)
            if r.ok:
                return
        except requests.RequestException as e:
            last_err = e
        time.sleep(0.25)
    raise RuntimeError(
        f"DevTools never became reachable on port {port} within "
        f"{timeout}s (last error: {last_err!r})"
    )


def open_tabs(bench: PhlinkBenchProcess, urls: list[str]) -> list[dict]:
    """Open one tab per URL via DevTools `/json/new`.

    The DevTools HTTP endpoint takes the URL as a literal path-query
    suffix (`PUT /json/new?<url>`); it is *not* a standard query
    parameter. PUT is the supported verb since M111.
    """
    targets = []
    for url in urls:
        r = requests.put(
            f"{bench.devtools_base}/json/new?{quote(url, safe=':/?#&=')}",
            timeout=10.0,
        )
        r.raise_for_status()
        targets.append(r.json())
    return targets


def write_report(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = max(0, min(len(s) - 1, round((pct / 100.0) * (len(s) - 1))))
    return float(s[k])


def summarize(values: list[float]) -> dict:
    if not values:
        return {"p50": 0.0, "p95": 0.0, "max": 0.0, "n": 0}
    return {
        "p50": percentile(values, 50),
        "p95": percentile(values, 95),
        "max": max(values),
        "mean": statistics.fmean(values),
        "n": len(values),
    }


def walk_processes(root: psutil.Process) -> list[psutil.Process]:
    procs = [root]
    with contextlib.suppress(psutil.NoSuchProcess):
        procs.extend(root.children(recursive=True))
    return procs


def sample_tree(root: psutil.Process) -> dict:
    rss = 0
    per_proc_rss: list[int] = []
    cpu = 0.0
    n = 0
    for p in walk_processes(root):
        try:
            mi = p.memory_info()
            rss += mi.rss
            per_proc_rss.append(mi.rss)
            cpu += p.cpu_percent(interval=None)
            n += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {
        "rss_total": rss,
        "rss_per_proc": per_proc_rss,
        "cpu_total": cpu,
        "process_count": n,
    }
