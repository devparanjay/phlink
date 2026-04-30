# Phase 1: Chromium Build Foundation — Context

**Gathered:** 2026-04-28
**Status:** Ready for planning
**Mode:** `--auto` (recommended defaults selected by the agent)

<domain>
## Phase Boundary

Establish a documented, repeatable procedure that produces a runnable phlink binary from upstream Chromium stable on macOS, Linux, and Windows. Scaffold the patch-set mechanism and the `.refs/` upstream documentation cache. **No phlink-specific behavior is implemented in this phase** — the build is unmodified Chromium with the phlink name reserved for Phase 3. The actual Chromium checkout and compile happen on the developer's machine; this phase ships the scripts, configs, and docs that make those operations turnkey.

</domain>

<decisions>
## Implementation Decisions

### Repository layout
- **D-01:** Chromium source lives **outside** this repo as a sibling directory (`../chromium-src/`), not as a submodule, vendored copy, or in-repo subdirectory. Rationale: a Chromium checkout is ~50–100 GB and is not a phlink artifact — it's a build dependency.
- **D-02:** This repo (`phlink/`) holds: patches, build scripts, GN argument configs, docs, future bundled extensions/components, and the `.refs/` cache. It does **not** hold Chromium source.

### Patch-set mechanism
- **D-03:** Patches are `git format-patch`-style `.patch` files stored in `patches/` at the repo root.
- **D-04:** A Python apply script (`scripts/apply-patches.py`) applies them to a checkout of `../chromium-src/` in numeric/lexicographic order.
- **D-05:** A refresh script (`scripts/refresh-patches.py`) regenerates patches from a working branch in the Chromium checkout, so devs edit Chromium normally with `git`, then export.
- **D-06:** Phase 1 ships an empty `patches/` directory with a documented format and the apply/refresh tooling. No phlink patches yet.

### Build accelerator
- **D-07:** `sccache` (cross-platform, OSS, MIT/Apache-2.0, distributed cache support) is the recommended local build accelerator. ccache is acceptable on Linux/macOS as a fallback; goma/reclient are out (not OSS-friendly outside Google).

### GN args baseline
- **D-08:** Per-platform GN args files live at `build/gn-args/{linux,mac,win}.gn` with a shared base in `build/gn-args/common.gni`. Initial baseline: `is_debug=false`, `symbol_level=1`, `is_component_build=false`, `enable_nacl=false`, `treat_warnings_as_errors=false`, `chrome_pgo_phase=0`, `use_official_google_api_keys=false`, `google_api_key=""`, `google_default_client_id=""`, `google_default_client_secret=""`. (Telemetry/branding flags layer in Phases 3–4.)

### depot_tools
- **D-09:** Developers install depot_tools at `~/depot_tools` per upstream Chromium docs. The bootstrap script (`scripts/bootstrap.sh` / `.ps1`) automates the clone + PATH guidance but does **not** modify shell rc files automatically.

### `.refs/` upstream docs cache
- **D-10:** Layout is `.refs/<ecosystem>/<project>@<version>/`, each containing fetched docs and a `MANIFEST.json`.
- **D-11:** `MANIFEST.json` schema captures: `name`, `version`, `ecosystem`, `source_url`, `fetch_date` (ISO 8601 UTC), `license` (SPDX id or string), `sha256_of_archive`, `notes`. Schema lives at `scripts/refs/MANIFEST.schema.json`.
- **D-12:** Fetch helper is a shell script (`scripts/refs-fetch.sh`) that takes `--name`, `--version`, `--ecosystem`, `--url`, `--license`, downloads the resource, and writes `MANIFEST.json` automatically. Format chosen for grep-ability and trivial AI-agent indexing.
- **D-13:** `.refs/` itself is gitignored (already in `.gitignore`). Documentation about the cache lives at `docs/dev/refs-cache.md` (tracked).

### CI relationship
- **D-14:** This phase does **not** include CI. Phase 2 stands up the GitHub Actions matrix.

### Documentation surface (Phase 1)
- **D-15:** `docs/dev/build.md` is the single source of truth for "how to build phlink locally." `docs/dev/upstream-tracking.md` documents the rebase strategy and patch lifecycle.

### the agent's Discretion
- Exact wording in docs.
- Internal structure of helper scripts.
- Whether to add convenience wrappers (e.g., `scripts/build.sh`) — yes, light wrappers acceptable but they must call documented `gn`/`autoninja` commands, not hide them.

</decisions>

<specifics>
## Specific Ideas

- Follow upstream Chromium "Checking out and building" guides for each platform as the procedural baseline.
- Bootstrap scripts must be idempotent and safe to re-run.
- Apply script must verify the target Chromium checkout's `git status` is clean before applying, and refuse to apply over a dirty tree by default (with a `--force` override).

</specifics>

<canonical_refs>
## Canonical References

- `docs/dev/PRD.md` §6.1 — Core browser feature parity required from the build
- `docs/dev/PRD.md` §8.1 — OSS-only dependencies constraint
- `docs/dev/PRD.md` §8.4 — `.refs/` structured upstream documentation cache requirement
- `docs/dev/PRD.md` §10.1 "Build base" — track Chromium stable, customizations as bundled extensions/components + minimal patch set
- `.planning/REQUIREMENTS.md` — BLD-01, BLD-02, BLD-06, CORE-01..05, CORE-07
- `.planning/ROADMAP.md` — Phase 1 success criteria

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- None. Greenfield repo containing only `LICENSE` and `docs/dev/PRD.md`.

### Patterns Observed
- None to follow yet.

</code_context>
