# Requirements: phlink

**Defined:** 2026-04-28
**Core Value:** A measurably lighter, privacy-by-default Chromium browser whose every default leans toward performance and privacy, without locking users out of customization.

## v1 Requirements

Requirements for initial release (v1.0 alpha). Each maps to roadmap phases.

### Build & Supply Chain (BLD)

- [ ] **BLD-01**: Chromium stable can be fetched, built, and run as `phlink` on macOS, Linux, and Windows from a documented setup procedure
- [ ] **BLD-02**: A minimal patch set is layered onto upstream Chromium and survives a stable rebase
- [ ] **BLD-03**: Cross-platform CI builds phlink on macOS, Linux, and Windows on every push to main
- [ ] **BLD-04**: Every shipped third-party dependency, filter list, and asset is OSS with a compatible license, recorded in `docs/dev/third-party-licenses.md`
- [ ] **BLD-05**: License compatibility is checked automatically in CI; non-compliant additions fail the build
- [ ] **BLD-06**: A `.refs/` upstream documentation cache is scaffolded with a `MANIFEST.json` schema, gitignored, and used during development

### Branding & Identity (BRND)

- [ ] **BRND-01**: All upstream "Chromium" / "Chrome" product strings visible to users are replaced with "phlink"
- [ ] **BRND-02**: phlink ships its own application icon, splash, and About page
- [ ] **BRND-03**: All Google sign-in / sync / Google-services targets are removed or disabled at the build level
- [ ] **BRND-04**: Default search engine is DuckDuckGo; Brave Search, Startpage, Google, and Bing are preloaded as switchable options

### Telemetry & Network Defaults (TELM)

- [ ] **TELM-01**: phlink performs zero outbound telemetry requests on a clean profile launch (verified by network capture)
- [ ] **TELM-02**: Crash reporting is disabled by default with no opt-in path in v1
- [ ] **TELM-03**: Default DoH resolver is Cloudflare 1.1.1.1 (no-log tier); Quad9 and NextDNS are preconfigured; user can pick or enter custom
- [ ] **TELM-04**: DNS-over-HTTPS / DNS-over-TLS is enabled by default and user-overridable

### Ad & Tracker Blocking (ADBL)

- [ ] **ADBL-01**: `adblock-rust` is integrated as the network-layer blocking engine
- [ ] **ADBL-02**: Cosmetic (element-hiding) filtering is supported
- [ ] **ADBL-03**: Default filter lists ship: EasyList, EasyPrivacy, uBO defaults, Peter Lowe's list, and Brave's MPL-compatible lists
- [ ] **ADBL-04**: Per-site Shield UI exposes Aggressive / Standard / Off modes; default is Standard
- [ ] **ADBL-05**: Filter list manager supports subscribing to, updating, and adding custom lists
- [ ] **ADBL-06**: An element picker lets the user create custom cosmetic rules
- [ ] **ADBL-07**: Allowlist management is available globally and per-site
- [ ] **ADBL-08**: Block rate is within ±5% of Brave Shield on a shared test corpus at default settings

### Privacy Hardening (PRIV)

- [ ] **PRIV-01**: Fingerprinting protections are active by default for canvas, audio, WebGL, font, hardware concurrency, and timezone
- [ ] **PRIV-02**: Storage is partitioned per top-level site (cookies, cache, storage APIs)
- [ ] **PRIV-03**: Third-party cookies are isolated by default
- [ ] **PRIV-04**: Referrer policy is hardened (cross-origin truncation) by default
- [ ] **PRIV-05**: A configurable URL query-parameter stripper is applied to navigations
- [ ] **PRIV-06**: Network state (HTTP cache, connection pool, DNS cache) is isolated per top-level site
- [ ] **PRIV-07**: Default settings pass the EFF Cover Your Tracks suite and the Brave fingerprint suite at parity or better with Brave defaults
- [ ] **PRIV-08**: Site-isolation remains ON at upstream defaults

### Performance (PERF)

