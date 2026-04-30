# phlink

## What This Is

phlink is an open-source, cross-platform Chromium-based browser for macOS, Linux, and Windows that pairs Brave-tier privacy and ad-blocking with measurably lower resource usage than Chrome and Firefox — wrapped in an aesthetic, customizable UI rather than a developer-tool look. It targets power users, privacy-conscious users, developers, and aesthetics-driven users who feel underserved by mainstream and existing privacy browsers.

## Core Value

A measurably lighter, privacy-by-default Chromium browser whose every default leans toward performance and privacy, without locking users out of customization.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **Extreme Performance (G1)** — ≥30% lower RAM and ≥20% lower CPU than Chrome on a reproducible 60-tab benchmark, no feature regressions vs. upstream Chromium stable.
- [ ] **Ad/Tracker Blocking (G2)** — Built-in network + cosmetic blocking at parity with Brave Shield (±5% on a shared corpus), per-site shield UI, custom filter lists, element picker.
- [ ] **Privacy by Design (G3)** — Architectural privacy: fingerprinting resistance, third-party cookie isolation, referrer minimization, DoH/DoT, partitioned storage, network-state isolation, query-param stripping, zero outbound telemetry by default.
- [ ] **Appearance (M1)** — Two WCAG AA-compliant default themes (Light: pastel sky blue / translucent off-white / white; Dark: pastel yellow / translucent light grey / black / white) inspired by isometric-game aesthetics; theme engine for community themes (post-v1).
- [ ] **Documentation (M2)** — `docs/user/` and `docs/dev/` covering install, features, settings, troubleshooting, privacy explanations, architecture, build, contribution, extension model, and release process.
- [ ] **Cross-platform parity** — macOS, Linux, Windows with green CI on all three; signed native installers; auto-update with verifiable signatures.
- [ ] **OSS-only supply chain** — every shipped library, asset, and tool is OSS with a compatible license; tracked in repo.
- [ ] **Local-only encrypted profile export/import** — no cloud sync in v1; self-hostable sync deferred to v2.
- [ ] **Standard Chromium extensions support** — install via Chrome Web Store URLs, ship no Google services; curated phlink-vetted list for first-run discovery.

### Out of Scope

- **Mobile platforms (iOS, Android)** — desktop-first; mobile is a future product.
- **Proprietary sync/cloud service** — undermines G3 (privacy by default).
- **Built-in cryptocurrency wallet, rewards system, or VPN** — bloat; counter to performance and privacy goals.
- **Custom rendering engine** — phlink stays on Chromium; replacing Blink is not the bet.
- **Forked extension store** — reusing Chrome Web Store URLs preserves the ecosystem; forking harms users.
- **Opt-in telemetry in v1** — no telemetry path in v1; if added later, must be local-first and explicitly opt-in.
- **Real-time chat / video posts / OAuth login** — not part of a browser product (carried over from prior templates only as anti-features).

## Context

