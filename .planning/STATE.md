# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-04-28)

**Core value:** A measurably lighter, privacy-by-default Chromium browser whose every default leans toward performance and privacy, without locking users out of customization.
**Current focus:** Phase 12 — Alpha Hardening & v1.0 Release

## Current Position

Phase: 12 of 12
Plan: Phase 11 complete; Phase 12 next (alpha hardening and v1.0 release)
Status: Phase 11 shipped: docs/user/ (install, features, settings, troubleshooting, privacy, README), docs/dev/ gap-fill (release-process.md, extension-model.md, README.md), lychee broken-link CI step. Commit dcecc08.
Last activity: 2026-05-01 — Phase 11 verification passed. Next: Phase 12 alpha hardening & v1.0 release.

Progress: [█████████░] 92% (11 of 12 phases shipped, plus 4.5 / 4.6 / 4.7 / 8.5 / 8.6 interstitials)

## Performance Metrics

**Velocity:**
- Total plans completed: 8 (Phase 1: 4, Phase 2: 4)
- Total execution time: ~1 session

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 4 | 1 session | — |
| 2 | 4 | 1 session | — |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Init: Track Chromium stable; bundled extensions/components + minimal patch set (minimizes upstream-rebase cost)
- Init: `adblock-rust` (MPL-2.0) for Brave Shield parity (G2)
- Init: Default DoH = Cloudflare 1.1.1.1 (no-log); Quad9 and NextDNS preconfigured
- Init: Zero outbound telemetry by default; no opt-in telemetry in v1
- Init: Local-only encrypted profile export/import; no cloud sync in v1
- Init: TUF-style signed updates; no background account
- Phase 10: TUF updater/release pipeline shipped with snapshot-to-target byte binding, stable updater root resource path, native installer scripts, platform signing gates, and release provenance checks.
- Init: Site-isolation upstream defaults stay ON; perf gains via tab-grouping-aware discarder
- Init: Two themes ship in v1 (Light, Dark); community themes deferred to v1.1+
- Init: WCAG AA enforced via automated CI checks on both default themes

### Pending Todos

None yet.

### Blockers/Concerns

- **Tooling**: `gsd-sdk` v0.1.0 (and `@gsd-build/sdk`) on this machine cannot reach the legacy `gsd-sdk query` API and the new `gsd-sdk init` requires `~/.claude/get-shit-done/bin/gsd-tools.cjs` which is not installed. Workflow is being run manually until tooling is fixed or replaced.

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| *(none)* | | | |

## Session Continuity

Last session: 2026-04-28
Stopped at: Phases 1 & 2 complete, both pushed to origin/dev-0.1. Ready for Phase 3 (Identity & Branding Strip) per standing flow rule.
Resume file: None

### Phase 1 deliverables shipped (commit 815a3c9 → 51fe4f7)

- `scripts/bootstrap.{sh,ps1}` — depot_tools install + checkout location guardrail
- `scripts/sync-chromium.{sh,ps1}` — `gclient sync` wrappers for `../chromium-src/`
- `scripts/gn-gen.{sh,ps1}` — concatenates `common.gni` + platform args, runs `gn gen`
- `scripts/build.{sh,ps1}` — `autoninja` wrappers
- `scripts/apply-patches.py`, `scripts/refresh-patches.py` — patch lifecycle
- `scripts/refs-fetch.sh` + `scripts/refs/MANIFEST.schema.json` — `.refs/` cache helper
- `build/gn-args/{common.gni,linux.gn,mac.gn,win.gn}` — GN args baseline
- `patches/README.md` + `.gitkeep` — patch directory scaffolding
- `docs/dev/build.md`, `docs/dev/upstream-tracking.md`, `docs/dev/refs-cache.md`

### Phase 2 deliverables shipped (commit 50196cd)

- `.github/workflows/lint.yml` — macOS/Linux/Windows lint matrix
- `pyproject.toml` (ruff), `.markdownlint.jsonc`, `.shellcheckrc`
- `.github/CODEOWNERS`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`
- `docs/dev/ci.md`
