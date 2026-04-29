"""60-tab steady-state perf benchmark.

This is the harness; it does not enforce a budget. It writes a JSON
report to `BENCHMARK_REPORT_PATH` (default `benchmark-report.json` in
CWD). Phase 12 will diff two reports against the PRD §9 budgets.

Skipped unless `PHLINK_BINARY` is set.
"""

from __future__ import annotations

import contextlib
import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import psutil

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _bench import (  # noqa: E402
    SAMPLE_INTERVAL,
    STEADY_SECONDS,
    WARMUP_SECONDS,
    PhlinkBenchProcess,
    open_tabs,
    read_urls,
    sample_tree,
    summarize,
    walk_processes,
    write_report,
)


def test_60_tab_steady_state(phlink_bench_process: PhlinkBenchProcess) -> None:
    urls = read_urls()
    assert len(urls) >= 60, f"benchmark needs >=60 URLs, got {len(urls)}"
    urls = urls[:60]

    targets = open_tabs(phlink_bench_process, urls)
    assert len(targets) == 60

    root = psutil.Process(phlink_bench_process.proc.pid)
    # Prime cpu_percent so the first reading is meaningful.
    for p in walk_processes(root):
        with contextlib.suppress(psutil.NoSuchProcess, psutil.AccessDenied):
            p.cpu_percent(interval=None)

    # Warmup: let renderers settle, fonts cache, etc.
    time.sleep(WARMUP_SECONDS)

    rss_total: list[float] = []
    rss_per_proc_max: list[float] = []
    cpu_total: list[float] = []
    proc_count: list[float] = []

    deadline = time.monotonic() + STEADY_SECONDS
    while time.monotonic() < deadline:
        s = sample_tree(root)
        rss_total.append(float(s["rss_total"]))
        rss_per_proc_max.append(float(max(s["rss_per_proc"]) if s["rss_per_proc"] else 0))
        cpu_total.append(float(s["cpu_total"]))
        proc_count.append(float(s["process_count"]))
        time.sleep(SAMPLE_INTERVAL)

    report = {
        "phlink_version": os.environ.get("PHLINK_VERSION", "dev"),
        "timestamp": datetime.now(UTC).isoformat(),
        "tab_count": len(urls),
        "warmup_seconds": WARMUP_SECONDS,
        "steady_seconds": STEADY_SECONDS,
        "sample_interval_seconds": SAMPLE_INTERVAL,
        "rss_total_bytes": summarize(rss_total),
        "rss_per_process_bytes": summarize(rss_per_proc_max),
        "process_count": summarize(proc_count),
        "cpu_percent_total": summarize(cpu_total),
    }

    out = Path(os.environ.get("BENCHMARK_REPORT_PATH", "benchmark-report.json"))
    write_report(out, report)
    print(f"[benchmark] wrote {out}")
    print(
        f"[benchmark] rss_total p50={report['rss_total_bytes']['p50']/1e9:.2f} GB "
        f"p95={report['rss_total_bytes']['p95']/1e9:.2f} GB "
        f"procs={report['process_count']['p95']:.0f}"
    )
