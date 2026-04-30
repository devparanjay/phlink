# Phase 8 — RESEARCH

> Targeted research for the appearance subsystem. CONTEXT D-01..D-12 are LOCKED; this doc records only the upstream-Chromium-side facts the plans need to be deterministic.

## 1. Mixer registration surface

**File:** `chrome/browser/ui/color/chrome_color_mixers.cc`
**Function:** `AddChromeColorMixers(ui::ColorProvider*, const ui::ColorProviderKey&)`
**Observed registration order (chromium@main, line ~58–82):**

```
AddChromeColorMixer
AddNewTabPageColorMixer
AddOmniboxColorMixer
AddProductSpecificationsColorMixer
AddProjectsPanelColorMixer
AddTabStripColorMixer
AddMaterialChromeColorMixer
AddMaterial{NTP,Omnibox,SidePanel,TabStrip}ColorMixer
AddNativeChromeColorMixer            ← "Must be the last one in order to override other mixer colors."
if (key.custom_theme) { key.custom_theme->AddColorMixers(provider, key); }
```

**Per CONTEXT D-02**, phlink mixer slots **after `AddNativeChromeColorMixer`** and **before** the `key.custom_theme` block. This intentionally overrides the comment's "Must be last" — phlink brand identity wins over native vibrancy, but a user-installed community theme (`custom_theme`) still wins.

**Insertion line:** between the existing `AddNativeChromeColorMixer(provider, key);` and `if (key.custom_theme)` block. Patch 0110 inserts a single new call `AddPhlinkColorMixer(provider, key);` plus `#include "chrome/browser/ui/color/phlink_color_mixer.h"`.

## 2. Color ID convention

**File:** `chrome/browser/ui/color/chrome_color_id.h`
**Pattern:** `E_CPONLY(kColorXxx)` macros inside a `COMMON_CHROME_COLOR_IDS` (or sibling) `#define` block, with the first ID seeded by `kChromeColorsStart`. The list is consumed by `ui/color/color_id_macros.inc` to produce both an enum and a `(id, "name")` map.

**Per CONTEXT D-01**, phlink defines its own header `chrome/browser/ui/color/phlink_color_id.h` containing a `PHLINK_COLOR_IDS` macro of `E_CPONLY(kColorPhlink*)` entries (11 light/dark-shared role tokens — D-08). The phlink macro is appended to `COMMON_CHROME_COLOR_IDS` (or invoked alongside it in `chrome_color_id.h`) so phlink IDs participate in the chrome color id map for `ColorIdName()` resolution and for DCHECK pretty-printing.

## 3. ColorMode dispatch

**File:** `ui/color/color_provider_key.h`, lines 28–31:
```
enum class ColorMode { kLight, kDark };
```
`ColorProviderManager` populates this from `ui::NativeTheme::ShouldUseDarkColors()`. **Per CONTEXT D-03**, no new plumbing at the mixer layer — the mixer reads `key.color_mode` and branches to the Light or Dark palette table.

## 4. Pref / observer pattern

**Reference:** `chrome/browser/themes/theme_service.{h,cc}`
- Owns a `PrefChangeRegistrar` for `prefs::kBrowserColorScheme`.
- Subscribes via `ui::NativeTheme::Get()->AddObserver(this)` for OS-level dark-mode flips.
- On change → `ColorProviderManager::Get().ResetColorProviderCache()` + walks `BrowserList`.

**Per D-10**, phlink mirrors this in `chrome/browser/themes/phlink_appearance_observer.{h,cc}` for `prefs::kPhlinkAppearanceMode` (integer pref, 0/1/2; **D-04, D-06** default = 2 / Follow System). Pref registration lives wherever phlink already registers per-profile prefs (Phase 5 added one — verify in 08-04 plan).

## 5. Settings WebUI surface

**Files (all exist upstream):**
- `chrome/browser/resources/settings/appearance_page/appearance_page.html`
- `chrome/browser/resources/settings/appearance_page/appearance_page.ts`
- `chrome/browser/resources/settings/appearance_page/appearance_browser_proxy.ts`

The page already uses Polymer/Lit-style pref binding via `prefs::` paths. **Per D-05**, plan 08-04 inserts a new "phlink theme" section *above* the existing Theme/Color rows with three radio buttons bound to `prefs::kPhlinkAppearanceMode`. No new mojom; reuses existing pref binding plumbing. Existing upstream "Chrome theme" row is naturally hidden on `is_chrome_branded=false` builds (phlink default).

## 6. WCAG-AA gate APIs

