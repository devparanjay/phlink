# Phase 5 — Adblock Subsystem (CONTEXT)

> Discuss-phase output for Phase 5. Decisions captured here are inputs
> to `05-PLAN.md`.

## 1. Goal restated

Ship a Chromium-integrated, MV-agnostic ad/tracker blocker built on
Brave's `adblock-rust` (MPL-2.0). Default blocking is **on** the moment
phlink first runs; no extension required. Per-site exceptions live in
the Shields surface (Phase 6 owns the polish; Phase 5 produces the
plumbing + a minimal toggle).

## 2. Hard constraint review

| Constraint                                | Decision                                                                                                                     |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| MPL-2.0 compat with BSD-3-Clause Chromium | Compatible. `adblock-rust` files stay in their own directory; only headers cross the boundary. We do not statically vendor MPL code into BSD-licensed files. |
| No proprietary blobs                      | All filter lists shipped come from EasyList / EasyPrivacy / uBO defaults / Peter Lowe / Brave (all MPL- or CC-BY-SA-compatible). |
| Site isolation stays ON                   | Adblock evaluation runs in the **browser process** at the URLLoader layer. Renderer-side cosmetic filtering is plumbed through Mojo, never via shared memory that crosses sites. |
| No phone-home                             | List updates use phlink's component-updater pointed at `https://updates.phlink.invalid/` (placeholder until Phase 11 stands up real infra). On first run, the bundled snapshot is used so the browser is functional offline. |

## 3. Decisions

### D-01 — Engine choice: `adblock-rust`, vendored into chromium-src

We vendor `adblock-rust` into `chromium-src/third_party/adblock_rust/`
and link it via Chromium's existing Rust support
(`//build/rust/...`). The pin is recorded in this repo as a patch
under `patches/third_party/adblock_rust/`.

**Rationale.** `adblock-rust` is the only mature, MPL-licensed
ABP-grammar engine. uBO's WASM core is GPL and would force the rest of
the binary to GPL; ad-block-plus core is closed; building our own is
out of scope.

### D-02 — Integration point: browser-process URLLoader interceptor

We register a `URLLoaderRequestInterceptor` (or equivalent in the
NetworkService) that consults `adblock-rust` per request. Cosmetic
(element-hiding) rules are pushed to renderers via a Mojo channel
(`phlink.mojom.AdblockRules`).

**Rationale.** Browser-process interception is the only spot that sees
**every** request from every renderer, regardless of frame, worker,
fetch type, or third-party iframe. WebRequest extensions (the MV3
declarativeNetRequest path) are intentionally NOT used: they are
opaque to the user, slower, and unfit for first-class shipping.

### D-03 — Cosmetic filtering: scriptlet injection via DevTools-style protocol

Cosmetic rules (`##.ad-banner` etc.) compile to CSS + JS scriptlets in
`adblock-rust` and are injected per-frame at document-start through a
`content::RenderFrame::ExecuteJavaScript` analogue exposed via Mojo.

**Rationale.** Matches uBO's behaviour. Avoids the renderer needing a
copy of the ruleset (privacy: no shared memory across sites; perf: no
~MB blob duplicated per renderer).

### D-04 — Filter lists shipped on day one

Bundled into the binary at build time, sourced from the upstream
projects under their respective licenses (recorded in
`docs/dev/third-party-licenses.md`):

- EasyList
- EasyPrivacy
- uBO Filters (the default `assets.json` "default" set)
- uBO Filters – Badware risks
- Peter Lowe's Ad and tracking server list
- Brave's "Cookie Notice Blocking" list

User can disable any of these from the Shields list manager (Phase 6
ships the UI; Phase 5 ships the prefs).

### D-05 — Update cadence

Component-updater on Chromium's standard schedule (5 hour delay after
launch, then every 5 hours). Endpoint locked to
`https://updates.phlink.invalid/` — must NOT resolve in dev, must be
overridable via `--phlink-component-updater-url=` for QA. Real endpoint
provisioned in Phase 11.

### D-06 — Storage

Compiled `adblock-rust` `Engine` blobs go in
`<UserDataDir>/Default/phlink/adblock/`. Per-site exception list lives
in a new pref `phlink.adblock.exceptions` (a list of registrable
domains). No Profile-keyed service for v1 — global state is fine
because the engine itself is stateless modulo the rules.

### D-07 — Concurrency model

The `Engine` instance is **per-thread**, owned by the URLLoaderFactory
on the network thread. Updates re-create the engine on a worker thread
and atomic-swap the pointer. No locks on the hot path. This matches
Brave's model.

### D-08 — Telemetry posture

Zero. The engine MUST NOT count blocks, MUST NOT report list-update
failures, MUST NOT emit UMA. Failures are logged to `chrome://net-export`
verbose log only. Block counts are surfaced in the Shields UI via an
in-process counter that never crosses a process boundary except into
the renderer for that page's badge.

### D-09 — Slot ranges (patches)

Phase 5 patches will land in:

- `patches/0090–0099` — adblock-rust integration (BUILD.gn,
  URLLoaderInterceptor, Mojo IPC, default prefs).
- `patches/third_party/adblock_rust/0001–0005` — vendored crate
  pin + the small set of upstream tweaks needed for Chromium's Rust
  bindings.

(Sequential numbering still applies; "0090" is aspirational, real
numbers are assigned by `refresh-patches.py` based on commit order.)

### D-10 — What Phase 5 does NOT ship

- No element picker (Phase 6).
- No custom-list import UI (Phase 6).
- No "block 3rd-party fingerprinting JS" rules beyond what comes in
  the default lists (Phase 7 — Privacy hardening).
- No HTTPS-Everywhere-style rule rewriting (out of scope; HTTPS is
  default upstream now).

## 4. Open question — **build prerequisite**

Phase 5 patches modify chromium-src files (`BUILD.gn`, network service
internals, mojom files). None of that is meaningfully reviewable
without running `autoninja -C out/Default chrome` and at the very
least observing it links. As of 2026-04-28, **no chromium build has
been produced yet** in this project. Two paths forward:

- **A.** Insert a "Phase 4.5 — first build" mini-phase: produce one
  successful Linux + macOS chromium build with the existing six
  patches applied. Output: a smoke-buildable artifact, plus
  identification of any linker/symbol regressions caused by the
  telemetry patches (especially patch 0005, which leaves dead code).
  Estimated cost: ~6 h of build time on the configured sccache, plus
  manual triage.

- **B.** Proceed straight into Phase 5 plan + vendoring without a
  build, and accept that the patches will need rework when the first
  build happens.

**Recommendation: Path A.** Path B is cheaper now but compounds risk.
Patch 0005 (`FetchVariationsSeed` short-circuit) and patch 0006 (DoH
default flip) both touch real network code paths and need a build to
validate. Better to spend the build cost now than discover a typo six
patches deep into Phase 5.

## 5. Status

CONTEXT complete. PLAN deferred until the user picks Path A vs Path B.
