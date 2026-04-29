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
- **No Chromium release builds.** Release packaging consumes prebuilt Chromium
	outputs from a separate, self-hosted or local build run.

## Release packaging workflows (Phase 10)

Phase 10 adds two manual release workflows:

| Workflow | Trigger | Purpose |
|---|---|---|
| [`.github/workflows/package-installers.yml`](../../.github/workflows/package-installers.yml) | `workflow_dispatch` | Downloads prebuilt `out/Default` artifacts from a Chromium build run and runs the platform installer scripts. |
| [`.github/workflows/release-sign.yml`](../../.github/workflows/release-sign.yml) | `workflow_dispatch` | Produces TUF `targets.json` plus Linux detached signatures from packaged installer artifacts. |

These jobs intentionally do not fetch Chromium or run `autoninja` on
GitHub-hosted runners. That keeps the release path compatible with the repo's
current CI budget while still giving signing and packaging a reproducible entry
point.

`release-sign.yml` is gated by the `release-signing` GitHub environment and
expects these environment secrets:

- `PHLINK_TARGETS_KEY` — Ed25519 TUF targets private key.
- `PHLINK_SNAPSHOT_KEY` — Ed25519 TUF snapshot private key.
- `PHLINK_TIMESTAMP_KEY` — Ed25519 TUF timestamp private key.
- `PHLINK_GPG_SECRET` — ASCII-armored gpg release signing secret key.

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
