# Phase 8 — Appearance Subsystem (CONTEXT)

> Discuss-phase output for Phase 8. Decisions captured here are inputs to `08-PLAN.md`.
>
> **Mode:** `/gsd-discuss-phase 8 --auto` — agent-selected recommended defaults, no interactive questions. The user mandate is "make small decisions yourself; report what + why."
>
> **Status update (2026-04-29):** `stitch` MCP is now configured and the Phase 8 token handoff is **complete**. Both Light and Dark themes were generated, ideology-validated against the screenshots, and the locked palette + typography scale lives at [.planning/sketches/phase-08/stitch-output.md](../../sketches/phase-08/stitch-output.md). [Decision D-08](#d-08--token-handoff-stitch-mcp-pending) is now LOCKED with final hex values. Phase 8 is unblocked end-to-end.

## 1. Goal restated

Deliver phlink's appearance subsystem in three layers: (1) a phlink color mixer that overrides Chromium defaults with a phlink-branded palette, (2) two default themes (Light, Dark) per [PRD §3.2 M1](../../../docs/dev/PRD.md), (3) a "Follow System" switcher in settings, and (4) a CI gate that fails the build when either default theme regresses below WCAG AA contrast. Community themes are stubbed for v1.1.

## 2. Hard constraint review

| Constraint | Decision |
| --- | --- |
| WCAG AA contrast for both themes | Enforced by Phase 11-04-style audit script + new gtest. Threshold: 4.5:1 normal text, 3:1 large text / non-text UI per WCAG 2.2 SC 1.4.3 / 1.4.11. |
| Site isolation stays ON | Theme system is browser-process only; no renderer-side capabilities added. CSS injection for cosmetic adblock (Phase 5) is unrelated to and must not interfere with theming. |
| No phone-home | Theme assets ship in the binary. No remote theme fetch in v1; community theme infra ships as part of v1.1 and will be local-file-import-only at first. |
| No proprietary blobs | All palette values are first-party. Token authoring uses `stitch` MCP (open-source workflow); generated CSS / SkColor literals land as ordinary source files under `chrome/browser/ui/color/`. |
| MV3-only extension implications | None — theming is internal, not extension-mediated. |

## 3. Domain & boundaries

**In scope (Phase 8):**
- `chrome/browser/ui/color/phlink_color_mixer.{cc,h}` — registers phlink color overrides keyed on `ColorMode::kLight` / `kDark`.
- `chrome/browser/ui/color/phlink_color_id.h` — `kColorPhlink*` token IDs.
- `chrome/browser/ui/color/phlink_palette.{cc,h}` — concrete light/dark palette tables.
- `prefs::kPhlinkAppearanceMode` — integer pref `{0=light, 1=dark, 2=follow_system}`.
- A small piece of `chrome/browser/resources/settings/appearance_page/` adding a 3-radio "phlink theme" row (Light / Dark / Follow System).
- `chrome/browser/ui/color/phlink_color_contrast_unittests.cc` — WCAG-AA gate, hooked into `unit_tests`.
- `.github/workflows/lint.yml` — extend with a hex-extraction smoke check that runs phlink-specific contrast assertions in CI without a Chromium build (a tiny Python script that mirrors the gtest pairs against the same SkColor literals).

**Out of scope (deferred):**
- **Community theme installation UI** — v1.1, separate phase.
- **Per-element theme override** (custom omnibox color, per-tab tint) — v1.1.
- **Window-frame native styling on macOS / Windows** — handled by upstream `NativeChromeColorMixer`, not overridden.
- **Settings WebUI mojom plumbing for adblock** — that's plan 5-06b, which inherits Phase 8's settings pattern but lands separately.

## 4. Canonical refs

> Mandatory. Every doc/spec/ADR a downstream agent needs, with full relative paths.

- [.planning/ROADMAP.md](../../ROADMAP.md) — Phase 8 goal, success criteria, plan list.
- [.planning/REQUIREMENTS.md](../../REQUIREMENTS.md) §APPR-01..05 — locked acceptance criteria.
- [docs/dev/PRD.md](../../../docs/dev/PRD.md) §3.2 M1 (palette names), §10.1 D-04 (site isolation), §10.1 D-12 (two built-in themes WCAG-AA).
- [docs/dev/phase-08-scoping.md](../../../docs/dev/phase-08-scoping.md) — upstream theme stack audit, integration surface, token namespace decision.
- [docs/dev/architecture.md](../../../docs/dev/architecture.md) §3 (UI layer), §7 (where new code goes).
- [docs/dev/third-party-licenses.md](../../../docs/dev/third-party-licenses.md) — manifest the contrast-gate script must keep license-clean.
- Upstream Chromium files (read-only references):
  - `chrome/browser/ui/color/chrome_color_mixers.cc` — registration order; phlink mixer slots after `AddNativeChromeColorMixer` and before `key.custom_theme`.
  - `chrome/browser/ui/color/chrome_color_id.h` — convention for `E_CPONLY(kColorPhlink*)` macro entries.
  - `ui/color/color_provider_key.h:29-30` — `ColorMode::{kLight,kDark}` enum.
  - `ui/color/color_utils.h` — `GetContrastRatio()` API the unittest will call.
  - `chrome/browser/themes/theme_service.h:121-148` — `UseSystemTheme()` / `UsingSystemTheme()` for the system-follow toggle.
  - `chrome/browser/resources/settings/appearance_page/appearance_page.{html,ts}` — settings UI host.

**stitch design handoff (LOCKED 2026-04-29):**
- [.planning/sketches/phase-08/stitch-output.md](../../sketches/phase-08/stitch-output.md) — consolidated token palette, typography, spacing, contrast verification.
- [.planning/sketches/phase-08/light-screenshot.png](../../sketches/phase-08/light-screenshot.png) — desktop chrome://settings/appearance Light validation.
- [.planning/sketches/phase-08/dark-screenshot.png](../../sketches/phase-08/dark-screenshot.png) — desktop chrome://settings/appearance Dark validation.
- [.planning/sketches/phase-08/light-stitch-raw.json](../../sketches/phase-08/light-stitch-raw.json) — stitch generation source (Light).
- [.planning/sketches/phase-08/dark-stitch-raw.json](../../sketches/phase-08/dark-stitch-raw.json) — stitch generation source (Dark).

## 5. Carrying forward (prior decisions)

- From Phase 4 / patches `0001`–`0002` — phlink branding identity is set; theme tokens cannot reintroduce "Chromium" or "Chrome" naming in any user-visible string.
- From Phase 5 / patch `0097` — renderer cosmetic agent uses `WebDocument::InsertStyleSheet` for adblock CSS. **The phlink color mixer must not collide with renderer-side stylesheet injection** — they target disjoint surfaces (browser chrome vs page content), but the agent reviewing must check no shared `kColor*` IDs leak into Blink-level styling.
- From Phase 6 / patches `0101`–`0102` — privacy posture forbids telemetry on theme switches. The system-follow observer must NOT emit UMA.
- From Phase 7-05 — benchmark harness is `tests/benchmark_60tab/` (pytest+CDP). If theme work changes startup cost noticeably, regression must surface there. Plan 08-05 should call out re-running the benchmark before merge.
- From Phase 11 (this session) — `scripts/license-audit.py` exists; any new third-party crate brought in for theme work (none expected) must update `docs/dev/third-party-licenses.md` in the same patch.

## 6. Decisions

### D-01 — Token namespace: `kColorPhlink*`

All phlink-introduced color IDs use the `kColorPhlink*` prefix. Lives in `chrome/browser/ui/color/phlink_color_id.h`. Each ID gets an `E_CPONLY(kColorPhlinkX)` entry in a `PHLINK_COLOR_IDS` macro and is included from the existing `chrome_color_id.h` so it participates in the chrome color id map.

**Rationale.** Avoids collision with the ~hundreds of upstream `kColorChrome*` / `kColorBrowser*` IDs. Grep-able, mechanical to audit. Same pattern Brave uses for `kColorBrave*`.

### D-02 — Mixer registration: after Native, before custom_theme

`AddPhlinkColorMixer(provider, key)` is called from `AddChromeColorMixers()` in `chrome_color_mixers.cc`, **after** `AddNativeChromeColorMixer` and **before** the `if (key.custom_theme) { … }` block.

**Rationale.** `AddNativeChromeColorMixer` is upstream's "let the platform have the last word" hook (e.g., macOS vibrancy). phlink's brand identity overrides those, but a future user-installed community theme (`key.custom_theme`) should still win. Confirmed valid against `phase-08-scoping.md` §2.1.

### D-03 — ColorMode dispatch via existing key field

We rely on `ui::ColorProviderKey::ColorMode` (`kLight` / `kDark`) which `ColorProviderManager` already populates from `NativeTheme::ShouldUseDarkColors()`. No new plumbing for system-follow at the mixer layer.

**Rationale.** Upstream already does the hard work for us on macOS / Windows. Linux's `theme_service` system-follow path is the only one that needs the pref-driven override.

### D-04 — Pref schema: single integer `prefs::kPhlinkAppearanceMode`

```
0 = Light
1 = Dark
2 = Follow System  (default for new installs)
```

Pref lives in `chrome/browser/profiles/profile_prefs.cc` (or the per-profile prefs file phlink already uses for adblock). Changes trigger a `ColorProviderManager::ResetColorProviderCache()` and `BrowserList::UpdateAllBrowserViews()` on a `ThemeServiceObserver` callback.

**Rationale.** Single integer is robust to roaming, easy to migrate, and matches Chromium's `prefs::kBrowserColorScheme` shape (which we deliberately do **not** override — phlink owns its own pref so behavior is independent of upstream UI changes).

### D-05 — Settings UI: dedicated phlink subsection

Add a new section "phlink theme" inside `chrome/browser/resources/settings/appearance_page/appearance_page.html` with three radio buttons bound to `prefs::kPhlinkAppearanceMode`. No new mojom; uses the existing `appearance_browser_proxy.ts` pref-binding plumbing.

**Rationale.** Smallest possible WebUI footprint. Doesn't fight upstream's existing "Theme" / "Color" rows — phlink's row appears above them, and on the default `is_chrome_branded=false` build the upstream "Chrome theme" row is naturally hidden.

### D-06 — Default mode: Follow System

Out of the box, new profiles get `kPhlinkAppearanceMode = 2 (Follow System)`.

**Rationale.** Matches user expectation in 2026 (every other major OS-level app does this). User's explicit opt-in to Light or Dark sticks across restarts.

### D-07 — WCAG-AA gate: gtest + lint-time mirror

Two layers:

1. **`chrome/browser/ui/color/phlink_color_contrast_unittests.cc`** — gtest that walks every `(background, foreground)` pair declared in `phlink_palette.cc` and asserts `color_utils::GetContrastRatio(bg, fg) >= 4.5` for normal-text pairs and `>= 3.0` for large-text / non-text pairs. Runs in `unit_tests`.
2. **`scripts/contrast-audit.py`** + step in `.github/workflows/lint.yml`. Parses the same hex literals out of `phlink_palette.cc` (regex over `0x[0-9a-fA-F]{6,8}`), reproduces the contrast math in pure Python, asserts the same thresholds. Catches regressions on PRs that don't trigger a Chromium build.

**Rationale.** Belt-and-braces: Chromium build CI is expensive and not yet wired (per [docs/dev/ci.md](../../../docs/dev/ci.md) §"Later"). Lint-time mirror keeps the gate green on every PR; gtest catches anything the regex misses.

### D-08 — Token handoff: stitch output LOCKED

stitch MCP authored both themes (project `12962487919675094023` — "phlink Browser Chrome"). Both screenshots were ideology-validated against PRD §3.2 M1 (recessive, no marketplace, no telemetry surfaces, hairlines + no shadows, WCAG AA). Final tokens below; full details, typography scale, spacing, and contrast verification table at [.planning/sketches/phase-08/stitch-output.md](../../sketches/phase-08/stitch-output.md).

**Light theme (locked hex):**

| Token | Hex | Role |
| --- | --- | --- |
| `kColorPhlinkCanvas` | `#FFFFFF` | Window canvas |
| `kColorPhlinkSurface` | `#F8F4EC` | Sidebar / inactive surface (warm off-white) |
| `kColorPhlinkSurfaceAlt` | `#F1EDE5` | Hover on surface |
| `kColorPhlinkCard` | `#FFFFFF` | Card / dropdown |
| `kColorPhlinkText` | `#1A1A1A` | Primary text |
| `kColorPhlinkTextMuted` | `#525252` | Secondary text |
| `kColorPhlinkHairline` | `#E5E0D6` | 1px borders |
| `kColorPhlinkAccent` | `#A8C8E8` | Pastel Sky Blue — selected/focus/toggle-on |
| `kColorPhlinkOnAccent` | `#1A1A1A` | Foreground on accent (11.4:1) |
| `kColorPhlinkDanger` | `#C0392B` | Reset / destructive |
| `kColorPhlinkSuccess` | `#2E8540` | Confirmation |

**Dark theme (locked hex):**

| Token | Hex | Role |
| --- | --- | --- |
| `kColorPhlinkCanvas` | `#0D0D0D` | Window canvas (near-black, slight warmth) |
| `kColorPhlinkSurface` | `#181818` | Sidebar surface |
| `kColorPhlinkSurfaceAlt` | `#1F1F1F` | Card surface |
| `kColorPhlinkCard` | `#1F1F1F` | Card / dropdown |
| `kColorPhlinkText` | `#FFFFFF` | Primary text |
| `kColorPhlinkTextMuted` | `#A0A0A0` | Secondary text |
| `kColorPhlinkHairline` | `#2A2A2A` | 1px borders |
| `kColorPhlinkAccent` | `#F5E68A` | Pastel Yellow — selected/focus/toggle-on |
| `kColorPhlinkOnAccent` | `#000000` | **Critical:** foreground on accent fills (16:1). NEVER white. |
| `kColorPhlinkDanger` | `#F5736B` | Reset / destructive (lightened for dark) |
| `kColorPhlinkSuccess` | `#6FE38A` | Confirmation |

**Departures from D-08 placeholders (intentional):**
1. Surfaces are now **opaque** (no α channel). Translucent surfaces would have failed on Windows builds without compositor blur (open risk #3 in §9). The stitch-validated visual achieves recessive feel via warm off-white in Light and layered greys in Dark — no transparency needed.
2. Token list expanded from 4 to 11 per theme. The original four-token model was insufficient for real settings UI (need separate canvas, surface, card, hairline, danger, success roles). All eleven tokens follow the `kColorPhlink*` namespace per D-01.
3. Typography scale adopted from stitch (Inter, 11/12/13/14/18/20px). Documented in stitch-output.md §3.

**Rationale.** stitch's auto-generated Material tonal palette was rejected as authoritative — it drifted from PRD §3.2 M1 named colors. The phlink-locked hex above came from the prompts (PRD-aligned) and was visually validated against rendered desktop screenshots in both modes.

### D-09 — Patch slot range

Phase 8 patches occupy `0110`–`0119` (10 slots reserved). Today's used slots: `0001`–`0102`. Plan 08-01b lands at `0110`. Plan 08-02 (light theme) at `0111`. Plan 08-03 (dark theme) at `0112`. Plan 08-04 (settings UI) at `0113`. Plan 08-05 (CI gate) at `0114`. Buffer of 5 for surprises.

### D-10 — System-follow observer placement

A new `PhlinkAppearanceModeObserver` lives in `chrome/browser/themes/phlink_appearance_observer.{cc,h}`. It subscribes to:
1. `PrefChangeRegistrar` for `prefs::kPhlinkAppearanceMode`.
2. `ui::NativeTheme::Get()->AddObserver(this)` for OS-level dark-mode changes (only meaningful when pref == Follow System).

On change, calls `ColorProviderManager::Get().ResetColorProviderCache()` and walks `BrowserList::GetInstance()` to invalidate browser views.

**Rationale.** Centralized observer, single owner, easy to unit-test. Mirrors how `theme_service.cc` already handles upstream's `kBrowserColorScheme` pref.

### D-11 — Performance posture

Theme switches are user-initiated and rare (≪ 1/min). No need to optimize the swap path. The mixer itself is called once per ColorProvider construction, which is cached. **No theme-related code in any hot path.** Specifically, no per-frame, per-paint, or per-network-request theming work.

**Rationale.** Avoids the temptation to cache pre-resolved SkColors anywhere — Chromium's `ColorProvider` already caches.

### D-12 — Testing strategy

| Layer | Test | Where |
| --- | --- | --- |
| Color tokens | `phlink_color_contrast_unittests.cc` | gtest, `chrome/browser/ui/color/` |
| Mixer registration | `phlink_color_mixer_unittests.cc` — assert `AddPhlinkColorMixer` was called by `AddChromeColorMixers` and that `kColorPhlinkPaletteAccent` resolves to a non-zero SkColor for both modes. | gtest |
| Pref → ColorMode | `phlink_appearance_observer_unittests.cc` — fake NativeTheme + PrefService, assert observer flips ColorMode. | gtest |
| Settings WebUI | Playwright E2E (one test): launch phlink, open `chrome://settings/appearance`, select Dark, assert browser chrome contrast inverts. | `tests/e2e/appearance_test.ts` (new dir for Phase 8). |
| WCAG audit (lint) | `scripts/contrast-audit.py` | `.github/workflows/lint.yml` |

**Playwright is preferred** for the settings flow per [docs/dev/mcp-workflow.md](../../../docs/dev/mcp-workflow.md) §1.

## 7. Deferred ideas (noted, not in this phase)

- **Per-tab accent tint** — v1.1 candidate. Requires per-`WebContents` ColorProviderSource, not in scope.
- **Custom user CSS** — out of scope forever; phlink does not ship a userChrome.css mechanism.
- **Auto-darken websites at 11pm local time** — no. Theme follows OS or user choice; no time-of-day logic.
- **Theme marketplace / discovery URL** — depends on Phase 14 (curated extension list); both deferred.
- **Animation on theme switch** — no. Instant swap. Animation would add a frame budget cost we don't need to take.
- **Window-frame vibrancy on macOS** — defer to upstream `NativeChromeColorMixer`; do not override.

## 8. Folded todos

(none — todo backlog has no Phase 8 items as of 2026-04-29)

## 9. Open risks

1. ~~**stitch MCP not wired up**~~ — RESOLVED 2026-04-29. Tokens locked, see D-08.
2. **Linux gtk-theme integration** — upstream's Linux theming (`chrome/browser/ui/color/linux/`) competes for the same color slots. May need a phlink-vs-gtk precedence call. Probably defer: phlink-on-Linux v1 alpha can let the upstream Linux mixer have last word; we revisit at v1.0.
3. **Translucent surfaces** — alpha-channel colors in the surface tokens may render incorrectly on Windows where the chrome window doesn't support compositor blur. Mitigation: keep alpha conservative (≤ 0.7) and ship a fallback opaque surface if the OS reports no blur available. Plan 08-02 / 08-03 must verify this.
4. **WCAG large-text vs normal-text classification** — the gate needs a per-pair "this is normal text" vs "this is non-text UI" tag. Plan 08-05 will define a small DSL in `phlink_palette.cc` (e.g., a `kPhlinkContrastNormalText` array vs `kPhlinkContrastNonText` array) to make the test mechanical.

## 10. Patch slot range (mirror of D-09)

`0110`–`0119` (Phase 8 reserved). First used: `0110` for 08-01b once stitch lands tokens.

---

**Phase entry criteria** (must be true before 08-01b plan starts):
- [x] `stitch` MCP configured in workspace.
- [x] Stitch design doc lands at `.planning/sketches/phase-08/stitch-output.md` with concrete hex values for each placeholder in D-08.
- [x] Doc added to canonical refs (§4 above).

**Phase 8 is fully unblocked.** Ready for `/gsd-plan-phase 8`.