- **Greenfield**: only `LICENSE` and `docs/dev/PRD.md` exist at init. No source tree yet.
- **Upstream base**: track Chromium stable; rebase on each stable bump. Customizations live as bundled extensions/components plus a minimal patch set to minimize rebase pain.
- **Adblock engine**: `adblock-rust` (Brave's MPL-2.0 Rust engine) — directly aligns with G2 parity target.
- **Default DoH**: Cloudflare `1.1.1.1` (no-logging tier); Quad9 and NextDNS preconfigured; user can pick or enter custom.
- **Default search**: DuckDuckGo; Brave Search, Startpage, Google, Bing preloaded as switchable.
- **Password manager**: Chromium's built-in, local-only, OS-keychain-backed (Keychain / libsecret / DPAPI). Cloud sync disabled.
- **Update mechanism**: TUF-style signed updates over HTTPS, per-platform native installers, no background account.
- **Process model**: upstream Chromium site-isolation default ON. Performance gains come from a tab-grouping-aware discarder, not weaker isolation.
- **Docs cache**: `.refs/<ecosystem>/<project>@<version>/` (gitignored) for offline reference of upstream docs feeding AI-assisted development.
- **MCP-assisted development**: `playwright`, `stitch-mcp` (design system / UI / logo / assets), `git` MCP, others as documented.
- **Telemetry**: zero outbound telemetry from phlink itself by default; no opt-in telemetry in v1.
- **Themes**: two ship in v1 (Light, Dark). Community themes from v1.1+, not v1.
- **License hygiene**: every bundled filter list / asset / dependency recorded in `docs/dev/third-party-licenses.md`. Brave-sourced lists shipped only where MPL-compatible.
- **Reproducible builds**: stretch goal, not a v1 gate.

## Constraints

- **Tech stack**: Chromium upstream stable + bundled extensions/components + minimal core patch set. `adblock-rust` for blocking.
- **Platforms**: macOS, Linux, Windows. CI must be green on all three.
- **License**: OSS-only shipped binaries. License compatibility audited before any new dependency lands.
- **Performance**: ≥30% lower steady-state RAM and ≥20% lower steady-state CPU vs Chrome on the 60-tab benchmark; no regression in cold-start time vs Chrome on equivalent hardware; no greater crash rate than upstream Chromium stable.
- **Privacy**: pass EFF Cover Your Tracks and Brave fingerprint suites at parity or better with Brave defaults; zero outbound telemetry by default.
- **Accessibility**: both default themes WCAG AA verified via automated CI checks; manual audit before each release.
- **Update integrity**: signed updates only; signature verification before applying.
- **Repo discipline**: every adopted OSS project recorded with name, version, license, why-chosen, integration notes, and link to its `.refs/` cache entry.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Track Chromium stable; bundle features as extensions/components + minimal patch set | Minimize upstream-rebase cost; ship security fixes promptly | — Pending |
| `adblock-rust` as blocking engine | OSS (MPL-2.0), Brave Shield parity, battle-tested | — Pending |
| Default DoH = Cloudflare 1.1.1.1 (no-log); Quad9 + NextDNS preconfigured | Audited no-log policies; same defaults as Firefox/Brave | — Pending |
| Default search = DuckDuckGo; Brave Search / Startpage / Google / Bing preloaded | Aligns with G3 without removing user choice | — Pending |
| Local-only encrypted profile export/import; no cloud sync in v1 | Cloud sync undermines G3; self-hosting deferred to v2 | — Pending |
| Standard Chromium extensions via Chrome Web Store URLs; ship no Google services; curated phlink-vetted list | Preserves ecosystem; avoids lock-in; supports privacy curation | — Pending |
| Zero outbound telemetry by default; no opt-in telemetry in v1 | Removes a class of risk to G3 | — Pending |
| Update mechanism = TUF-style signed updates over HTTPS, no background account | Security without identity or telemetry | Phase 10 shipped: TUF metadata/client, native installers, platform signing gates, and release provenance checks |
| Process model = upstream site-isolation ON; perf via tab-grouping-aware discarder | Site isolation is non-negotiable; gains come from smarter discarding | — Pending |
| Two themes ship in v1 (Light, Dark); community themes deferred to v1.1+ | Keeps v1 scope tight without closing the door on M1 | — Pending |
| Docs cache path = `.refs/` (gitignored) | Short, unambiguous, no collision with build/tool dirs | — Pending |
| Password manager = Chromium built-in, local-only, OS-keychain-backed | Reuses upstream code; respects G3; platform-native security | — Pending |
| Accessibility = WCAG AA enforced in CI on both default themes; manual audit per release | Concretizes M1 into something testable | — Pending |
| Default filter lists = EasyList, EasyPrivacy, uBO, Peter Lowe's, Brave (where MPL-compatible) | Brave-Shield parity while staying license-clean | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-30 after Phase 10 verification*
