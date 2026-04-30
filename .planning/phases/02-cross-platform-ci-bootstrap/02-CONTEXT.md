# Phase 2: Cross-Platform CI Bootstrap — Context

**Gathered:** 2026-04-28
**Status:** Ready for planning
**Mode:** `--auto` (recommended defaults selected by the agent)
**Scope reminder:** scaffolding only — no full Chromium build in CI yet.

<domain>
## Phase Boundary

Stand up the GitHub Actions CI matrix (macOS / Linux / Windows) that exercises everything phlink owns *without* requiring a multi-hour Chromium compile. This phase ships:

1. A reusable workflow that runs lint/syntax checks on the scripts and configs we shipped in Phase 1.
2. A matrix workflow that confirms `scripts/bootstrap.{sh,ps1}` is parseable and that the GN args files are well-formed on each OS.
3. CODEOWNERS, a basic CONTRIBUTING.md, and PR template so the project is reviewable.

Full Chromium-build CI (which requires self-hosted runners with ~100 GB disk and many hours of compute) is **deferred to a later phase** as documented in `docs/dev/PRD.md`. We document the future path in `docs/dev/ci.md` so the next person knows where this is heading.

</domain>

<decisions>
## Implementation Decisions

### CI provider
- **D-01:** GitHub Actions only. No CircleCI/Buildkite/etc. Repo is on GitHub; no need for a second provider.

### Runner strategy
- **D-02:** GitHub-hosted runners only in this phase. `ubuntu-22.04`, `macos-14` (Apple Silicon), `windows-2022`. Self-hosted runners are deferred to the future Chromium-build phase.

### What CI checks (Phase 2 scope)
- **D-03:** Shell script linting via `shellcheck` for all `scripts/*.sh`.
- **D-04:** PowerShell script linting via `PSScriptAnalyzer` for all `scripts/*.ps1`.
- **D-05:** Python script linting via `ruff` (config in `pyproject.toml`) and `python -m py_compile` for all `scripts/*.py`.
- **D-06:** GN args files validated by syntax-checking with `gn format --dry-run` if `gn` is on PATH (skipped gracefully otherwise — depot_tools isn't fetched in CI).
- **D-07:** Markdown lint via `markdownlint-cli2` on `docs/**/*.md` and root `*.md` (excluding `docs/dev/PRD.md` which has its own conventions; configurable via ignore file).
- **D-08:** JSON Schema validation: `scripts/refs/MANIFEST.schema.json` is itself validated as a Draft 2020-12 schema.

### What CI does NOT do (Phase 2)
- **D-09:** No Chromium fetch, no Chromium build, no end-to-end browser tests. Those land in a future phase with self-hosted runners and a build cache.

### Branching & PR policy
- **D-10:** Required checks on `main`: the Phase 2 lint matrix. Direct pushes to `main` blocked except for maintainers.
- **D-11:** Conventional Commits encouraged (not enforced via bot in Phase 2 — defer to a later phase).

### Repo hygiene files
- **D-12:** Add `CODEOWNERS` at repo root pointing all paths to `@devparanjay` initially.
- **D-13:** Add `CONTRIBUTING.md` summarizing workflow + Conventional Commits + how to run lint locally.
- **D-14:** Add `.github/PULL_REQUEST_TEMPLATE.md` with checklist (lint passes, docs updated, no telemetry added, etc.).
- **D-15:** **Note:** the project's existing `.gitignore` excludes `.github/` from this repo specifically. We need to *override that* for the workflow files we're adding — they MUST be tracked. We'll explicitly un-ignore `.github/workflows/`, `.github/CODEOWNERS`, and `.github/PULL_REQUEST_TEMPLATE.md` while keeping the rest (skill files, planning instructions) ignored.

### Caching
- **D-16:** Use `actions/cache` for `ruff`, `shellcheck`, `markdownlint` toolchains where it speeds things up. No Chromium-related caching in this phase.

### Workflow file structure
- **D-17:**
  - `.github/workflows/lint.yml` — fast lint matrix (the main check).
  - `.github/workflows/ci.yml` — orchestrator that calls `lint.yml` (reserved for future `build.yml` as a sibling).

</decisions>

<specifics>
## Specific Ideas

- Pin third-party actions by SHA, not tag (supply-chain hygiene — phlink is a privacy-first project).
- All actions used in Phase 2 must be from `actions/`, `github/`, or well-known orgs (`DavidAnson/markdownlint-cli2-action`).
- Workflows should fail fast (`fail-fast: false` so all OS lanes report).
- Use `GITHUB_TOKEN` with the smallest permissions needed (`contents: read`).

</specifics>

<canonical_refs>
## Canonical References

- [.planning/REQUIREMENTS.md](../../REQUIREMENTS.md) — BLD-03, BLD-04, BLD-05 (cross-platform CI), QUAL-01..03 (lint, formatting, hygiene)
- [.planning/ROADMAP.md](../../ROADMAP.md) — Phase 2 success criteria
- [docs/dev/PRD.md](../../../docs/dev/PRD.md) §6.5 — cross-platform parity
- Phase 1 deliverables — what we're linting

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/*.{sh,ps1,py}` shipped in Phase 1 (commit `815a3c9`) — these become the lint targets.
- `build/gn-args/*.{gni,gn}` — additional lint targets.
- `scripts/refs/MANIFEST.schema.json` — gets self-validated.

### Patterns Observed
- All Phase 1 shell scripts use `set -euo pipefail` and `--help` flags.
- All Phase 1 PowerShell scripts use `[CmdletBinding()]` and `$ErrorActionPreference = 'Stop'`.
- All Phase 1 Python scripts use type hints + `argparse`.

### .gitignore complication
- Repo-level `.gitignore` currently has `.github` (no trailing slash, ignores both `.github` file and dir contents). Phase 2 must add explicit *un-ignore* rules for the workflow files while keeping skill/agent customization files ignored.

</code_context>
