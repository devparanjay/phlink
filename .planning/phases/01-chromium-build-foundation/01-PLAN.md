# Phase 1: Chromium Build Foundation — Plan

**Created:** 2026-04-28
**Phase goal:** A documented, repeatable procedure produces a runnable phlink binary from upstream Chromium stable on macOS, Linux, and Windows, with `.refs/` cache scaffolding and a patch-set strategy in place.
**Depends on:** None
**Mode:** YOLO, parallel where dependencies allow.
**Plan-Checker pass:** self-checked (CLI subagents unavailable).

## Wave Plan

| Wave | Plans (parallel within wave) |
|------|------------------------------|
| 1 | 01-01, 01-03 |
| 2 | 01-02 |
| 3 | 01-04 |

01-02 depends on 01-01 (patches operate on a Chromium checkout). 01-04 depends on 01-01, 01-02, 01-03 (it documents them). 01-03 (`.refs/`) is independent of the Chromium checkout.

## Plans

### 01-01: Bootstrap depot_tools + Chromium checkout + GN args baseline

**Goal:** A developer with a fresh machine can run a single bootstrap script to install depot_tools, fetch Chromium stable into `../chromium-src/`, generate a build directory using a per-platform GN args baseline, and produce a working binary.

**Tasks:**
1. Create `scripts/bootstrap.sh` (POSIX) — clones depot_tools to `~/depot_tools`, prints PATH setup instructions, refuses to run if `../chromium-src` already exists unless `--force` is passed.
2. Create `scripts/bootstrap.ps1` (Windows) — Windows equivalent of the above.
3. Create `scripts/sync-chromium.sh` and `scripts/sync-chromium.ps1` — `gclient sync` wrappers that target `../chromium-src/`.
4. Create `build/gn-args/common.gni` — shared GN args baseline.
5. Create `build/gn-args/linux.gn`, `build/gn-args/mac.gn`, `build/gn-args/win.gn` — per-platform GN args that import `common.gni`.
6. Create `scripts/gn-gen.sh` and `.ps1` — wrappers that call `gn gen out/Default --args="$(cat build/gn-args/<platform>.gn)"`.
7. Create `scripts/build.sh` and `.ps1` — autoninja wrappers that call `autoninja -C ../chromium-src/out/Default chrome` (binary still named "chrome" pre-rename — Phase 3 changes that).

**Files created:** `scripts/bootstrap.sh`, `scripts/bootstrap.ps1`, `scripts/sync-chromium.sh`, `scripts/sync-chromium.ps1`, `scripts/gn-gen.sh`, `scripts/gn-gen.ps1`, `scripts/build.sh`, `scripts/build.ps1`, `build/gn-args/common.gni`, `build/gn-args/linux.gn`, `build/gn-args/mac.gn`, `build/gn-args/win.gn`.

**Verification (run by developer, not by this agent):**
- `bash scripts/bootstrap.sh` succeeds on a clean macOS / Linux box.
- `pwsh scripts/bootstrap.ps1` succeeds on a clean Windows box.
- `bash scripts/sync-chromium.sh` populates `../chromium-src/`.
- `bash scripts/gn-gen.sh && bash scripts/build.sh` produces a binary that launches and renders a page.

**Requirements covered:** BLD-01, BLD-02 (foundation), CORE-01..05, CORE-07.

---

### 01-02: Patch-set mechanism

**Goal:** A documented patch-set workflow that survives Chromium stable rebases.

**Tasks:**
1. Create `patches/` directory.
2. Create `patches/README.md` — explains naming convention `NNNN-short-slug.patch`, ordering, format (output of `git format-patch`).
3. Create `patches/.gitkeep` (so the empty dir is tracked).
4. Create `scripts/apply-patches.py` — Python 3 script that:
   - Locates `../chromium-src/` (configurable via `--checkout` flag).
   - Refuses to apply on a dirty tree unless `--force`.
   - Applies all `patches/*.patch` in lexicographic order via `git am`.
   - Aborts and reports the offending patch on conflict.
