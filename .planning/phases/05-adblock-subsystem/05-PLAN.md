# Phase 5 — Adblock Subsystem — PLAN

> Decisions in `05-CONTEXT.md`. The chromium-src tree at `/Volumes/Tools/dev/chromium-src/src` already has the `chromium_crates_io` infra and the `gnrt` tooling under `tools/crates/run_gnrt.py` — that is the canonical path to vendor `adblock-rust`. Brave's hand-rolled `BUILD.gn` approach is rejected (D-01 stays, but the *mechanism* uses upstream tooling rather than copying Brave's tree wholesale).

## Plans

### 05-01 — Vendor `adblock` crate via `gnrt`

Single-step crate import using Chromium's documented procedure (`third_party/rust/README-importing-new-crates.md`):

1. Add `adblock = "<latest>"` to `//third_party/rust/chromium_crates_io/Cargo.toml` under a new `[dependencies]` block (or extend the existing one).
2. `vpython3 tools/crates/run_gnrt.py vendor` — downloads adblock + transitive deps into `third_party/rust/chromium_crates_io/vendor/`.
3. `vpython3 tools/crates/run_gnrt.py gen` — emits per-crate `BUILD.gn` files under `third_party/rust/<name>/v<major>/`.
4. Add minimal `OWNERS` (`set noparent`, `*`) for each new crate dir.
5. `git add -f third_party/rust/chromium_crates_io/vendor third_party/rust/<adblock dir> third_party/rust/<each new transitive dep dir>`.
6. **Verify it compiles standalone**: `autoninja -C out/Default third_party/rust/adblock/v0_8:lib` (or whatever target name `gen` produced) — must succeed without errors.

**Acceptance:** the `adblock` rlib builds. We do NOT yet link it into `//chrome` — that is plan 5-02.

**Patch slot:** This plan produces a *huge* commit (vendor blob = many MB), which is what every chromium adblock integrator does. The phlink-side patch is captured by `git format-patch` after the chromium-src commit lands; estimated patch size 5–20 MB. Slot 0090 reserved.

### 05-02 — Define the phlink adblock service crate boundary

Create a thin C++ wrapper that owns the `adblock::Engine` and exposes only the methods the URLLoader interceptor will call (`should_block(url, source_url, request_type) -> Decision`). Lives at `chrome/browser/phlink/adblock/` (new directory). Mojom interface defined alongside.

Acceptance: header compiles, unit test stubs link against the rlib.

### 05-03 — URLLoaderRequestInterceptor wiring

Register a `content::URLLoaderRequestInterceptor` in the network service that consults the adblock service for every top-level / subresource request. Cancel blocked requests with `net::ERR_BLOCKED_BY_CLIENT`.

Acceptance: a hand-rolled rule blocking `*.doubleclick.net` actually blocks the request in a manual test.

### 05-04 — Default filter list bundling

Bundle EasyList + EasyPrivacy + uBO defaults + Peter Lowe + Brave cookie-notice list as resources. Compile-time `Engine` snapshot generated at build by a small Python tool that calls into a host-built `adblock` binary. Snapshot loaded at first run.

Acceptance: clean profile loads bundled lists; `should_block("https://doubleclick.net/ad", ...)` returns block.

### 05-05 — Cosmetic filtering (CSS/JS injection)

Plumb cosmetic rules through Mojo to renderers; inject at document-start via existing render-frame extension hook. Per-frame, per-page.

Acceptance: a known cosmetic rule (`example.com##.ad`) hides matching elements on the test page.

### 05-06 — Pref + per-site exception plumbing

Register `phlink.adblock.enabled` (default true) and `phlink.adblock.exceptions` (registrable-domain list, default empty). Surface a single Shields toggle in `chrome://settings/phlink/adblock` (full Shields UI is Phase 6).

Acceptance: toggling pref disables blocking for matching site; engine remains hot.

### 05-07 — Component-updater pin to `updates.phlink.invalid`

Configure the adblock list update endpoint to `https://updates.phlink.invalid/` (intentionally non-resolving in dev — D-05). Updater runs but fails silently (no telemetry).

Acceptance: `chrome://components` lists the adblock component; updater fires, fails to resolve, no stack trace, no UMA emitted.

### 05-08 — Roadmap update + push

Update ROADMAP, commit, push. Phase verification gate: end-to-end manual smoke on a known ad-laden page (ESPN front page, etc.) showing visible blocking.

## Phase verification gate

1. `should_block` called from the URLLoader path returns the right answer for ~10 spot-check URLs.
2. Cosmetic rules hide elements on a test page.
3. Network capture harness still green (no telemetry regressions; no outbound to non-allowlisted hosts).
4. Branding audit still green.
5. Manual smoke: load 5 popular ad-laden sites; visible improvement vs. unmodified Chromium.
