# phlink — Product Requirements Document (PRD)

| Field        | Value                                       |
| ------------ | ------------------------------------------- |
| Product      | phlink                                      |
| Type         | Open-source, cross-platform Chromium browser |
| Platforms    | macOS, Linux, Windows                       |
| License      | Open source (exclusively OSS dependencies)  |
| Status       | Draft                                       |
| Owner        | devparanjay                                 |
| Last Updated | 2026-04-28                                  |

---

## 1. Overview

**phlink** is an open-source, cross-platform web browser built on top of Chromium. Its design philosophy centers on **performance, privacy, and aesthetics** without sacrificing the features users expect from a modern browser. phlink targets users who feel underserved by mainstream browsers (Chrome, Firefox, Edge) on resource consumption and privacy, and who find existing privacy-focused browsers (Brave, LibreWolf) either too opinionated or visually utilitarian.

## 2. Vision

A browser that:

- Runs measurably lighter than Chrome and Firefox under heavy multi-tab workloads.
- Blocks ads and trackers at parity with the industry-leading open-source baseline (Brave Shield).
- Is private by architectural default, not by opt-in checkbox.
- Looks and feels like a modern, aesthetic application — not a developer tool.
- Remains fully customizable: every default is a suggestion, not a constraint.

## 3. Goals

### 3.1 Major Goals (P0)

#### G1. Extreme Performance

- **Objective:** Be significantly lighter than Chrome and Firefox on system resources (RAM, CPU, energy) while preserving the major features of modern browsers (tab management, extensions, sync, devtools, media, PWAs, etc.).
- **Benchmark scenario:** 60 individual tabs open simultaneously across a representative mix of content (news, video, social, SaaS apps, idle tabs).
- **Customization:** Users can tune performance behaviors (tab discarding, background throttling, prefetching, hardware acceleration, process model knobs) with **suggested defaults** that lean toward lightness.
- **Success criteria (target, to be validated):**
  - ≥ 30% lower steady-state RAM than Chrome on the 60-tab benchmark.
  - ≥ 20% lower steady-state CPU than Chrome on the 60-tab benchmark.
  - No regression in core feature parity vs. upstream Chromium stable.

#### G2. Ad Blocking

