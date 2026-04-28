# tests/branding-audit/

Phase 4.7 (BRND-01) regression gate for unwanted "Chromium" / "Google Chrome" strings in the built phlink bundle.

## Files

- `audit.sh` — automated `strings`-based scan. Exits non-zero on any unexpected match.
- `allowlist.txt` — explicit allowlist with rationale per category.
- `SMOKE.md` — manual smoke checklist for surfaces that automated string scans cannot cover (window titles, about box, menus, etc.).
- `SMOKE-RESULTS-<date>.md` — historical records of manual smoke runs.

## Running the automated audit

```bash
# Defaults to /Volumes/Tools/dev/chromium-src/src/out/Default/phlink.app
bash tests/branding-audit/audit.sh

# Or point at a specific bundle
PHLINK_APP=/path/to/phlink.app bash tests/branding-audit/audit.sh
```

Exit codes:

- `0` — all `(?i)\bchromium\b|google chrome` matches accounted for.
- `1` — unexpected matches found (printed to stderr).
- `2` — bundle / framework binary not found.

## When the audit fails

1. Read the unexpected matches printed by `audit.sh`.
2. Classify each against the categories documented in `allowlist.txt`.
3. If the match is **legitimately user-visible**, write a patch (slot 0013–0029) that fixes it. Add a regression entry to `SMOKE.md` so it's checked manually too.
4. If the match is **not user-visible** (internal symbol, debug path, devtools URL, etc.), add it to `allowlist.txt` under the matching category with a rationale comment.

## Why both an automated audit and a manual smoke checklist

`strings` shows the raw string blob — including `<ph><ex>Chromium</ex></ph>` translation hints, internal symbol names, and source-path debug info. A string appearing in `strings` does NOT mean a user sees it. The smoke checklist (`SMOKE.md`) covers the actual user-visible surfaces (menus, about box, window titles) that the audit can't measure.

## CI integration

The audit script is the standing branding regression gate. Wire into CI under `tests/` once the CI bootstrap (Phase 2) is alive in the cloud. Currently it runs locally, gating phlink rebuilds.