5. Create `scripts/refresh-patches.py` — Python 3 script that:
   - Takes a base ref (default: `origin/main` of the Chromium checkout) and a head ref.
   - Runs `git format-patch <base>..<head> -o patches/` from inside the checkout.
   - Strips noisy headers (timestamps, signatures) for stable diffs.

**Files created:** `patches/README.md`, `patches/.gitkeep`, `scripts/apply-patches.py`, `scripts/refresh-patches.py`.

**Verification:**
- `python3 scripts/apply-patches.py --dry-run` succeeds on an empty `patches/` directory (no-op).
- `python3 scripts/apply-patches.py` refuses to run against a dirty checkout without `--force`.

**Requirements covered:** BLD-02.

---

### 01-03: `.refs/` upstream docs cache scaffolding

**Goal:** A documented, queryable upstream-docs cache rooted at `.refs/`, with a JSON schema, a fetch helper, and developer docs.

**Tasks:**
1. Create `scripts/refs/MANIFEST.schema.json` — JSON Schema (Draft 2020-12) for `MANIFEST.json` entries.
2. Create `scripts/refs-fetch.sh` — POSIX shell helper:
   - Args: `--name`, `--version`, `--ecosystem`, `--url`, `--license` (SPDX), optional `--notes`.
   - Creates `.refs/<ecosystem>/<name>@<version>/`, downloads the URL into `source.{ext}`, computes sha256, writes `MANIFEST.json`.
   - Validates `MANIFEST.json` against the schema using `python3 -m jsonschema` (graceful fallback if not installed).
3. Create `docs/dev/refs-cache.md` — developer docs explaining the layout, fetch procedure, and intended use by AI agents.

**Files created:** `scripts/refs/MANIFEST.schema.json`, `scripts/refs-fetch.sh`, `docs/dev/refs-cache.md`.

**Verification:**
- `bash scripts/refs-fetch.sh --name jsonschema --version 4.21.0 --ecosystem python --url https://example.invalid --license MIT --dry-run` produces a valid `MANIFEST.json` skeleton.

**Requirements covered:** BLD-06.

---

### 01-04: Build & upstream-tracking documentation

**Goal:** `docs/dev/build.md` is the single source of truth for building phlink locally; `docs/dev/upstream-tracking.md` documents the Chromium stable rebase strategy and patch lifecycle.

**Tasks:**
1. Create `docs/dev/build.md` — covers prerequisites per platform, `scripts/bootstrap.{sh,ps1}` usage, depot_tools, `gclient sync`, GN args, `autoninja`, common pitfalls, sccache setup.
2. Create `docs/dev/upstream-tracking.md` — covers the rebase cadence (every Chromium stable bump), patch refresh procedure, conflict resolution playbook, and how to contribute a new patch.

**Files created:** `docs/dev/build.md`, `docs/dev/upstream-tracking.md`.

**Verification:**
- A developer following `docs/dev/build.md` end-to-end can produce a working binary on at least one platform without external assistance.

**Requirements covered:** BLD-01, BLD-02, BLD-06.

---

## Phase Success Gate (verifier checklist)

- [ ] `scripts/bootstrap.{sh,ps1}` exists and is documented.
- [ ] `scripts/sync-chromium.{sh,ps1}` exists.
- [ ] `scripts/gn-gen.{sh,ps1}` and `scripts/build.{sh,ps1}` exist.
- [ ] `build/gn-args/{common.gni,linux.gn,mac.gn,win.gn}` exist with the documented baseline flags.
- [ ] `patches/` exists with README + apply/refresh scripts.
- [ ] `.refs/` schema, fetch helper, and developer doc exist.
- [ ] `docs/dev/build.md` and `docs/dev/upstream-tracking.md` exist and reference the scripts above.
- [ ] PRD §10.1 "Build base" decisions remain consistent with the patch-set mechanism shipped here.

## Out of Scope (this phase)

- Actually fetching and compiling Chromium (developer-machine task).
- CI integration (Phase 2).
- Branding rename and Google-services strip (Phase 3).
- Telemetry strip (Phase 4).
- Any phlink behavioral patches.