- **Objective:** Comprehensive ad and tracker blocking comparable to **Brave Shield**.
- **Approach:** Built-in (not bolted on as an extension), leveraging open-source filter lists (EasyList, EasyPrivacy, uBlock Origin defaults, Brave's lists where licensing permits) and network-layer + cosmetic filtering.
- **Customization:** Per-site toggles, aggressive/standard/off modes, user-supplied filter lists, allowlist management. Suggested default: **Standard** (parity with Brave Shield default).
- **Success criteria:**
  - Blocking effectiveness within ±5% of Brave Shield on a shared test corpus of top sites.
  - No noticeable site breakage at the default level beyond what Brave Shield itself causes.

#### G3. Privacy by Design

- **Objective:** Privacy is a property of the system architecture, not a settings page. Minimize the user's digital footprint during normal browsing. Excludes data the user *willingly* submits to sites.
- **Scope includes:** fingerprinting resistance, third-party cookie isolation, referrer minimization, DNS privacy (DoH/DoT), telemetry-free defaults, partitioned storage, network state isolation, query-parameter stripping.
- **Customization:** Granular per-site and global controls with **suggested defaults** that prioritize privacy while remaining usable.
- **Success criteria:**
  - Pass Brave's and EFF's fingerprinting/tracker test suites at parity or better with Brave default settings.
  - Zero outbound telemetry from phlink itself by default.

### 3.2 Minor Goals (P1)

#### M1. Appearance

- Modern, aesthetic UI inspired by **beautiful isometric games**.
- Two default themes, both **WCAG AA compliant**:
  - **Light:** Pastel Sky Blue, Translucent Off-white, White.
  - **Dark:** Pastel Yellow, Translucent Light Grey, Black, White.
- Theming system that allows community themes later.

#### M2. Documentation

- **User documentation:** install, features, settings, troubleshooting, privacy explanations.
- **Developer documentation:** architecture, build, contribution guide, extension/component model, release process.
- Both must live in-repo under `docs/user/` and `docs/dev/`.

#### M3. Extensibility

- Goals beyond the above may be added in future revisions of this PRD.

## 4. Non-Goals (for v1)

- Mobile platforms (iOS, Android).
- A proprietary sync/cloud service.
- A built-in cryptocurrency wallet, rewards system, or VPN.
- A custom rendering engine — phlink stays on Chromium.
- Replacing Chromium's extension ecosystem; phlink will support standard Chromium extensions.

## 5. Target Users

- **Power users** running many tabs and feeling resource pressure on Chrome/Firefox.
- **Privacy-conscious users** who want Brave-tier protections without Brave's bundled features.
- **Developers and tinkerers** who want a hackable, well-documented Chromium-based browser.
- **Aesthetics-driven users** who care about how their everyday tools look.

## 6. Functional Requirements

### 6.1 Core Browser

- Full Chromium feature parity for: navigation, tabs, windows, bookmarks, history, downloads, devtools, PWAs, media playback, autofill, password manager, profiles.
- Support for standard Chromium extensions (MV3 + as long as MV2 is upstream-supported).

### 6.2 Performance Subsystem

- Configurable tab discarding and freezing strategy.
- Configurable background tab throttling.
- Process model tuning surface (with safe defaults).
- Built-in performance dashboard (per-tab RAM/CPU/energy).
- Benchmark harness in repo for the 60-tab scenario.

### 6.3 Ad/Tracker Blocking Subsystem

- Native network-layer blocking engine (e.g., Rust adblock-rs or equivalent OSS engine).
- Cosmetic filtering.
- Filter list manager (subscribe, update, custom).
- Per-site shield UI: aggressive / standard / off.
- Element-picker for user custom rules.

### 6.4 Privacy Subsystem

- DoH/DoT with user-selectable resolver and a vetted default.
- Fingerprinting protections (canvas, audio, WebGL, font, hardware concurrency, timezone).
- Storage partitioning per top-level site.
- Referrer policy hardening.
- URL query-parameter stripping (configurable list).
- No outbound telemetry by default; any optional telemetry must be opt-in and documented.

### 6.5 Appearance Subsystem

- Two built-in themes (Light, Dark) per palettes in §3.2 M1.
- WCAG AA contrast verified via automated checks in CI.
- Theme switcher with system-follow option.

### 6.6 Documentation

- `docs/user/` — end-user docs.
- `docs/dev/` — developer docs (this PRD lives here).
- Build/release docs, architecture docs, contribution guide.

## 7. Non-Functional Requirements

- **Cross-platform:** macOS, Linux, Windows. Build and CI on all three.
- **Open source only:** no proprietary dependencies in shipped binaries; license compatibility audited.
- **Reproducible builds** as a stretch goal.
- **Stability:** no greater crash rate than upstream Chromium stable.
- **Update mechanism:** auto-update with verifiable signatures.

## 8. Development Approach

1. **Open-source-only dependencies.** Every shipped library, asset, and tool must be OSS with a compatible license. Licenses tracked in repo.
2. **Chromium extensions as feature vehicles.** Where feasible, features are delivered as bundled Chromium extensions/components rather than core patches, to reduce upstream-rebase pain.
3. **MCP-assisted development workflow.** Authorized MCP servers used during development:
   - `playwright` — automated browser testing.
   - `stitch-mcp` — design system, UI/UX, logo, asset generation.
   - `git` MCP — version control operations.
   - Additional MCPs may be added; they must be documented in `docs/dev/`.
4. **Structured upstream documentation cache.** Before adopting any technology, language, or OSS library, phlink's workflow searches and **locally stores reference documentation** in a structured, queryable cache.
   - Purpose: offline reference, deterministic context for AI-assisted development.
   - **Not tracked by git** (added to `.gitignore`); these docs describe *dependencies*, not phlink itself.
   - **Location:** `.refs/` at the repo root, organized as `.refs/<ecosystem>/<project>@<version>/` (e.g., `.refs/rust/adblock-rs@0.8.0/`). Each entry contains the fetched docs plus a `MANIFEST.json` capturing source URL, fetch date, version, and license. Format chosen for grep-ability and trivial AI-agent indexing without a database.
5. **Structured, documented development.** Every adopted OSS project is recorded with: name, version, license, why-chosen, integration notes, and link to its cached docs.

## 9. Success Metrics

| Metric                               | Target                                                              |
| ------------------------------------ | ------------------------------------------------------------------- |
| RAM usage @ 60 tabs vs. Chrome       | ≥ 30% lower (steady state)                                          |
| CPU usage @ 60 tabs vs. Chrome       | ≥ 20% lower (steady state)                                          |
| Cold start time vs. Chrome           | ≤ Chrome on equivalent hardware                                     |
| Ad/tracker block rate vs. Brave      | within ±5% on shared test corpus at default settings                |
| Fingerprinting resistance            | ≥ Brave default on EFF Cover Your Tracks / Brave fingerprint suite  |
| Outbound telemetry (default)         | 0 requests                                                          |
| Theme contrast (both default themes) | WCAG AA compliant (verified in CI)                                  |
| Platforms with green CI              | 3 (macOS, Linux, Windows)                                           |

## 10. Risks & Open Questions

- **Chromium upstream churn:** rebases will be expensive. Mitigation: prefer extensions/components over core patches.
- **Ad-blocking parity vs. site breakage:** matching Brave Shield without inheriting its breakage profile.
- **Performance claims:** require a rigorous, reproducible benchmark harness before any marketing claim.
- **License compatibility** of bundled filter lists and assets (notably anything sourced from Brave). Mitigation: every bundled list is recorded in `docs/dev/third-party-licenses.md` with its license; only lists under permissive or copyleft-compatible terms ship by default.

### 10.1 Resolved Decisions

| Topic            | Decision                                                                                              | Rationale                                                                                                                                                                                                                       |
| ---------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sync (v1)        | **Local-only encrypted profile export/import; no cloud sync in v1. Self-hostable sync as v2 stretch.** | Privacy goal (G3) is undermined by any default cloud sync. Local export keeps the feature useful with zero footprint. Self-hosting is deferred so v1 doesn't ship a server.                                                     |
| Default DoH      | **Cloudflare `1.1.1.1` (no-logging tier) as default; Quad9 and NextDNS preconfigured; user can pick or enter custom.** | Cloudflare and Quad9 publish audited no-log policies and are the same defaults Firefox/Brave use, so we inherit their scrutiny. Always user-overridable to honor the customization principle.                                   |
| Extension store  | **Support standard Chromium extensions; install via Chrome Web Store URL but ship no Google services. Provide a curated, signed phlink-vetted list for first-run discovery.**                              | Forking the store is out of scope and harms users. Reusing CWS URLs preserves the ecosystem; the curated list lets us recommend privacy-respecting extensions without locking users in.                                          |
| Adblock engine   | **`adblock-rust` (Brave's open-source Rust engine).**                                                  | Directly aligns with the Brave Shield parity target (G2), is OSS (MPL-2.0), and is the most battle-tested non-Chromium-internal engine.                                                                                          |
| Filter lists (default) | **EasyList, EasyPrivacy, uBlock Origin filters, Peter Lowe's list, and Brave's default lists where MPL-compatible.**                                                                              | Matches Brave Shield default coverage while staying license-clean.                                                                                                                                                              |
| Telemetry        | **None by default. No opt-in telemetry in v1.**                                                       | Avoids any risk to G3 and removes a class of decisions. Crash reporting, if added later, must be local-first and explicitly opt-in.                                                                                              |
| Update mechanism | **The Update Framework (TUF)-style signed updates over HTTPS, per-platform native installers; no background account.**                                                                            | Security (signature verification) without introducing identity or telemetry.                                                                                                                                                    |
| Build base       | **Track Chromium stable; rebase on each stable bump. Customizations live as bundled extensions/components and a minimal patch set.**                                                              | Minimizes upstream-rebase cost (per §10) and keeps phlink shipping security fixes promptly.                                                                                                                                      |
| Process model    | **Upstream Chromium site-isolation default ON; phlink adds a tab-grouping-aware discarder tuned for the 60-tab benchmark.**                                                                       | Site isolation is a privacy/security primitive we will not weaken. Performance gains come from smarter discarding, not weaker isolation.                                                                                         |
| Themes           | **Two ship by default (Light, Dark per §3.2). Theme engine supports community themes from v1.1+; not v1.**                                                                                        | Keeps v1 scope tight while not closing the door on M1's extensibility.                                                                                                                                                          |
| Docs cache path  | **`.refs/` (gitignored).**                                                                            | Short, unambiguous, doesn't collide with common build/tool dirs.                                                                                                                                                                |
| Password manager | **Use Chromium's built-in password manager with local-only storage; cloud sync disabled. Integration with OS keychains (Keychain / libsecret / DPAPI) for the encryption key.**                    | Reuses upstream code (low maintenance), respects G3, and gives users platform-native security primitives.                                                                                                                        |
| Search engines   | **Default to DuckDuckGo; preload Brave Search, Startpage, Google, Bing as switchable options.**       | DDG default aligns with G3 without removing user choice.                                                                                                                                                                        |
| Accessibility    | **WCAG AA enforced via automated CI checks on both default themes; manual audit before each release.** | Concretizes M1's AA claim into something testable.                                                                                                                                                                              |

## 11. Out of Scope (this document)

Implementation details, milestone breakdown, and roadmap sequencing are tracked separately (e.g., in a roadmap document or planning artifacts), not in this PRD.

## 12. Glossary

- **Brave Shield:** Brave browser's built-in ad/tracker/fingerprint blocking system.
- **WCAG AA:** Web Content Accessibility Guidelines, level AA contrast and accessibility conformance.
- **MCP:** Model Context Protocol server providing tools to AI development agents.
- **MV2/MV3:** Chromium extension manifest versions 2 and 3.
- **DoH/DoT:** DNS over HTTPS / DNS over TLS.
