# Phase 2: Cross-Platform CI Bootstrap — Plan

**Created:** 2026-04-28
**Phase goal:** A GitHub Actions matrix runs on every PR and on `main` pushes, lints all Phase 1 deliverables on macOS/Linux/Windows, and is wired up with CODEOWNERS, CONTRIBUTING, and a PR template.
**Depends on:** Phase 1.
**Mode:** YOLO, parallel where dependencies allow.

## Wave Plan

| Wave | Plans (parallel within wave) |
|------|------------------------------|
| 1 | 02-01 (.gitignore tweak + workflows), 02-02 (lint configs), 02-03 (repo hygiene files) |
| 2 | 02-04 (docs/dev/ci.md) — depends on 02-01 |

(All three Wave 1 plans are independent — they touch disjoint paths. We commit them as one coherent unit at end of phase.)

## Plans

### 02-01: GitHub Actions workflows + .gitignore allowlist

**Goal:** A `.github/workflows/lint.yml` matrix runs on PR and `main` push, exercising shellcheck/PSScriptAnalyzer/ruff/markdownlint across `ubuntu-22.04`/`macos-14`/`windows-2022`.

**Tasks:**
1. Edit `.gitignore` to allowlist `.github/workflows/`, `.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md` while keeping everything else under `.github/` ignored.
2. Create `.github/workflows/lint.yml` — single workflow with one job per OS:
   - Common steps: checkout, install language toolchains.
   - **Lint job (Linux):** shellcheck, ruff, markdownlint, JSON Schema self-check.
   - **Lint job (macOS):** shellcheck (brew), ruff, markdownlint.
   - **Lint job (Windows):** PSScriptAnalyzer, ruff, markdownlint.
3. Pin all third-party actions by full-length commit SHA.
4. Restrict permissions: `permissions: contents: read`.
5. Add concurrency group to cancel superseded runs.

**Files created:** `.github/workflows/lint.yml`. **Files edited:** `.gitignore`.

**Verification:**
- `act` or live PR: workflow parses, jobs queue, lint passes on the existing Phase 1 codebase.

**Requirements covered:** BLD-03, BLD-04, BLD-05, QUAL-01.

---

### 02-02: Lint tooling configuration

**Goal:** Each linter has a tracked config so local and CI behavior match.

**Tasks:**
1. Create `pyproject.toml` (or `ruff.toml`) with ruff config: `target-version = "py311"`, line-length 100, select common rule groups, ignore `D` (no docstring nagging — discipline rule).
2. Create `.markdownlint.jsonc` excluding `docs/dev/PRD.md` (PRD has its own style) and `CHANGELOG.md` (when it exists).
3. Create `.shellcheckrc` with sensible defaults (`disable=SC1090,SC1091`).

**Files created:** `pyproject.toml`, `.markdownlint.jsonc`, `.shellcheckrc`.

**Note re `pyproject.toml`:** the existing `.gitignore` ignores `package*.json` but not `pyproject.toml`. Safe to add.

**Verification:**
- `ruff check scripts/` passes locally.
- `markdownlint-cli2 'docs/**/*.md'` passes locally.
- `shellcheck scripts/*.sh` passes locally.

**Requirements covered:** QUAL-01, QUAL-02, QUAL-03.

---

### 02-03: Repo hygiene files (CODEOWNERS, CONTRIBUTING, PR template)

**Goal:** Newcomers know how to contribute; reviewers know what to check.

**Tasks:**
1. Create `.github/CODEOWNERS` — `* @devparanjay` for Phase 2; expand later as the team grows.
2. Create `CONTRIBUTING.md` at repo root — workflow, Conventional Commits, link to `docs/dev/build.md`, link to `docs/dev/upstream-tracking.md`, lint commands.
3. Create `.github/PULL_REQUEST_TEMPLATE.md` — checklist: lint passes, docs updated, no telemetry added, no Google-services regression, OSS-only deps, links the relevant `.planning/` requirement ID(s).

**Files created:** `.github/CODEOWNERS`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`.

**Verification:**
- Files render correctly in GitHub UI (visual check post-push).
- CODEOWNERS syntax validated by GitHub.

**Requirements covered:** QUAL-03 (review hygiene), DOCS-01 (contributor docs).

---

### 02-04: CI roadmap doc

**Goal:** `docs/dev/ci.md` documents what CI does today and what it will do later (full Chromium build matrix on self-hosted runners).

**Tasks:**
1. Create `docs/dev/ci.md`:
   - Today: lint matrix (this phase).
   - Soon: dependency-pinning audit, license check.
   - Later: full Chromium build per OS, smoke tests, perf benchmark (60-tab scenario).
   - Why deferred: build hours and runner cost; needs a hosted Chromium build cache.

**Files created:** `docs/dev/ci.md`.

**Verification:**
- Internal links resolve.
- Cross-referenced from `CONTRIBUTING.md`.

**Requirements covered:** DOCS-01, DOCS-02.

---

## Phase Success Gate (verifier checklist)

- [ ] `.github/workflows/lint.yml` exists and is tracked.
- [ ] All Phase 1 scripts pass linting locally and in CI.
- [ ] `CODEOWNERS`, `CONTRIBUTING.md`, `PULL_REQUEST_TEMPLATE.md` exist.
- [ ] `docs/dev/ci.md` documents current and future CI.
- [ ] `.gitignore` correctly tracks the new `.github/*` files while continuing to ignore skill/agent customization.

## Out of Scope

- Full Chromium build in CI (deferred — needs self-hosted runners).
- E2E browser smoke tests.
- Conventional-commit bot enforcement.
- Release pipeline, artifact signing, code signing (Phase 10).
