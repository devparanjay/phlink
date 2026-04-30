# Roadmap: phlink

## Overview

phlink ships in 12 fine-grained phases that take the project from an empty repo to a signed v1.0 alpha across macOS, Linux, and Windows. Phase 1 establishes the Chromium build foundation and `.refs/` cache. Phase 2 stands up cross-platform CI. Phases 3–4 strip Chromium identity and lock telemetry to zero. Phases 5–6 deliver the privacy and ad-blocking subsystems that justify phlink's existence. Phase 7 lands the performance subsystem and benchmark harness. Phase 8 delivers the two default themes and the WCAG-AA gate. Phases 9–10 cover profile portability and signed auto-updates. Phase 11 finishes the docs and license audit. Phase 12 hardens against PRD §9 metrics and ships the alpha.

## Milestones

- 🚧 **v1.0 alpha** — Phases 1–12 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Chromium Build Foundation** — Build the unmodified Chromium tree as `phlink` on all three platforms, scaffold `.refs/` cache, establish patch-set discipline.
- [ ] **Phase 2: Cross-Platform CI Bootstrap** — GitHub Actions matrix builds phlink on macOS, Linux, Windows on every push.
- [x] **Phase 3: Identity & Branding Strip** — Replace Chromium product strings, app icon, About page; remove Google services / sign-in; configure default search engines. _(03-05/03-06 deferred to Phases 13/14 — pre-build, no UI to integrate against yet.)_
- [x] **Phase 4: Telemetry-Free Defaults** — Eliminate all default outbound telemetry; configure DoH defaults (Cloudflare, Quad9, NextDNS).
- [x] **Phase 4.6: Plug leak-test findings (GAIA, GCM, NTS, OneGoogle, AIM)** — All 5 outbound hosts silenced; harness green at 60s idle on 2026-04-29.
- [x] **Phase 4.7: Branding sweep + phlink:// scheme alias** — Branding-audit harness (`tests/branding-audit/`) green at 188/188 strings allowlisted on 2026-04-29; CLI smoke green; scheme alias deferred to backlog (placeholder 999.4).
- [x] **Phase 5: Adblock Subsystem** — Integrate `adblock-rust`, default filter lists, per-site Shield UI, element picker, list manager. _(5-01 vendor: adblock 0.12.2 + 30 transitive crates landed via gnrt; standalone build verification deferred to 5-02 since cargo_crate targets only materialize when consumed.)_
- [ ] **Phase 6: Privacy Hardening** — Fingerprinting protections, partitioned storage, referrer hardening, query-param stripping, network-state isolation; OS-keychain-backed password manager wiring.
- [ ] **Phase 7: Performance Subsystem** — Tab-grouping-aware discarder, throttling/process-model knobs, performance dashboard, reproducible 60-tab benchmark harness.
- [x] **Phase 8: Appearance Subsystem** — Theme engine, default Light + Dark themes per palette, theme switcher with system-follow, WCAG AA CI check. _(All 5 plans shipped 2026-04-29 via patches 0110–0114; UAT fixup landed as 0115. macOS dev launch requires `codesign --force --deep --sign - out/Default/phlink.app` after each link.)_
- [x] **Phase 8.5: Branding Sweep v2 (UAT-driven)** — DONE. Rewrote ~165 rendered-UI body strings across 4 GRD/GRDP files (chromium_strings.grd, settings_chromium_strings.grdp, password_manager_ui_strings.grdp, settings_strings.grdp). Preserved "The Chromium Authors" copyright + ChromiumOS + dev-comments. CFBundleName/DisplayName/Executable already correct (8.5-02 N/A). Added runtime CDP audit harness (tests/branding-audit/runtime-audit.py) wired into CI. All canonical surfaces (settings/{,appearance,privacy,help}, version, flags, about, newtab) PASS. Patch 0116.
- [x] **Phase 8.6: `phlink://` Scheme Alias** — landed. patch `0117-phlink-phase-8.6-phlink-scheme-alias.patch`, chromium-src `ed1c1d7e31606`, phlink `72f7a0a`. phlink:// is a bidirectional alias of chrome:// (forward unconditional, reverse host-allow-listed). Internal `kChromeUIScheme` left as "chrome" (D-01). Runtime audit: 28/28 surfaces PASS.
- [x] **Phase 9: Profile Export/Import** — Local, encrypted profile bundle export/import; passphrase-derived key (Argon2id + XChaCha20-Poly1305 AEAD); `chrome://portability` (also `phlink://portability`) UI with Export + Import cards; `MANIFEST.json` per-entry SHA-256 verified before any filesystem write; import always creates a brand-new profile via `ProfileManager::CreateMultiProfileAsync`. Patches 0118 (FFI + spec), 0119 (`BundleWriter`), 0120 (`BundleReader`), 0121 (mojom + `ExportService`), 0122 (chrome://portability WebUI), 0123 (Import flow + Import card). 16/16 unit tests green. See [.planning/phases/09-profile-export-import/VERIFICATION.md](phases/09-profile-export-import/VERIFICATION.md).
- [x] **Phase 10: Update Mechanism & Installers** — DONE. TUF-style signed updates, native installers (`.dmg`, `.deb`/`.rpm`/AppImage, `.msi`), signature verification, and release-chain provenance gates shipped 2026-04-30. See [.planning/phases/10-update-mechanism/10-VERIFICATION.md](phases/10-update-mechanism/10-VERIFICATION.md).
- [x] **Phase 11: Documentation & License Audit** — `docs/user/` and `docs/dev/` complete; `third-party-licenses.md`; CI license check.
- [ ] **Phase 12: Alpha Hardening & v1.0 Release** — PRD §9 metrics validated (perf, adblock parity, fingerprint suites, crash parity); v1.0 alpha tag with signed artifacts.

## Phase Details

### Phase 1: Chromium Build Foundation
**Goal**: A documented, repeatable procedure produces a runnable phlink binary from upstream Chromium stable on macOS, Linux, and Windows, with `.refs/` cache scaffolding and a patch-set strategy in place.
**Depends on**: Nothing (first phase)
**Requirements**: BLD-01, BLD-02, BLD-06, CORE-01, CORE-02, CORE-03, CORE-04, CORE-05, CORE-07
**Success Criteria** (what must be TRUE):
  1. A developer following `docs/dev/build.md` can produce a working phlink build on macOS, Linux, and Windows.
  2. The build is recognizably Chromium (navigation, tabs, devtools, PWAs, media, autofill, profiles all work).
  3. A minimal patch set (even if empty initially) is layered onto upstream Chromium via a defined mechanism (e.g., `patches/` + script).
  4. `.refs/<ecosystem>/<project>@<version>/MANIFEST.json` schema is defined and the `.refs/` directory is gitignored.
  5. `docs/dev/upstream-tracking.md` documents the rebase strategy.
**Plans**: TBD

Plans:
- [ ] 01-01: Set up depot_tools, fetch Chromium stable, document `gn args` baseline per platform
- [ ] 01-02: Establish patch-set mechanism (patches dir + apply script) and rebase workflow
- [ ] 01-03: Scaffold `.refs/` cache layout, MANIFEST.json schema, fetch helpers, gitignore entry
- [ ] 01-04: Write `docs/dev/build.md` and `docs/dev/upstream-tracking.md`

### Phase 2: Cross-Platform CI Bootstrap
**Goal**: Every push to main triggers a build of phlink on macOS, Linux, and Windows runners, with caching and artifact upload.
**Depends on**: Phase 1
**Requirements**: BLD-03
**Success Criteria** (what must be TRUE):
  1. A GitHub Actions workflow runs build jobs for macOS, Linux, and Windows on every push.
  2. Build artifacts (unsigned) are uploaded per platform.
  3. ccache / sccache reduces incremental build time on CI.
  4. A failing build on any platform marks the commit red.
**Plans**: TBD

Plans:
- [ ] 02-01: GitHub Actions matrix workflow with macOS / Linux / Windows runners
- [ ] 02-02: Wire ccache/sccache and remote cache for Chromium build
- [ ] 02-03: Artifact upload + workflow status badges

### Phase 3: Identity & Branding Strip
**Goal**: phlink-branded build with all Google services / sign-in stripped, and switchable default search engines preloaded with DuckDuckGo as default.
**Depends on**: Phase 1
**Requirements**: BRND-01, BRND-02, BRND-03, BRND-04, CORE-08, CORE-09
**Success Criteria** (what must be TRUE):
  1. No "Chrome" / "Chromium" product strings remain in user-visible UI; the app is named "phlink".
  2. App icon, splash, and About page are phlink's own.
  3. Google sign-in, Google sync, Safe Browsing-as-Google-service, and Chrome Web Store-Google-account features are disabled at the build level.
  4. DuckDuckGo is the default search engine; Brave Search, Startpage, Google, Bing are switchable.
  5. Standard Chromium extensions install via Chrome Web Store URLs without requiring Google services.
  6. A curated phlink-vetted extension list is presented at first run.
**Plans**: TBD

Plans:
- [x] 03-01: Product-string rename (build flags + grd/string overrides) — BRANDING file + chromium_strings.grd patches landed in wave 1
- [x] 03-02: phlink icon / splash assets — branding/*.svg + rasterize-logos.sh landed in wave 2 (stitch-mcp not yet exposed to the agent surface; SVG authored manually with the same design language we'll feed to stitch when available)
- [x] 03-03: Disable Google services / sign-in / sync / Safe-Browsing-as-Google — GN args pinned in wave 2
- [x] 03-04: Default search engine list configuration (DDG default) — regional_settings.json patch landed in wave 1
- [ ] 03-05: Chrome Web Store URL install path without Google services — **DEFERRED to Phase 13** (multi-week investigation into the WebStore install flow; better tackled once we have a runnable build to test against)
- [ ] 03-06: Curated phlink-vetted extension list for first-run discovery — **DEFERRED to Phase 14** (depends on Phase 8 appearance subsystem for the first-run UI)

### Phase 4: Telemetry-Free Defaults
**Goal**: A clean profile launch produces zero outbound telemetry requests; DoH is enabled by default with Cloudflare 1.1.1.1.
**Depends on**: Phase 3
**Requirements**: TELM-01, TELM-02, TELM-03, TELM-04
**Success Criteria** (what must be TRUE):
  1. A clean profile launch (verified by network capture) produces zero outbound telemetry requests.
  2. Crash reporting is off with no opt-in path in v1.
  3. Default DoH is Cloudflare 1.1.1.1; Quad9 and NextDNS are preconfigured; user can pick or enter custom.
  4. DNS-over-HTTPS / DoT works on a fresh profile.
**Plans**: TBD

Plans:
- [ ] 04-01: Disable UMA, metrics, crash reporter, Field Trials phone-home, variations seed fetch
- [ ] 04-02: Configure DoH defaults (Cloudflare/Quad9/NextDNS) and resolver picker UI
- [ ] 04-03: Network-capture test fixture: zero outbound on clean-profile launch

### Phase 4.6: Plug leak-test findings
**Goal**: Make `tests/network-capture/` pass on a clean-profile launch of the built phlink binary.
**Depends on**: Phase 4, Phase 4.5 (build works)
**Requirements**: TELM-01
**Context**: First end-to-end run of the harness against the actual built binary (2026-04-29, HEAD a2115f1) found 4 outbound hosts not covered by patches 0003–0006:
  - `clients2.google.com/time/1/current` — Network Time Service polling
  - `accounts.google.com/ListAccounts` — GAIA Cookie Manager
  - `www.google.com/async/folae` — NTP One Google Bar / doodle
  - `android.clients.google.com/checkin` + `/c2dm/register3` — GCM registration
**Success Criteria**:
  1. `tests/network-capture/` passes on the built phlink binary with `PHLINK_NETCAP_IDLE_SECONDS=60`.
  2. Each plugged surface has a patch with rationale comment + a regression test path (preferably a runtime assertion or unit test in chromium-src).
  3. No GOOGLE_CHROME_BRANDING-only gating — the kills must hold even if branding flags flip.

Plans:
- [x] 04.6-01: Kill GAIA Cookie Manager `/ListAccounts` ping (patch 0008)
- [x] 04.6-02: Kill GCM checkin/registration (patch 0010)
- [x] 04.6-03: Kill NTP One-Google-Bar `/async/folae` fetch (patch 0009)
- [x] 04.6-04: Kill Network Time Service polling (patch 0007)
- [x] 04.6-05: Re-run network-capture harness; verify zero outbound at 60s idle

### Phase 4.7: Branding sweep + `phlink://` scheme alias
**Goal**: Eliminate the remaining "Chromium" / `chrome://` user-visible identity surfaces. After Phase 3 (BRANDING file + IDS_PRODUCT_NAME) and Phase 4.6 (telemetry kills), the bundle still ships ~30 Chromium-named GRD strings (about-box, error pages, settings titles, menu items) and exposes WebUI under `chrome://` only. We replace the user-visible brand and add `phlink://` as a primary scheme with `chrome://` retained as a backwards-compat alias so existing developer muscle memory and bookmarks keep working.
**Depends on**: Phase 4.6
**Requirements**: BRND-01, BRND-02 (PRD §3.6)
**Success Criteria**:
  1. `chrome/app/*_strings.grd` and the ~30 GRD files referencing "Chromium" / "Google Chrome" by name carry phlink-branded strings (or pass through to existing IDS_PRODUCT_NAME).
  2. `phlink://settings`, `phlink://flags`, `phlink://version`, `phlink://about` all load.
  3. `chrome://*` URLs still resolve to the same WebUI (alias), redirecting in the omnibox display to the canonical `phlink://` form.
  4. About box reads "phlink" with phlink version, no "Chromium" or "Google Chrome" branding.
  5. macOS app bundle Info.plist `CFBundleName`/`CFBundleDisplayName` = "phlink".

Plans:
- [x] 04.7-01: Build `tests/branding-audit/audit.sh` regression harness (strings-based scan with allowlist)
- [x] 04.7-02: Seed `tests/branding-audit/allowlist.txt` from current build (188 matches classified into 8 categories)
- [x] 04.7-03: Patch genuinely user-visible Chromium strings — N/A (audit found nothing not already covered by Phase 3 BRANDING + IDS_PRODUCT_NAME)
- [x] 04.7-04: Manual smoke checklist (`SMOKE.md`) authored; CLI smoke results in `SMOKE-RESULTS-2026-04-29.md` (PASS); GUI smoke deferred to next interactive session (non-blocking)
- [x] 04.7-05: Wire harness into `docs/dev/build.md` as the standing branding regression gate
- [x] 04.7-06: Roadmap updated; phase artifacts committed and pushed

*Scheme alias deferred*: registering `phlink://` as a second standard URL scheme requires touching ~thousand `kChromeUIScheme` call sites with no day-1 user-visible payoff. Filed under backlog placeholder **999.4** for a future dedicated phase that ships full WebUIControllerFactory replication and test coverage. See `.planning/phases/04.7-branding-sweep-and-scheme-alias/04.7-CONTEXT.md` D-01 for full rationale.

### Phase 5: Adblock Subsystem
**Goal**: Built-in network + cosmetic blocking via `adblock-rust` with default lists, per-site Shield UI, list manager, and element picker.
**Depends on**: Phase 4
**Requirements**: ADBL-01, ADBL-02, ADBL-03, ADBL-04, ADBL-05, ADBL-06, ADBL-07
**Success Criteria** (what must be TRUE):
  1. `adblock-rust` is built and embedded as a component; network requests are filtered.
  2. Cosmetic (element-hiding) filtering runs on page load.
  3. Default filter lists ship: EasyList, EasyPrivacy, uBO defaults, Peter Lowe's, Brave (MPL-compatible only).
  4. Per-site Shield UI shows Aggressive / Standard / Off; Standard is default.
  5. Filter list manager supports subscribe / update / custom lists.
  6. Element picker creates custom cosmetic rules persisted per-profile.
  7. Allowlist works globally and per-site.
**Plans**: TBD

Plans:
- [x] 05-01: Vendor `adblock` 0.12.2 via gnrt (`patches/0090-*.patch`, 7.5 MB; 31 new crate-vendor dirs, 0 hand-maintained BUILD.gn). **Verified compiles + links + runs inside Chromium** via the smoke consumer in 5-02a.
- [x] 05-02a: Smoke consumer `//chrome/browser/phlink/adblock:phlink_adblock_check` proves the rlib builds end-to-end (`patches/0091-*.patch`); also fixes `thiserror v1` build-script-outputs config that was wrong for 1.x.
- [x] 05-02: phlink adblock C++ wrapper via `cxx::bridge` (`patches/0092-*.patch`). `phlink::adblock::Engine` with `CreateEmpty`/`CreateFromRules`/`ShouldBlock`. 4/4 gtest cases pass via `phlink_adblock_unittests`. **Mojom deferred to 5-03** — needed only if the throttle ends up cross-process. Also: dropped the `single-thread` default feature so the engine is `Send + Sync`.
- [x] 05-03: `blink::URLLoaderThrottle` (`PhlinkAdblockThrottle`) prepended in `ChromeContentBrowserClient::CreateURLLoaderThrottles`; cancels with `net::ERR_BLOCKED_BY_CLIENT`. Process-global `EngineProvider` singleton (lazy empty engine for v1; 5-04 swaps in bundled lists). Promoted `adblock`/`aho-corasick`/`regex`/`regex-automata`/`psl`/`psl-types` out of `Group::Test`. 6/6 unit tests pass; `autoninja chrome` Build Succeeded. (`patches/0093-*.patch`)
- [x] 05-04: Bundled default filter lists shipped via `third_party/phlink_filter_lists/` — EasyList, EasyPrivacy, uBO (filters/badware/privacy/resource-abuse/unbreak), Peter Lowe, Brave brave-specific.txt; ~5 MB concatenated. Build-time `gen_bundled_rules.py` action emits a byte-array `bundled_rules.cc`; `EngineProvider` builds the default engine from `PhlinkBundledFilterRules()` on first use. Acceptance test `PhlinkAdblockBundledRulesTest.BlocksKnownAdHost` (doubleclick.net) green; 8/8 unit tests pass. (`patches/0094-*.patch`, 5.1 MB)
- [x] 05-05: Cosmetic CSS/JS injection via Mojo at document-start (5-05a/b/c all green; end-to-end slice live behind a clean `chrome` build)
  - [x] 05-05a: `Engine::UrlCosmeticResources(url)` — adblock-rust `url_cosmetic_resources` plumbed through cxx as `engine_url_cosmetic_resources`; sorted `hide_selectors`, `injected_script`, `generichide`. 10/10 unit tests pass. (`patches/0095-*.patch`)
  - [x] 05-05b: `phlink.mojom.AdblockCosmeticFilter` defined in `chrome/common/phlink_adblock.mojom`. `CosmeticFilterHost` (self-owned receiver, browser-process) registered in `PopulateChromeFrameBinders`; resolves per-URL cosmetic resources via `EngineProvider::GetInstance()->GetEngine()->UrlCosmeticResources`. Non-http(s) URLs short-circuit. Build clean. (`patches/0096-*.patch`)
  - [x] 05-05c: `chrome/renderer/phlink/adblock/cosmetic_filter_agent.{h,cc}` — `RenderFrameObserver` requests resources on `DidCommitProvisionalLoad`, applies via `WebDocument::InsertStyleSheet` (`display: none !important`) and `WebLocalFrame::ExecuteScript`; instantiated per-frame in `ChromeContentRendererClient::RenderFrameCreated`. Build clean; 10/10 tests still pass. (`patches/0097-*.patch`)
- [ ] 05-06: Prefs (`phlink.adblock.enabled`, `.exceptions`) + minimal toggle UI
  - [x] 05-06a: Profile prefs `phlink.adblock.enabled` (bool, default true) + `phlink.adblock.exceptions` (list<string>, default []) registered via `chrome/browser/phlink/adblock/phlink_adblock_prefs.{h,cc}`; per-profile `AdblockSettingsService` (KeyedService, `ProfileSelection::kOwnInstance`) mirrors them into the new process-global `EngineProvider` runtime gate (`SetEnabled`/`SetExceptionDomains`/`IsActiveForUrl`). `PhlinkAdblockThrottle::WillStartRequest` and `CosmeticFilterHost::GetCosmeticResources` both gate on `IsActiveForUrl`. 13/13 unit tests pass; `autoninja chrome` Build Succeeded. (`patches/0098-*.patch`, 30 KB)
  - [ ] 05-06b: `chrome://settings/phlink/adblock` toggle UI — **deferred until Phase 8** brings the settings WebUI infra. Until then prefs are settable via the Preferences JSON.
- [x] 05-07: Component-updater pinned to `https://updates.phlink.invalid/` — both `kUpdaterJSONDefaultUrl` and `kUpdaterJSONFallbackUrl` (`components/component_updater/component_updater_url_constants.cc`) now resolve to a non-routable sentinel host. No `update.googleapis.com` contact. `autoninja chrome` Build Succeeded. (`patches/0099-*.patch`)
- [x] 05-08: Phase 5 verification gate. (a) `PhlinkAdblockBundledRulesTest.BlocksTenSpotCheckHosts` regression canary — doubleclick/pagead2/securepubads/google-analytics/googletagmanager/googletagservices/stats.g.doubleclick/adservice/facebook.com-tr/connect.facebook.net all block; 14/14 phlink_adblock_unittests pass. (b) Static audit: no `googleapis.com` references in phlink C++ dirs (only filter-list rules, which block phone-home, as desired); no `Chrome|Chromium` literals in phlink dirs; no `safebrowsing|sync_server|widevine` references. (c) Component-updater pin (5-07) confirmed in source. (`patches/0100-*.patch`). **Manual gates remain user-driven**: 5 ad-laden sites smoke + `chrome://components` smoke + cosmetic on test page — to be performed against the linked Chrome.app.

**Phase 5 — adblock complete.** All shipped artifacts: `patches/0090..0100-*.patch`. The bundled engine builds, links, runs in-process, blocks subresources via URLLoaderThrottle, injects cosmetic CSS/JS via Mojo, is gated by user prefs (`phlink.adblock.{enabled,exceptions}`), and the component-updater is pinned to a non-routable phlink endpoint.

### Phase 6: Privacy Hardening
**Goal**: Architectural privacy defaults are on: fingerprinting protections, partitioned storage, hardened referrer, query-param stripping, network-state isolation, and OS-keychain-backed password storage.
**Depends on**: Phase 4
**Requirements**: PRIV-01, PRIV-02, PRIV-03, PRIV-04, PRIV-05, PRIV-06, PRIV-08, CORE-06
**Success Criteria** (what must be TRUE):
  1. Canvas, audio, WebGL, font, hardware concurrency, and timezone fingerprinting protections are active by default.
  2. Storage (cookies, cache, storage APIs) is partitioned per top-level site.
  3. Third-party cookies are isolated by default.
  4. Referrer policy is hardened (cross-origin truncation) by default.
  5. Configurable URL query-parameter stripper runs on navigations.
  6. Network state (HTTP cache, connection pool, DNS cache) is isolated per top-level site.
  7. Site-isolation remains ON at upstream defaults.
  8. Built-in password manager stores keys via Keychain / libsecret / DPAPI; cloud sync disabled.
**Plans**: TBD

Plans:
- [ ] 06-01: Fingerprinting protections (canvas/audio/WebGL/font/hwConcurrency/timezone) — **DEFERRED to a dedicated multi-week effort.** Chromium has no built-in farbling toggle; doing this right means porting a Brave-style randomization-seed-per-eTLD+1 scheme and modifying canvas / WebGL / Web Audio / Font Access / `navigator.hardwareConcurrency` / Date / Intl surfaces. Out of scope for "make small autonomous decisions". Slated for Phase 6.5.
- [x] 06-02: Storage partitioning per top-level site — **already-default upstream.** `net::features::kThirdPartyStoragePartitioning` is `FEATURE_ENABLED_BY_DEFAULT` (verified `net/base/features.cc:229`). No phlink patch needed; recorded as audited in this roadmap.
- [x] 06-03: Third-party cookies blocked by default in regular profiles. `prefs::kCookieControlsMode` registered with `CookieControlsMode::kBlockThirdParty` (vs upstream `kIncognitoOnly`). `autoninja chrome` Build Succeeded. (`patches/0101-*.patch`)
- [x] 06-04: Referrer policy hardening — **already-default upstream.** `blink::features::kReducedReferrerGranularity` is `FEATURE_ENABLED_BY_DEFAULT` (`third_party/blink/common/features.cc:2168`); cross-origin requests default to `strict-origin-when-cross-origin` (origin-only, no path/query). No phlink patch needed; recorded as audited.
- [ ] 06-05: URL query-parameter stripping (configurable list) — **DEFERRED to a dedicated effort.** Requires a navigation throttle + a maintained tracking-param list + a settings UI surface. Slated for Phase 6.6 alongside 06-01.
- [x] 06-06: Network-state isolation per top-level site. Flipped `kSplitCacheByNetworkIsolationKey`, `kSplitCodeCacheByNetworkIsolationKey`, `kPartitionConnectionsByNetworkIsolationKey` from `DISABLED_BY_DEFAULT` to `ENABLED_BY_DEFAULT` in `net/base/features.cc`. Accepts the cache-hit-rate trade-off per PRD privacy-first stance. `autoninja chrome` Build Succeeded. (`patches/0102-*.patch`)
- [x] 06-07: Password manager OS-keychain integration — **already-default upstream** on all three platforms (`components/os_crypt/common/keychain_password_mac.{h,mm}` for macOS; equivalent libsecret/DPAPI bindings exist for Linux/Windows). Cloud sync is off by virtue of Phase 4-01 having disabled the sync server. No phlink patch needed; recorded as audited.

**Phase 6 partial close**: 06-02, 06-03, 06-04, 06-06, 06-07 done. 06-01 and 06-05 split out into Phase 6.5 / 6.6 as dedicated efforts.

### Phase 7: Performance Subsystem
**Goal**: Configurable performance behaviors plus a built-in performance dashboard and a reproducible 60-tab benchmark harness.
**Depends on**: Phase 1
**Requirements**: PERF-01, PERF-02, PERF-03, PERF-04, PERF-05
**Success Criteria** (what must be TRUE):
  1. Tab-grouping-aware discarder is configurable and tuned for the 60-tab benchmark.
  2. Background tab throttling is configurable with documented suggested defaults.
  3. Process-model knobs are exposed with safe defaults.
  4. Performance dashboard shows per-tab RAM / CPU / energy.
  5. A reproducible 60-tab benchmark harness lives in the repo and runs from a single command.
**Plans**: TBD

Plans:
- [ ] 07-01: Tab-grouping-aware discarder (component + settings UI)
- [ ] 07-02: Configurable background-tab throttling
- [ ] 07-03: Process-model knobs surface (with safe defaults)
- [ ] 07-04: Per-tab performance dashboard UI
- [x] 07-05: 60-tab reproducible benchmark harness — `tests/benchmark_60tab/` (pytest + DevTools Protocol + psutil). Single command: `PHLINK_BINARY=/path/to/Chromium python -m pytest tests/benchmark_60tab/`. Boots fresh profile via CDP, opens 60 URLs (`urls.txt`), warms up, samples process tree (RAM total + per-process, CPU%, process count) at 1 Hz for 60s, writes JSON report (`BENCHMARK_REPORT_PATH`). Skips cleanly when `PHLINK_BINARY` unset (CI-safe). Phase 12 will add the budget-diff gate. Decision: pytest+CDP rather than Playwright — Playwright can't see browser-process traffic and adds a Node toolchain just to drive tabs; the DevTools HTTP `/json/new` endpoint is sufficient and the same psutil tree-walk is reusable for the future per-tab dashboard.

**Phase 7 deferral**: 07-01 / 07-02 / 07-03 / 07-04 are dedicated multi-week efforts requiring chromium-side discarder + throttling + process-model component work and a settings WebUI surface. They are pulled forward to **Phase 7.5: Perf Subsystem (full)** after Phase 8 ships the settings WebUI infrastructure (which 07-01/07-04 both depend on). 07-05 stands alone and is shipped now so we have a baseline.

### Phase 8: Appearance Subsystem
**Goal**: Theme engine plus the two default WCAG-AA themes (Light, Dark), with a system-follow switcher and a CI gate that fails on contrast regressions.
**Depends on**: Phase 3
**Requirements**: APPR-01, APPR-02, APPR-03, APPR-04, APPR-05
**Success Criteria** (what must be TRUE):
  1. Theme engine loads built-in themes (community-theme support stubbed for v1.1).
  2. Default Light theme uses Pastel Sky Blue / Translucent Off-white / White.
  3. Default Dark theme uses Pastel Yellow / Translucent Light Grey / Black / White.
  4. Theme switcher in settings supports Light / Dark / Follow System.
  5. Automated CI check fails the build if either default theme regresses below WCAG AA contrast.
**Plans**: TBD

**Plans:** 5 plans
Plans:
- [x] 08-01a: Scoping + upstream integration audit — see [docs/dev/phase-08-scoping.md](../docs/dev/phase-08-scoping.md). Shipped autonomously 2026-04-29.
- [x] 08-CONTEXT: Discuss-phase auto-mode CONTEXT + DISCUSSION-LOG captured 2026-04-29 (`.planning/phases/08-appearance-subsystem/`). 12 decisions locked; token hex values explicitly deferred to stitch.
- [x] 08-RESEARCH + 08-PATTERNS: targeted upstream-Chromium research (mixer registration, ID convention, observer pattern, WebUI surface, WCAG APIs) + per-file pattern map. Authored 2026-04-29.
- [x] 08-01b: Color mixer foundation — `kColorPhlink*` IDs + `phlink_color_mixer.{cc,h}` + `phlink_palette.{cc,h}` skeleton, registered in `chrome_color_mixers.cc` after Native / before custom_theme. (`patches/0110-*.patch`)
- [x] 08-02: Default Light theme — `kPhlinkLight[]` populated with locked D-08 hex; per-token EXPECT_EQ test. (`patches/0111-*.patch`)
- [x] 08-03: Default Dark theme — `kPhlinkDark[]` populated with locked D-08 hex incl. `kOnAccent=#000000` never-white invariant. (`patches/0112-*.patch`)
- [x] 08-04: `prefs::kPhlinkAppearanceMode` (default Follow System) + `PhlinkAppearanceObserver` + chrome://settings/appearance radio row. (`patches/0113-*.patch`) **Plus fixup `patches/0115-*.patch`**: settingsPrivate allowlist entry (`prefs_util.cc`) + BUILD.gn dep + `<div class="cr-row continuation">` wrapper around the radio group — the original landing was missing both the WebUI pref allowlist (radio writes were dead) and the canonical row wrapper (radios were unstyled). UAT confirmed working post-fixup.
- [x] 08-05: WCAG-AA gate — pair tables + `phlink_color_contrast_unittests.cc` (15/15 green) + `scripts/contrast-audit.py` lint mirror + CI step. (`patches/0114-*.patch`)

**Phase 8 — appearance subsystem complete.** Patches `0110..0115`. UAT 2026-04-29 surfaced two follow-on items split out as Phases 8.5 + 8.6 below.

### Phase 8.5: Branding Sweep v2 (UAT-driven)
**Goal**: Eliminate the rendered-UI "Chromium" / "Chrome" / "Google Chrome" strings that survived Phase 4.7's strings-only audit. UAT of `chrome://settings/appearance` (2026-04-29) showed the settings header, About box, version page, window title, and several menu items still read "Chromium". 4.7 allowlisted ~188 matches into 8 categories on the assumption they were non-user-visible; UAT proves several are user-visible.
**Depends on**: Phase 8
**Requirements**: BRND-01, BRND-02 (PRD §3.6)
**Success Criteria**:
  1. `tests/branding-audit/allowlist.txt` re-classified — entries reachable via the rendered UI moved to a "must-patch" bucket.
  2. Settings header, About box, version page (`chrome://version`), window/menu titles, and `chrome://flags` help text all read "phlink".
  3. macOS bundle `Info.plist` `CFBundleName` + `CFBundleDisplayName` = `phlink` (verified via `defaults read out/Default/phlink.app/Contents/Info.plist`).
  4. New screenshot-diff regression test (or runtime grep over rendered DOM) catches reintroduction.
  5. Branding-audit harness still green; allowlist shrinks measurably.
**Plans**: Executed inline (`08.5-CONTEXT.md` + `08.5-DISCUSSION-LOG.md` under `.planning/phases/08.5-branding-sweep-v2/`). Single patch slot 0116.

### Phase 8.6: `phlink://` Scheme Alias
**Goal**: Register `phlink://` as a primary WebUI URL scheme; keep `chrome://` working as a backwards-compatible alias so dev muscle memory and bookmarks survive. Promotes backlog placeholder 999.4 (deferred from Phase 4.7) to a full phase.
**Depends on**: Phase 8.5 (avoid stacking branding edits with scheme edits)
**Requirements**: BRND-02 (PRD §3.6)
**Reference patterns**: Brave's `brave://` (`chromium_src/content/public/common/url_constants.cc` + `BraveContentBrowserClient::AdditionalSchemesForBrowserContext`); Vivaldi's `vivaldi://`.
**Success Criteria**:
  1. `phlink://settings`, `phlink://flags`, `phlink://version`, `phlink://about`, `phlink://newtab`, `phlink://components` all load.
  2. `chrome://*` URLs resolve to the same WebUI controllers (alias preserved).
  3. Omnibox displays the canonical `phlink://` form when the user types either prefix.
  4. Internal cross-references (in-product help, about-box links, doc URLs) emit `phlink://` form.
  5. Unit tests cover the alias mapping (no double-registration; both schemes route to same `WebUIController`).
**Touchpoints**:
  - `content::kChromeUIScheme` register-additional path
  - `ChromeWebUIControllerFactory::GetWebUIType` / `CreateWebUIControllerForURL`
  - `OmniboxAutocompleteProvider` rewrite rules
  - `chrome/common/url_constants.{cc,h}` phlink mirrors
  - History DB serialization (avoid duplicating entries under both schemes)
**Plans**: TBD (authored by `/gsd-plan-phase 8.6`).

**Wave structure** (file-overlap-aware):
- Wave 1: 08-01b
- Wave 2: 08-02 (mutates `phlink_palette.cc`)
- Wave 3: 08-03 (mutates same file)
- Wave 4: 08-04 + 08-05 (parallel — disjoint files: 08-04 touches themes/+settings/, 08-05 touches color/+scripts/+.github/)

**Status note (2026-04-29, updated)**: stitch MCP enabled mid-session. Both Light and Dark themes generated via `projects/12962487919675094023`, ideology-validated against rendered desktop screenshots, and final tokens locked at `.planning/sketches/phase-08/stitch-output.md`. CONTEXT D-08 promoted from placeholder to LOCKED. **Plans 08-01b through 08-05 authored 2026-04-29 via `/gsd-plan-phase 8 --auto`.** Downstream work (5-06b adblock settings UI, 7-01/04 perf settings UI, 03-06 first-run discovery) unblocks once 08-04 ships the settings WebUI pattern.

### Phase 9: Profile Export/Import
**Goal**: Users can export a complete encrypted profile bundle locally and import it on any phlink install on any supported platform.
**Depends on**: Phase 6
**Requirements**: PROF-01, PROF-02, PROF-03
**Success Criteria** (what must be TRUE):
  1. A user can export a full profile (history, bookmarks, passwords, extensions, settings) as a single encrypted bundle, secured by a passphrase-derived key.
  2. A user can import a bundle on any phlink install on macOS, Linux, or Windows.
  3. No cloud sync endpoint exists; export/import is the only portability mechanism.
**Plans**: TBD

Plans:
- [x] 09-01: Encrypted bundle format spec (passphrase-KDF + AEAD) *(patch 0118)*
- [~] 09-02: Export flow — codec landed (patch 0119); service + Settings WebUI Export card deferred to **09-02b**
- [~] 09-03: Import flow — codec landed (patch 0120); ProfileManager hookup + Import card + round-trip integration test deferred to **09-03b**

### Phase 10: Update Mechanism & Installers
**Goal**: Signed native installers per platform with TUF-style auto-updates and signature verification before any update is applied.
**Depends on**: Phase 2
**Requirements**: UPD-01, UPD-02, UPD-03
**Success Criteria** (what must be TRUE):
  1. Signed `.dmg` (macOS), `.deb` / `.rpm` / AppImage (Linux), and signed `.msi` / `.exe` (Windows) installers are produced by CI.
  2. TUF-style update channel ships signed metadata + payloads over HTTPS, with no background account.
  3. The updater verifies signatures before applying any update; failed signatures abort the update with a logged reason.
**Plans**: TBD

Plans:
- [x] 10-01: TUF metadata roles + canonical JSON + signed root/timestamp/snapshot/targets client landed across patches 0124-0136.
- [x] 10-02: Updater scheduler, service, metadata fetcher, payload fetcher, staging, update-check pipeline, and production service wiring landed across patches 0126-0136.
- [x] 10-03: macOS helper/apply flow, DMG/update zip packaging, Developer ID/notarization CI gates, and stable bundle trust-root path shipped.
- [x] 10-04: Linux helper/apply flow, AppImage/deb/rpm packaging, bundled `release.gpg`, detached-signature release flow, and non-colliding updater root path shipped.
- [x] 10-05: Windows helper/apply flow, MSI/update exe packaging, Authenticode signing gates, and release provenance shipped.
- [x] 10-06: Settings Help updater controls shipped.
- [x] 10-07: Cross-platform installer scripts shipped.
- [x] 10-08: Release key ceremony, signing scripts, package/release workflows, and provenance gates shipped.

**Phase 10 complete:** `patches/0124..0136` plus phlink-side installer/release tooling. Verification: `autoninja -j 8 -C out/Default phlink_updater_unittests chrome`, `phlink_updater_unittests` 38/38, mac DMG smoke, release-sign dry run, workflow YAML/heredoc checks, and GSD code review all passed.

### Phase 11: Documentation & License Audit
**Goal**: Complete user and developer docs, a comprehensive third-party license file, and a CI license-compatibility check that fails on incompatible additions.
**Depends on**: Phase 1
**Requirements**: BLD-04, BLD-05, DOCS-01, DOCS-02, DOCS-03, DOCS-04
**Success Criteria** (what must be TRUE):
  1. `docs/user/` covers install, features, settings, troubleshooting, and privacy explanations.
  2. `docs/dev/` covers architecture, build, contribution guide, extension/component model, and release process.
  3. `docs/dev/third-party-licenses.md` lists every shipped dependency, filter list, and asset with its license.
  4. `docs/dev/mcp-workflow.md` documents the authorized MCPs (`playwright`, `stitch-mcp`, `git`, others).
  5. A CI job fails the build when a non-compatible license is added.
**Plans**: TBD

Plans:
- [x] 11-01: `docs/user/` content authoring (install / features / settings / troubleshooting / privacy) — shipped (commit `dcecc08`).
- [x] 11-02: `docs/dev/` content authoring — `release-process.md`, `extension-model.md`, `docs/dev/README.md`, lychee CI step — shipped (commit `dcecc08`).
- [x] 11-03: `docs/dev/third-party-licenses.md` content (Rust crates, filter lists, assets) — shipped 2026-04-29 (commit `1f6a4bf`). Generator/CI diff portion lives in 11-04.
- [x] 11-04: CI license-compatibility check — [scripts/license-audit.py](../scripts/license-audit.py) wired into `.github/workflows/lint.yml`. Shipped 2026-04-29 (commit `62f93fa`).
- [x] 11-05: `docs/dev/mcp-workflow.md` — shipped 2026-04-29 (commit `1f6a4bf`).

### Phase 12: Alpha Hardening & v1.0 Release
**Goal**: PRD §9 success metrics are measured, met, and published, and a signed v1.0 alpha is tagged for all three platforms.
**Depends on**: Phase 5, Phase 6, Phase 7, Phase 8, Phase 9, Phase 10, Phase 11
**Requirements**: ADBL-08, PRIV-07, PERF-06, PERF-07, PERF-08, QUAL-01, QUAL-02, QUAL-03
**Success Criteria** (what must be TRUE):
  1. Adblock block-rate is within ±5% of Brave Shield on a shared test corpus at default settings.
  2. EFF Cover Your Tracks and Brave fingerprint suites pass at parity or better with Brave defaults.
  3. Steady-state RAM at 60 tabs is ≥30% lower than Chrome on equivalent hardware.
  4. Steady-state CPU at 60 tabs is ≥20% lower than Chrome on equivalent hardware.
  5. Cold start time is ≤ Chrome on equivalent hardware.
  6. Crash rate over a representative usage corpus is ≤ upstream Chromium stable.
  7. v1.0 alpha is tagged with signed installers for macOS, Linux, and Windows.
  8. Release notes document the validated metrics against PRD §9.
**Plans**: TBD

Plans:
- [ ] 12-01: Adblock corpus parity test vs Brave Shield
- [ ] 12-02: EFF Cover Your Tracks + Brave fingerprint suite runs
- [ ] 12-03: 60-tab perf measurement vs Chrome (RAM / CPU / cold start)
- [ ] 12-04: Crash-rate measurement vs upstream Chromium stable
- [ ] 12-05: v1.0 alpha tag, signed artifacts, release notes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Chromium Build Foundation | 0/4 | Not started | - |
| 2. Cross-Platform CI Bootstrap | 0/3 | Not started | - |
| 3. Identity & Branding Strip | 0/6 | Not started | - |
| 4. Telemetry-Free Defaults | 3/3 | Complete (HEAD a1eb452) | 2026-04-28 |
| 5. Adblock Subsystem | 0/8 | Not started | - |
| 6. Privacy Hardening | 0/7 | Not started | - |
| 7. Performance Subsystem | 0/5 | Not started | - |
| 8. Appearance Subsystem | 5/5 | Complete (HEAD 78e5582) | 2026-04-29 |
| 8.5. Branding Sweep v2 | 1/1 | **Complete** | `0ef1fed20307` (chromium-src) → patch `0116` |
| 8.6. `phlink://` Scheme Alias | 1/1 | Done (patch 0117) | 2026-04-29 |
| 9. Profile Export/Import | 1/3 + 2 partial | Codec checkpoint landed (0118/0119/0120); service+UI deferred to 09-02b/09-03b | - |
| 10. Update Mechanism & Installers | 0/5 | Not started | - |
| 11. Documentation & License Audit | 0/5 | Not started | - |
| 12. Alpha Hardening & v1.0 Release | 0/5 | Not started | - |
