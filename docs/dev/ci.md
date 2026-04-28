# Continuous Integration

> phlink runs CI on every PR and on every push to `main`. This document describes what CI does today, what it will do soon, and what's deliberately deferred.

## Today (Phase 2)

A single workflow — [`.github/workflows/lint.yml`](../../.github/workflows/lint.yml) — runs a lint matrix on three GitHub-hosted runners:

| Runner | Linters |
|---|---|
| `ubuntu-22.04` | `shellcheck`, `ruff`, `python -m compileall`, `markdownlint-cli2`, JSON-Schema self-check |
| `macos-14` | `shellcheck`, `ruff`, `python -m compileall` |
| `windows-2022` | `PSScriptAnalyzer`, `ruff`, `python -m compileall` |

Third-party actions are pinned by full-length commit SHA. The job has `permissions: contents: read` and uses concurrency groups to cancel superseded runs.

### What CI does NOT do today

- **No Chromium fetch or build.** That requires ~100 GB of disk and many hours of compute per OS — not feasible on GitHub-hosted runners and prohibitively expensive on hosted services.
- **No browser smoke tests.** Same reason.
- **No release builds, signing, or installer generation.** Deferred to Phase 10.

## Soon

Planned additions in upcoming phases:

| When | Addition | Notes |
|---|---|---|
| Phase 4 | License / dependency audit | Catches accidental proprietary deps and license-incompatible additions. |
| Phase 11 | Docs link-checker | Catches broken cross-doc links. |
| Phase 12 | Conventional-commit enforcement | Bot check on PR titles / commit subjects. |

## Later: full Chromium build CI

Eventually phlink wants a real "does it actually build?" check on every PR that touches build args, patches, or Chromium-side code. The plan:

1. **Self-hosted runners** in a project-controlled environment (one per OS at minimum).
2. **Hosted Chromium build cache** (sccache distributed mode, or similar OSS solution).
3. **Smoke job** that boots the resulting binary and runs a tiny Playwright suite (open page, navigate, screenshot).
4. **60-tab benchmark** as a nightly cron rather than per-PR (it's the perf north star — see PRD §9).

This is *not* a Phase 2 deliverable. It's a phase of its own once we have a working build to test.

## Running CI checks locally

See [CONTRIBUTING.md](../../CONTRIBUTING.md#linting-run-before-opening-a-pr) for the exact commands.

## Why GitHub Actions

phlink's repo is on GitHub; GitHub Actions ships the matrix runners we need at no cost for OSS. We're not committing to GHA forever — if we move to a different forge, the workflow files would be rewritten, but the project's lint commands are forge-independent (they're just shell/python invocations).