- [ ] **PERF-01**: Tab discarding strategy is configurable, tab-grouping-aware, and tuned for the 60-tab benchmark
- [ ] **PERF-02**: Background tab throttling is configurable with documented suggested defaults
- [ ] **PERF-03**: Process model knobs are exposed with safe defaults
- [ ] **PERF-04**: A built-in performance dashboard shows per-tab RAM, CPU, and energy usage
- [ ] **PERF-05**: A reproducible 60-tab benchmark harness lives in the repo and runs on demand
- [ ] **PERF-06**: Steady-state RAM at 60 tabs is ≥30% lower than Chrome on equivalent hardware
- [ ] **PERF-07**: Steady-state CPU at 60 tabs is ≥20% lower than Chrome on equivalent hardware
- [ ] **PERF-08**: Cold start time is ≤ Chrome on equivalent hardware

### Appearance & Themes (APPR)

- [ ] **APPR-01**: A theme engine supports built-in and (post-v1) community themes
- [ ] **APPR-02**: A default Light theme ships using the palette: Pastel Sky Blue, Translucent Off-white, White
- [ ] **APPR-03**: A default Dark theme ships using the palette: Pastel Yellow, Translucent Light Grey, Black, White
- [ ] **APPR-04**: A theme switcher with a system-follow option is available in settings
- [ ] **APPR-05**: Both default themes are WCAG AA compliant, verified by an automated CI check

### Core Browser Parity (CORE)

- [ ] **CORE-01**: Navigation, tabs, windows, bookmarks, history, and downloads work at upstream-stable parity
- [ ] **CORE-02**: DevTools work at upstream-stable parity
- [ ] **CORE-03**: PWAs (install, run, update) work at upstream-stable parity
- [ ] **CORE-04**: Media playback works at upstream-stable parity
- [ ] **CORE-05**: Autofill works at upstream-stable parity
- [ ] **CORE-06**: The built-in password manager works at upstream-stable parity, local-only, with OS-keychain-backed key storage (Keychain / libsecret / DPAPI)
- [ ] **CORE-07**: Profiles (multiple, switching) work at upstream-stable parity
- [ ] **CORE-08**: Standard Chromium extensions (MV3 + MV2 while upstream-supported) install via Chrome Web Store URLs and run, with no Google services bundled
- [ ] **CORE-09**: A curated, signed phlink-vetted extension list is shown for first-run discovery

### Profile Portability (PROF)

- [ ] **PROF-01**: A user can export their full profile as a local, encrypted bundle (passphrase-derived key)
- [ ] **PROF-02**: A user can import a profile bundle on any phlink install on any supported platform
- [ ] **PROF-03**: No cloud sync endpoint exists in v1; export/import is the only portability mechanism

### Update Mechanism (UPD)

- [x] **UPD-01**: phlink ships native installers per platform: signed `.dmg` for macOS, `.deb` / `.rpm` / AppImage for Linux, signed `.msi` / `.exe` for Windows
- [x] **UPD-02**: Auto-update uses TUF-style signed updates over HTTPS, with no background account
- [x] **UPD-03**: Signature verification runs before any update is applied; failed signatures abort the update

### Documentation (DOCS)

- [ ] **DOCS-01**: `docs/user/` covers install, features, settings, troubleshooting, and privacy explanations
- [ ] **DOCS-02**: `docs/dev/` covers architecture, build, contribution guide, extension/component model, and release process
- [ ] **DOCS-03**: `docs/dev/third-party-licenses.md` lists every shipped dependency, filter list, and asset with its license
- [ ] **DOCS-04**: A documented MCP development workflow lists authorized MCPs (`playwright`, `stitch-mcp`, `git`, others) and their use

### Quality & Release (QUAL)

- [ ] **QUAL-01**: Crash rate is no greater than upstream Chromium stable across a representative usage corpus
- [ ] **QUAL-02**: A v1.0 alpha is tagged and released with signed installers for all three platforms
- [ ] **QUAL-03**: Release notes document validated metrics against §9 of the PRD

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Sync (SYNC)

- **SYNC-01**: Self-hostable encrypted sync server (stretch goal for v2)
- **SYNC-02**: Multi-device profile sync via the self-hosted server

### Themes (THEM2)

- **THEM2-01**: Community themes can be packaged, distributed, and installed (v1.1+)
- **THEM2-02**: Theme marketplace UI for browsing community themes

### Builds (BLD2)

- **BLD2-01**: Reproducible builds across all three platforms (stretch goal)