- **In-process:** `ui/color/color_utils.h` → `color_utils::GetContrastRatio(SkColor a, SkColor b)` returns the WCAG luminance ratio.
- **Out-of-process:** pure-Python re-implementation of the WCAG 2.2 relative-luminance formula (sRGB → linearise → 0.2126/0.7152/0.0722 weights), feeding `(L1+0.05)/(L2+0.05)`. Standard, license-clean, ~30 lines.

**Per D-07 / D-12**, two layers:
1. `chrome/browser/ui/color/phlink_color_contrast_unittests.cc` — gtest hooked into the existing `unit_tests` target via `chrome/test/BUILD.gn`. Walks two arrays in `phlink_palette.cc`: `kPhlinkContrastNormalText[]` (≥4.5:1) and `kPhlinkContrastNonText[]` (≥3:1). Both Light and Dark are exercised by parametrising on `ColorProviderKey::ColorMode`.
2. `scripts/contrast-audit.py` — regex-extracts `0x[FF]?RRGGBB` literals from `phlink_palette.cc`, mirrors the same pair tables (kept in a tiny structured manifest the script reads), reproduces the math in pure Python, exits non-zero on any failing pair. Called from `.github/workflows/lint.yml`.

## 7. Build wiring

- **Source list:** `chrome/browser/ui/color/BUILD.gn` `sources` list (alongside `chrome_color_mixer.cc`, `chrome_color_mixers.cc`, `native_chrome_color_mixer.cc`, …) — adds `phlink_color_id.h`, `phlink_color_mixer.{cc,h}`, `phlink_palette.{cc,h}`.
- **Unit tests:** `chrome/test/BUILD.gn` `unit_tests` target — adds `chrome/browser/ui/color/phlink_color_contrast_unittests.cc`, `phlink_color_mixer_unittests.cc`, `chrome/browser/themes/phlink_appearance_observer_unittests.cc`.
- **Pref registration:** wherever phlink already calls `RegisterIntegerPref` for adblock prefs (Phase 5). Discovery during 08-04 — likely `chrome/browser/profiles/profile_prefs.cc` or a phlink-specific `profile_prefs_phlink.cc`.

## 8. Patch-slot allocation (mirror of D-09)

| Plan | Patch slot | Subject |
| ---- | ---------- | ------- |
| 08-01b | 0110 | Add `kColorPhlink*` IDs, `phlink_color_mixer.{cc,h}`, `phlink_palette.{cc,h}` skeleton; register in `chrome_color_mixers.cc` |
| 08-02  | 0111 | Light theme palette values + Light branch in mixer + Light pair tables |
| 08-03  | 0112 | Dark theme palette values + Dark branch in mixer + Dark pair tables |
| 08-04  | 0113 | `prefs::kPhlinkAppearanceMode` + `phlink_appearance_observer.{cc,h}` + appearance_page WebUI radio row |
| 08-05  | 0114 | `phlink_color_contrast_unittests.cc` + `scripts/contrast-audit.py` + `.github/workflows/lint.yml` step |

Slots 0115–0119 reserved as buffer per D-09.

## 9. Hot-path / performance check

Theme change is user-driven, ≪1/min (D-11). Mixer is invoked once per `ColorProvider` construction; ColorProvider is itself cached. **No phlink theme code may run per-frame, per-paint, or per-network-request.** Flagged here so reviewers reject any caching layer or per-`WebContents` work that creeps into 08-04's observer.

## 10. Risks discovered during research

1. **`E_CPONLY` macro hygiene** — `chrome_color_id.h` uses `kChromeColorsStart` as the seed for the *first* entry. Adding `PHLINK_COLOR_IDS` after `COMMON_CHROME_COLOR_IDS` must NOT re-seed (no second `kChromeColorsStart` arg) or all chrome IDs shift. Plan 08-01b must specify the macro append, not redefinition.
2. **`unit_tests` source list ordering** — `chrome/test/BUILD.gn` is alphabetised; new entries must land in the correct lexical slot to avoid noisy diffs / merge conflicts on rebases. Plan 08-01b / 08-05 should call this out.
3. **Linux gtk competition** — `chrome/browser/ui/color/linux/` contributes a Linux-specific mixer. Per CONTEXT §9 risk #2, **no plan in this phase touches Linux gtk** — defer to v1.0. 08-01b's mixer registration is platform-agnostic; on Linux the gtk mixer keeps last word for now.
4. **Pref roaming** — `kPhlinkAppearanceMode` is a profile pref, not a local-state pref. Confirms behaviour roams cleanly into Phase 9 (profile portability) without extra work.
