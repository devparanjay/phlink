"""Pytest fixtures for the 60-tab perf benchmark.

Boots phlink with `--remote-debugging-port=<random>` and a fresh
profile. Skips cleanly when `PHLINK_BINARY` is unset so the suite is
safe to include in CI before every contributor has a build.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Make the suite's helper module importable as `_bench` regardless of
# how pytest is invoked (`pytest tests/`, `pytest tests/benchmark_60tab/`,
# or via an IDE runner).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _bench import (  # noqa: E402
    STARTUP_GRACE_SECONDS,
    PhlinkBenchProcess,
    free_port,
    wait_for_devtools,
)


@pytest.fixture()
def phlink_binary() -> Path:
    raw = os.environ.get("PHLINK_BINARY", "").strip()
    if not raw:
        pytest.skip("PHLINK_BINARY not set; skipping benchmark")
    p = Path(raw).expanduser()
    if not p.exists() or not os.access(p, os.X_OK):
        pytest.skip(f"PHLINK_BINARY={raw!r} is not an executable file")
    return p


@pytest.fixture()
def phlink_bench_process(phlink_binary: Path, tmp_path: Path):
    profile = tmp_path / "profile"
    profile.mkdir()
    port = free_port()
    args = [
        str(phlink_binary),
        f"--user-data-dir={profile}",
        f"--remote-debugging-port={port}",
        "--remote-debugging-address=127.0.0.1",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate",
        "about:blank",
    ]
    log_path = profile / "phlink.stderr.log"
    with log_path.open("wb") as logf:
        proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=logf)
        try:
            wait_for_devtools(port, timeout=STARTUP_GRACE_SECONDS)
            yield PhlinkBenchProcess(proc=proc, profile=profile, devtools_port=port)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