### Telemetry (TELM2)

- **TELM2-01**: Optional, local-first, explicitly opt-in crash reporting (post-v1 only)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mobile platforms (iOS, Android) | Desktop-first; mobile is a separate product |
| Proprietary cloud sync service | Undermines privacy-by-default (G3) |
| Built-in cryptocurrency wallet / rewards | Bloat; counter to performance and privacy goals |
| Built-in VPN | Bloat; outside scope of a browser |
| Custom rendering engine | phlink stays on Chromium |
| Forked extension store | Reusing Chrome Web Store URLs preserves the ecosystem |
| Opt-in telemetry in v1 | No telemetry path in v1; deferred to v2 with strict gates |
| Background account for updates | TUF + signatures suffice; account adds identity surface |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| BLD-01 | Phase 1 | Pending |
| BLD-02 | Phase 1 | Pending |
| BLD-06 | Phase 1 | Pending |
| BLD-03 | Phase 2 | Pending |
| BLD-04 | Phase 11 | Pending |
| BLD-05 | Phase 11 | Pending |
| BRND-01 | Phase 3 | Pending |
| BRND-02 | Phase 3 | Pending |
| BRND-03 | Phase 3 | Pending |
| BRND-04 | Phase 3 | Pending |
| TELM-01 | Phase 4 | Pending |
| TELM-02 | Phase 4 | Pending |
| TELM-03 | Phase 4 | Pending |
| TELM-04 | Phase 4 | Pending |
| ADBL-01 | Phase 5 | Pending |
| ADBL-02 | Phase 5 | Pending |
| ADBL-03 | Phase 5 | Pending |
| ADBL-04 | Phase 5 | Pending |
| ADBL-05 | Phase 5 | Pending |
| ADBL-06 | Phase 5 | Pending |
| ADBL-07 | Phase 5 | Pending |
| ADBL-08 | Phase 12 | Pending |
| PRIV-01 | Phase 6 | Pending |
| PRIV-02 | Phase 6 | Pending |
| PRIV-03 | Phase 6 | Pending |
| PRIV-04 | Phase 6 | Pending |
| PRIV-05 | Phase 6 | Pending |
| PRIV-06 | Phase 6 | Pending |
| PRIV-07 | Phase 12 | Pending |
| PRIV-08 | Phase 6 | Pending |
| PERF-01 | Phase 7 | Pending |
| PERF-02 | Phase 7 | Pending |
| PERF-03 | Phase 7 | Pending |
| PERF-04 | Phase 7 | Pending |
| PERF-05 | Phase 7 | Pending |
| PERF-06 | Phase 12 | Pending |
| PERF-07 | Phase 12 | Pending |
| PERF-08 | Phase 12 | Pending |
| APPR-01 | Phase 8 | Pending |
| APPR-02 | Phase 8 | Pending |
| APPR-03 | Phase 8 | Pending |
| APPR-04 | Phase 8 | Pending |
| APPR-05 | Phase 8 | Pending |
| CORE-01 | Phase 1 | Pending |
| CORE-02 | Phase 1 | Pending |
| CORE-03 | Phase 1 | Pending |
| CORE-04 | Phase 1 | Pending |
| CORE-05 | Phase 1 | Pending |
| CORE-06 | Phase 6 | Pending |
| CORE-07 | Phase 1 | Pending |
| CORE-08 | Phase 3 | Pending |
| CORE-09 | Phase 3 | Pending |
| PROF-01 | Phase 9 | Pending |
| PROF-02 | Phase 9 | Pending |
| PROF-03 | Phase 9 | Pending |
| UPD-01 | Phase 10 | Done |
| UPD-02 | Phase 10 | Done |
| UPD-03 | Phase 10 | Done |
| DOCS-01 | Phase 11 | Pending |
| DOCS-02 | Phase 11 | Pending |
| DOCS-03 | Phase 11 | Pending |
| DOCS-04 | Phase 11 | Pending |
| QUAL-01 | Phase 12 | Pending |
| QUAL-02 | Phase 12 | Pending |
| QUAL-03 | Phase 12 | Pending |

**Coverage:**
- v1 requirements: 60 total
- Mapped to phases: 60
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-28*
*Last updated: 2026-04-28 after initial definition*
