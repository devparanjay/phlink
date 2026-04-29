# 60-Tab Benchmark Harness

Reproducible PRD §9 perf harness. Boots a fresh phlink profile, opens
60 URLs across N tabs, lets the system settle, then samples
process-tree RAM and CPU for `STEADY_STATE_SECONDS` and writes a JSON
report.

## Usage

```bash
export PHLINK_BINARY=/Volumes/Tools/dev/chromium-src/src/out/Default/Chromium.app/Contents/MacOS/Chromium
python -m pip install -r requirements.txt
pytest tests/benchmark-60tab/ -s -v
```

Override the URL list with `BENCHMARK_URLS_FILE=path/to/urls.txt`
(one URL per line). The default list lives in `urls.txt`.

Override the warm-up window with `BENCHMARK_WARMUP_SECONDS` (default
30) and the sampling window with `BENCHMARK_STEADY_SECONDS` (default
60).

## Output

A JSON report is written to `BENCHMARK_REPORT_PATH` (default
`benchmark-report.json` in CWD) with the schema:

```json
{
  "phlink_version": "...",
  "timestamp": "...",
  "tab_count": 60,
  "warmup_seconds": 30,
  "steady_seconds": 60,
  "rss_total_bytes": { "p50": ..., "p95": ..., "max": ... },
  "rss_per_process_bytes": { "p50": ..., "p95": ..., "max": ... },
  "process_count": { "p50": ..., "p95": ..., "max": ... },
  "cpu_percent_total": { "p50": ..., "p95": ..., "max": ... }
}
```

The harness is intentionally side-effect-free: it does not assert
against a budget. Budgets are tracked separately in PRD §9; CI
compares two report files via `scripts/diff-benchmark.py` (Phase 12).

## Why pytest and not a standalone script?

It reuses the `phlink_binary` / `phlink_profile` fixtures from the
network-capture suite's pattern, ships clean skip behavior when
`PHLINK_BINARY` isn't set (so the suite is safe to add to CI before
every contributor has a build), and integrates with the existing
ruff/pytest tooling.
