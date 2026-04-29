# Phase 8 — Appearance Subsystem: Scoping & Integration Plan

> Status: scoping only. The implementation plans listed in [.planning/ROADMAP.md](../../.planning/ROADMAP.md) §"Phase 8" remain `[ ]`. This document captures the audited integration surface so a follow-up interactive session can author tokens via `stitch-mcp` and wire the WebUI without re-discovering the same context.

## 1. Why this is scoping-only (not a full autonomous build)

Phase 8 spans four sub-domains that each demand human-in-the-loop design judgment:

1. **Design tokens** — PRD §3.2 M1 names colors ("Pastel Sky Blue", "Translucent Off-white", "Pastel Yellow", "Translucent Light Grey") but does **not** lock hex values. Per `.github/copilot-instructions.md` §10, tokens must be authored via `stitch-mcp`, not hand-rolled by an autonomous agent.
2. **WebUI** — adds a phlink-flavored panel under `chrome://settings/appearance` (and unblocks 5-06b's `chrome://settings/phlink/adblock`). WebUI work needs interactive screenshot review.
3. **System-follow** — depends on `ui::NativeTheme::ShouldUseDarkColors()` propagation through the existing `ColorProviderKey::color_mode` field, plus pref plumbing — fine to flip, but only after tokens exist.
4. **WCAG-AA CI gate** — needs a real token table to test against. Useless before §1 lands.

The autonomous heuristic (`copilot-instructions.md` §"Heuristic: ship small flips/audits autonomously; defer big new subsystems") routes Phase 8 to this scoping doc + a roadmap split.

## 2. Upstream integration surface (audited 2026-04-29 against `phlink-wip`)

### 2.1 Color provider entry points

The color system is a 3-layer stack:

| Layer | Path | Role |
| --- | --- | --- |
| Core IDs | `ui/color/color_id.h` | Cross-component semantic IDs (`kColorPrimary`, `kColorAccent`, …) |
| Chrome IDs | `chrome/browser/ui/color/chrome_color_id.h` | `kColorAppMenu*`, `kColorTabStrip*`, `kColorOmnibox*`, … (~hundreds) |
| Mixer dispatch | `chrome/browser/ui/color/chrome_color_mixers.cc` → `AddChromeColorMixers()` | Calls each per-area mixer in order; `AddNativeChromeColorMixer` is **last** so platforms can override. |

Phlink integration: register an `AddPhlinkColorMixer(provider, key)` call **after** `AddNativeChromeColorMixer` and **before** the `key.custom_theme` user-theme override block. This guarantees:

- phlink-branded tokens win over Chrome defaults,
- user-installed community themes (post-v1.1) still win over phlink defaults.

The `key.color_mode` enum (`ui::ColorProviderKey::ColorMode::{kLight,kDark}`, defined `ui/color/color_provider_key.h:29-30`) already gives us per-mode dispatch — no new plumbing required for system-follow at the mixer layer.

### 2.2 Theme service & system-follow

- `chrome/browser/themes/theme_service.{h,cc}` already exposes `UseSystemTheme()` / `UsingSystemTheme()` and a `ui::SystemTheme` enum (`ui/color/system_theme.h`).
- Linux today is the only platform that exercises this branch in upstream Chrome. macOS/Windows already follow OS dark-mode through `NativeTheme`.
- Phlink's "Follow System" toggle = bind a single `prefs::kPhlinkAppearanceMode` integer pref (`{0=light, 1=dark, 2=system}`) + a `ThemeServiceObserver` that pushes the resulting `ColorMode` into `ColorProviderManager::ResetColorProviderCache()` on change.

### 2.3 Settings WebUI

- Existing surface: `chrome/browser/resources/settings/appearance_page/appearance_page.{html,ts}`.
- Phlink panel = a new subsection (or a replacement section under `is_chrome_branded=false`) with three radio rows: Light / Dark / Follow System. No new mojo interfaces — uses the existing `appearance_browser_proxy.ts`.

### 2.4 WCAG-AA CI gate

- Token table will live at `chrome/browser/ui/color/phlink_color_tokens.h` (one `struct PhlinkPalette { SkColor bg; SkColor fg; … };` per mode).
- CI test: a new `phlink_color_contrast_unittests.cc` that walks every `(bg, fg)` pair in the table and asserts `color_utils::GetContrastRatio(bg, fg) >= 4.5` (WCAG AA normal text) or `>= 3.0` (large text / non-text), gated on the same pairs the design contract calls out.
- Hooked into `unit_tests` target — falls into the existing CI matrix from Phase 2.

## 3. Decision: token namespace

All phlink-introduced color IDs use the `kColorPhlink*` prefix to avoid collisions with the ~hundreds of existing `kColorChrome*` / `kColorBrowser*` IDs.

Examples (placeholders pending stitch-mcp):

```
kColorPhlinkPaletteAccent          // "Pastel Sky Blue" (light) / "Pastel Yellow" (dark)
kColorPhlinkPaletteSurface         // "Translucent Off-white" / "Translucent Light Grey"
kColorPhlinkPaletteSurfaceContrast // White (both modes)
kColorPhlinkPaletteForeground      // dark grey (light) / White (dark)
```

These IDs land alongside concrete tokens in plan 08-02 (Light) and 08-03 (Dark), not now.

## 4. Roadmap split applied (see [.planning/ROADMAP.md](../../.planning/ROADMAP.md))

The original five plans (08-01..05) remain. **08-01 is split** into:

- **08-01a — _this doc_**: Scoping + integration audit. **Done autonomously.**
- **08-01b**: Implement `phlink_color_mixer.{cc,h}`, register it in `chrome_color_mixers.cc`, introduce `kColorPhlink*` IDs. **Interactive** (needs stitch-mcp for first token values).

08-02 / 08-03 / 08-04 / 08-05 are unchanged and remain interactive.

## 5. References

- Upstream color system overview: `.refs/chromium/chromium@main/docs/ui/color/` (if present in the snapshot; otherwise `ui/color/README.md` in tree).
- ColorMixer authoring guide: `ui/color/color_mixer.h` doc-comment + `ui/color/README.md`.
- Theme service: `chrome/browser/themes/theme_service.h:121-148`.
- PRD palette: [docs/dev/PRD.md §3.2 M1](PRD.md).
- Locked decisions: [docs/dev/PRD.md §10.1](PRD.md) — D-12 "two built-in themes, both WCAG-AA".
