# Phase 8 — PATTERNS (upstream analogs for each new file)

> For every new source artifact in plans 08-01b..08-05, the closest upstream-Chromium analog. Executors copy structure, not content.

| New file | Upstream analog | What to mimic |
| -------- | --------------- | ------------- |
| `chrome/browser/ui/color/phlink_color_id.h` | `chrome/browser/ui/color/chrome_color_id.h` (`COMMON_CHROME_COLOR_IDS` macro) | `E_CPONLY` macro list pattern; `#include "components/color/color_id.h"` + `"ui/color/color_id.h"`. Define `PHLINK_COLOR_IDS` as a single backslash-continued macro, **append** (do not re-seed) to the chrome map. |
| `chrome/browser/ui/color/phlink_color_mixer.h` | `chrome/browser/ui/color/chrome_color_mixer.h` | One forward decl + `void AddPhlinkColorMixer(ui::ColorProvider*, const ui::ColorProviderKey&);` |
| `chrome/browser/ui/color/phlink_color_mixer.cc` | `chrome/browser/ui/color/chrome_color_mixer.cc` (esp. `AddChromeColorMixer` body) | `ui::ColorMixer& mixer = provider->AddMixer();` then per-token `mixer[kColorPhlinkX] = {SkColorSetRGB(...)};`. Branch on `key.color_mode == ui::ColorProviderKey::ColorMode::kDark`. Defer the actual hex tables to `phlink_palette.cc` (08-02 / 08-03 fill them). |
| `chrome/browser/ui/color/phlink_palette.h` | `chrome/browser/ui/color/material_chrome_color_mixer.h` (declarations only) | Declare two `constexpr SkColor kPhlinkLight*[]` and `kPhlinkDark*[]` arrays + the contrast pair tables (`kPhlinkContrastNormalText`, `kPhlinkContrastNonText`). |
| `chrome/browser/ui/color/phlink_palette.cc` | `chrome/browser/ui/color/material_chrome_color_mixer.cc` (constexpr SkColor literals) | One `constexpr SkColor` per token per mode. Pair tables are `constexpr std::array<std::pair<ui::ColorId, ui::ColorId>, N>`. |
| `chrome/browser/ui/color/phlink_color_mixer_unittests.cc` | `chrome/browser/ui/color/chrome_color_mixer_unittest.cc` | TestColorProvider boilerplate; assert `provider.GetColor(kColorPhlinkAccent) != gfx::kPlaceholderColor` for both modes. |
| `chrome/browser/ui/color/phlink_color_contrast_unittests.cc` | `ui/color/color_utils_unittest.cc` (uses `GetContrastRatio`) + chrome_color_mixer_unittest.cc | Parametrised TEST_P over ColorMode; iterate both pair tables; `EXPECT_GE(GetContrastRatio(bg, fg), threshold)`. |
| `chrome/browser/themes/phlink_appearance_observer.{h,cc}` | `chrome/browser/themes/theme_service.{h,cc}` (`OnNativeThemeUpdated`, `PrefChangeRegistrar` setup) | KeyedService-or-Profile-owned singleton; `ui::NativeThemeObserver` impl; `PrefChangeRegistrar` for `kPhlinkAppearanceMode`; on change → `ColorProviderManager::Get().ResetColorProviderCache()` + iterate `BrowserList::GetInstance()`. |
| `chrome/browser/themes/phlink_appearance_observer_unittests.cc` | `chrome/browser/themes/theme_service_unittest.cc` | `ScopedTestingLocalState` + `TestingPrefServiceSimple` + a fake `ui::NativeTheme`. Assert pref flip and OS flip both invalidate. |
| Pref registration entry | Existing phlink adblock pref registration (Phase 5 — `chrome/browser/profiles/profile_prefs.cc` or sibling) | Single `registry->RegisterIntegerPref(prefs::kPhlinkAppearanceMode, 2);` (default = Follow System per D-06). |
| `chrome/browser/resources/settings/appearance_page/appearance_page.html` (edit) | Existing rows in same file, esp. the upstream "Theme" row | New `<settings-radio-group pref="{{prefs.phlink.appearance_mode}}">` block with three `<controlled-radio-button>` children. Inserted **above** the existing Theme/Color rows. |
| `chrome/browser/resources/settings/appearance_page/appearance_page.ts` (edit) | Same file (existing pref-bound radio handling) | Add `i18n` strings `phlinkThemeLight`, `phlinkThemeDark`, `phlinkThemeFollowSystem`; no new browser-proxy methods (pure pref binding). |
| `tests/e2e/appearance_test.ts` (new) | `tests/network-capture/` Playwright structure (Phase 6) | Spawn phlink, navigate to `chrome://settings/appearance`, click "Dark" radio, screenshot, assert contrast inversion via DOM-derived computed style. |
| `scripts/contrast-audit.py` | `scripts/license-audit.py` (Phase 11) | Same shape: argparse, single-file scan, exits non-zero with diagnostics. Standalone — no Chromium build needed. |
| `.github/workflows/lint.yml` (edit) | Existing `lint.yml` (license-audit step) | Add `- name: phlink contrast audit` step that runs `python3 scripts/contrast-audit.py patches/0111-*.patch patches/0112-*.patch` (or the in-tree palette file once patches apply). |

**Patch wrappers** (one per plan): copy the wrapper from the most recent applied phase patch, e.g. `patches/0102-phlink-phase-06-06-network-state-isolation.patch` — header format, slot number incremented to 0110/0111/0112/0113/0114.

## Cross-file invariants the executors must preserve

1. The `kColorPhlink*` IDs declared in `phlink_color_id.h` MUST equal the keys used in `phlink_color_mixer.cc` and the keys used in the contrast pair tables. A mismatch fails the mixer unittest at link time (undefined ID) — desirable; surfaces typos fast.
2. `phlink_palette.cc` is the **sole source of truth for hex literals**. `phlink_color_mixer.cc` references named constants from `phlink_palette.h`, never inline `SkColorSetRGB(...)` for token values. The contrast-audit Python script also reads only `phlink_palette.cc` — single-file regex.
3. Patch files must apply in slot order (0110 → 0114). 0110's mixer skeleton must declare both `kPhlinkLight*` and `kPhlinkDark*` arrays as `extern` so 0111/0112 can fill them without re-declaring.
