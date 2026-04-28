# Phase 4.7 Smoke Results — 2026-04-29

> Run against `/Volumes/Tools/dev/chromium-src/src/out/Default/phlink.app`, framework version `149.0.7814.0`, phlink commit `47d702e` on `dev-0.1`.
>
> Automated portion: covered by `tests/branding-audit/audit.sh` (PASS — 188 strings matched, all on allowlist).
>
> CLI-verifiable portion (below): completed automatically. GUI-only items left as `PENDING` for the next interactive smoke session — not blocking the phase since Phase 3's BRANDING substitution drives them and we have no regressions in the underlying fields.

## Automated CLI checks

| #  | Surface                | Result                                                              |
|----|------------------------|---------------------------------------------------------------------|
| A1 | `phlink --version`     | **PASS** — outputs `phlink 149.0.7814.0`                           |
| A2 | `Info.plist CFBundleName`              | **PASS** — `phlink`                          |
| A3 | `Info.plist CFBundleDisplayName`       | **PASS** — `phlink`                          |
| A4 | `Info.plist CFBundleIdentifier`        | **PASS** — `org.phlink.phlink`               |
| A5 | `branding-audit/audit.sh`              | **PASS** — 188 strings, all on allowlist     |
| A6 | `tests/network-capture/`               | **PASS** — 1 passed in 71.21s (Phase 4.6)    |

## Items deferred to next interactive smoke (GUI required)

Items 1–14 in `SMOKE.md` (app menu, about box, window title, settings landing, version page, flags, help, dock tooltip, activity monitor, first-run UX, crash dialog, search engine, sync UI). All are **driven by `IDS_PRODUCT_NAME` / `BRANDING`** which Phase 3 already swapped; no regressions are expected, but a human sweep is still required for full PASS.

**Action:** when the next interactive build happens, walk `SMOKE.md` and append `SMOKE-RESULTS-<that-date>.md` with the GUI items filled in. Any FAIL becomes a follow-up patch in slot 0013–0029.

## Phase verification gate

- [x] `audit.sh` exits 0 on current build.
- [x] CLI-verifiable smoke items PASS.
- [ ] GUI smoke items PASS (deferred to next interactive session — non-blocking; underlying mechanism verified).
- [x] `tests/network-capture/` regression green.
- [x] No source patches added in this phase (audit-only — D-02 / 04.7-03 found nothing user-visible to patch beyond what Phase 3 already covered).
