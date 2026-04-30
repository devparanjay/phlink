---
phase: 08-appearance-subsystem
plan: 01b
type: execute
wave: 1
depends_on: []
files_modified:
  - chrome/browser/ui/color/phlink_color_id.h
  - chrome/browser/ui/color/phlink_color_mixer.h
  - chrome/browser/ui/color/phlink_color_mixer.cc
  - chrome/browser/ui/color/phlink_palette.h
  - chrome/browser/ui/color/phlink_palette.cc
  - chrome/browser/ui/color/chrome_color_id.h
  - chrome/browser/ui/color/chrome_color_mixers.cc
  - chrome/browser/ui/color/BUILD.gn
  - chrome/test/BUILD.gn
  - chrome/browser/ui/color/phlink_color_mixer_unittests.cc
  - patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch
autonomous: true
requirements:
  - APPR-01
patch_slot: "0110"
must_haves:
  truths:
    - "A phlink color mixer is registered after Native and before custom_theme in chrome_color_mixers.cc."
    - "The 11 kColorPhlink* role token IDs (D-08) are defined and grep-able under //chrome/browser/ui/color/."
    - "Both Light and Dark palette tables exist as extern arrays (values may be placeholder zeros at this stage — 08-02/08-03 fill them) so the mixer compiles cleanly."
    - "phlink_color_mixer_unittests.cc exists, compiles, and passes (smoke: AddPhlinkColorMixer is callable for both ColorModes without DCHECK)."
    - "The change ships as patch 0110 and applies cleanly on the current chromium-src tree."
  artifacts:
    - path: chrome/browser/ui/color/phlink_color_id.h
      provides: PHLINK_COLOR_IDS macro with 11 E_CPONLY entries
      contains: "PHLINK_COLOR_IDS"
    - path: chrome/browser/ui/color/phlink_color_mixer.cc
      provides: AddPhlinkColorMixer(ColorProvider*, ColorProviderKey&) impl
      contains: "void AddPhlinkColorMixer"
    - path: chrome/browser/ui/color/phlink_palette.h
      provides: extern declarations for kPhlinkLight*/kPhlinkDark* SkColor arrays + contrast pair tables
      contains: "kPhlinkLight"
    - path: chrome/browser/ui/color/phlink_palette.cc
      provides: definitions of palette arrays (zero-filled placeholders for 08-02/08-03)
      contains: "kPhlinkLight"
    - path: patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch
      provides: applied patch capturing the above
      contains: "phlink_color_mixer"
  key_links:
    - from: chrome/browser/ui/color/chrome_color_mixers.cc
      to: chrome/browser/ui/color/phlink_color_mixer.h
      via: AddPhlinkColorMixer call site between AddNativeChromeColorMixer and key.custom_theme block
      pattern: "AddPhlinkColorMixer\\(provider, key\\);"
    - from: chrome/browser/ui/color/chrome_color_id.h
      to: chrome/browser/ui/color/phlink_color_id.h
      via: "#include + PHLINK_COLOR_IDS appended into the chrome color id map"
      pattern: "PHLINK_COLOR_IDS"
    - from: chrome/browser/ui/color/BUILD.gn
      to: phlink_color_mixer.cc, phlink_palette.cc
      via: sources list addition
      pattern: "phlink_color_mixer\\.cc"
    - from: chrome/test/BUILD.gn
      to: phlink_color_mixer_unittests.cc
      via: unit_tests sources list
      pattern: "phlink_color_mixer_unittests\\.cc"
---

<objective>
Lay the type-safe foundation for the phlink appearance subsystem. After this plan: phlink owns 11 `kColorPhlink*` role token IDs (per D-08), a `phlink_color_mixer` is wired into Chromium's `AddChromeColorMixers` registration in the slot defined by D-02, and a smoke unittest proves both Light and Dark code paths reach the mixer. **Concrete hex values are intentionally NOT in this plan** — they ship in 08-02 (Light) and 08-03 (Dark) so each theme is one atomic, reviewable patch.

Purpose: De-risk the integration surface (mixer registration order, ID-map participation, BUILD.gn wiring) before touching brand colors. Per CONTEXT D-09, this is patch slot 0110.
Output: 5 new source files, 4 edited files, 1 patch (0110), 1 unittest, all committed in `chromium-src` on branch `phlink-wip` and refreshed into `patches/`.
</objective>

<execution_context>
@.github/get-shit-done/workflows/execute-plan.md
@.github/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/08-appearance-subsystem/08-CONTEXT.md
@.planning/phases/08-appearance-subsystem/08-RESEARCH.md
@.planning/phases/08-appearance-subsystem/08-PATTERNS.md
@docs/dev/phase-08-scoping.md
@docs/dev/architecture.md

<interfaces>
<!-- Key upstream contracts. Executor uses these directly — no codebase exploration needed. -->

From `ui/color/color_provider_key.h` (lines 28–31):
```cpp
namespace ui {
struct ColorProviderKey {
  enum class ColorMode { kLight, kDark };
  enum class ContrastMode { kNormal, kHigh };
  ColorMode color_mode;
  // ... (other fields not used by phlink)
};
}  // namespace ui
```

From `chrome/browser/ui/color/chrome_color_mixers.cc` `AddChromeColorMixers()` body — insertion point:
```cpp
  // ... (existing chrome + material mixers above)
  // Must be the last one in order to override other mixer colors.
  AddNativeChromeColorMixer(provider, key);

  // <<< INSERT: AddPhlinkColorMixer(provider, key); >>>

  if (key.custom_theme) {
    key.custom_theme->AddColorMixers(provider, key);
  }
```

From `chrome/browser/ui/color/chrome_color_id.h` macro pattern:
```cpp
#define COMMON_CHROME_COLOR_IDS \
  E_CPONLY(kColorAppMenuHighlightSeverityLow, kChromeColorsStart, kChromeColorsStart) \
  E_CPONLY(kColorAppMenuHighlightSeverityHigh) \
  /* ... many more ... */
```
**`PHLINK_COLOR_IDS` MUST append, not re-seed.** Do NOT pass `kChromeColorsStart` — let the IDs continue numbering from the last `COMMON_CHROME_COLOR_IDS` entry.

From `ui/color/color_mixer.h`:
```cpp
namespace ui {
class ColorMixer {
 public:
  ColorRecipe& operator[](ColorId id);
};
}  // namespace ui
```
Set a recipe with `mixer[kColorPhlinkX] = {SkColorSetRGB(0xRR, 0xGG, 0xBB)};`.
</interfaces>
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Define kColorPhlink* IDs and palette skeletons</name>
  <files>
    chrome/browser/ui/color/phlink_color_id.h,
    chrome/browser/ui/color/phlink_palette.h,
    chrome/browser/ui/color/phlink_palette.cc,
    chrome/browser/ui/color/chrome_color_id.h
  </files>
  <behavior>
    - Test 1: `phlink_color_id.h` defines `PHLINK_COLOR_IDS` containing exactly 11 `E_CPONLY(kColorPhlink…)` entries: Canvas, Surface, SurfaceAlt, Card, Text, TextMuted, Hairline, Accent, OnAccent, Danger, Success (per D-08).
    - Test 2: `chrome_color_id.h` invokes `PHLINK_COLOR_IDS` *after* `COMMON_CHROME_COLOR_IDS` so all phlink IDs participate in the chrome color id map (verifiable via `grep -n PHLINK_COLOR_IDS chrome/browser/ui/color/chrome_color_id.h`).
    - Test 3: `phlink_palette.h` declares `extern constexpr SkColor kPhlinkLight[kPhlinkPaletteSize]` and `kPhlinkDark[kPhlinkPaletteSize]` (or equivalent fixed-size arrays) plus `extern const std::array<std::pair<ui::ColorId, ui::ColorId>, N> kPhlinkContrastNormalText` and `kPhlinkContrastNonText` (sizes filled by 08-05; can be `0` at this stage, but symbol must exist).
    - Test 4: `phlink_palette.cc` zero-fills the palette arrays and contrast tables. Compiles cleanly.
  </behavior>
  <action>
    Create `phlink_color_id.h` (per D-01) with:
    ```cpp
    #ifndef CHROME_BROWSER_UI_COLOR_PHLINK_COLOR_ID_H_
    #define CHROME_BROWSER_UI_COLOR_PHLINK_COLOR_ID_H_

    #include "components/color/color_id.h"
    #include "ui/color/color_id.h"

    // clang-format off
    #define PHLINK_COLOR_IDS \
      E_CPONLY(kColorPhlinkCanvas) \
      E_CPONLY(kColorPhlinkSurface) \
      E_CPONLY(kColorPhlinkSurfaceAlt) \
      E_CPONLY(kColorPhlinkCard) \
      E_CPONLY(kColorPhlinkText) \
      E_CPONLY(kColorPhlinkTextMuted) \
      E_CPONLY(kColorPhlinkHairline) \
      E_CPONLY(kColorPhlinkAccent) \
      E_CPONLY(kColorPhlinkOnAccent) \
      E_CPONLY(kColorPhlinkDanger) \
      E_CPONLY(kColorPhlinkSuccess)
    // clang-format on

    #endif  // CHROME_BROWSER_UI_COLOR_PHLINK_COLOR_ID_H_
    ```
    Edit `chrome/browser/ui/color/chrome_color_id.h`: add `#include "chrome/browser/ui/color/phlink_color_id.h"` at the top of the includes. After the `COMMON_CHROME_COLOR_IDS` macro definition closes, add a sibling `#define CHROME_COLOR_IDS COMMON_CHROME_COLOR_IDS PHLINK_COLOR_IDS` (or, if the existing convention already uses one umbrella macro, append `PHLINK_COLOR_IDS` to it). **Critical: do NOT pass `kChromeColorsStart` to PHLINK_COLOR_IDS' first entry — the numbering continues from the previous block.** Verify any existing call sites that consume `COMMON_CHROME_COLOR_IDS` are switched to the new umbrella name OR keep both — pick whichever is the smaller diff.
    Create `phlink_palette.h` declaring:
    - `inline constexpr size_t kPhlinkPaletteSize = 11;`
    - `extern const SkColor kPhlinkLight[kPhlinkPaletteSize];` and `kPhlinkDark[kPhlinkPaletteSize];`
    - Index aliases: `enum PhlinkToken { kCanvas = 0, kSurface, kSurfaceAlt, kCard, kText, kTextMuted, kHairline, kAccent, kOnAccent, kDanger, kSuccess };`
    - Forward decls for the contrast pair tables (08-05 fills sizes/contents).
    Create `phlink_palette.cc` with both arrays zero-filled (`SkColorSetRGB(0,0,0)` placeholders). Add a TODO comment per array citing "filled by patch 0111 (Light) / 0112 (Dark) per CONTEXT D-08."
    File the change in patches/0110-…patch via the standard `scripts/refresh-patches.py` flow at end of plan (Task 3). Per D-09 use slot 0110.
  </action>
  <verify>
    <automated>cd /Volumes/Tools/dev/chromium-src/src &amp;&amp; grep -c "E_CPONLY(kColorPhlink" chrome/browser/ui/color/phlink_color_id.h | grep -qx 11 &amp;&amp; grep -q "PHLINK_COLOR_IDS" chrome/browser/ui/color/chrome_color_id.h &amp;&amp; grep -q "kPhlinkLight" chrome/browser/ui/color/phlink_palette.h</automated>
  </verify>
  <done>11 IDs declared; chrome_color_id.h includes phlink_color_id.h and folds PHLINK_COLOR_IDS into the umbrella macro; palette skeletons compile.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Implement phlink_color_mixer.{cc,h} and register it in chrome_color_mixers.cc</name>
  <files>
    chrome/browser/ui/color/phlink_color_mixer.h,
    chrome/browser/ui/color/phlink_color_mixer.cc,
    chrome/browser/ui/color/chrome_color_mixers.cc,
    chrome/browser/ui/color/BUILD.gn,
    chrome/browser/ui/color/phlink_color_mixer_unittests.cc,
    chrome/test/BUILD.gn
  </files>
  <behavior>
    - Test 1: `AddPhlinkColorMixer(provider, key)` is invoked from `AddChromeColorMixers` between `AddNativeChromeColorMixer(provider, key);` and the `if (key.custom_theme)` block (per D-02).
    - Test 2: For both `ColorMode::kLight` and `ColorMode::kDark`, `AddPhlinkColorMixer` adds a mixer that maps each of the 11 `kColorPhlink*` IDs to a recipe pulling from `kPhlinkLight[i]` or `kPhlinkDark[i]` respectively. (Values are still placeholder zeros — Light = 0x000000, Dark = 0x000000 — until 08-02/08-03; the test only asserts the IDs are bound, not their hex.)
    - Test 3: Build target `phlink_color_mixer_unittests` compiles and passes; both ColorModes resolve every kColorPhlink* without DCHECK.
  </behavior>
  <action>
    Create `phlink_color_mixer.h`:
    ```cpp
    #ifndef CHROME_BROWSER_UI_COLOR_PHLINK_COLOR_MIXER_H_
    #define CHROME_BROWSER_UI_COLOR_PHLINK_COLOR_MIXER_H_

    namespace ui { class ColorProvider; struct ColorProviderKey; }

    void AddPhlinkColorMixer(ui::ColorProvider* provider,
                             const ui::ColorProviderKey& key);

    #endif
    ```
    Create `phlink_color_mixer.cc` with:
    ```cpp
    #include "chrome/browser/ui/color/phlink_color_mixer.h"

    #include "chrome/browser/ui/color/phlink_color_id.h"
    #include "chrome/browser/ui/color/phlink_palette.h"
    #include "ui/color/color_mixer.h"
    #include "ui/color/color_provider.h"
    #include "ui/color/color_provider_key.h"
    #include "ui/color/color_recipe.h"

    void AddPhlinkColorMixer(ui::ColorProvider* provider,
                             const ui::ColorProviderKey& key) {
      const bool dark = key.color_mode == ui::ColorProviderKey::ColorMode::kDark;
      const SkColor* p = dark ? kPhlinkDark : kPhlinkLight;
      ui::ColorMixer&amp; mixer = provider->AddMixer();
      mixer[kColorPhlinkCanvas]     = {p[kCanvas]};
      mixer[kColorPhlinkSurface]    = {p[kSurface]};
      mixer[kColorPhlinkSurfaceAlt] = {p[kSurfaceAlt]};
      mixer[kColorPhlinkCard]       = {p[kCard]};
      mixer[kColorPhlinkText]       = {p[kText]};
      mixer[kColorPhlinkTextMuted]  = {p[kTextMuted]};
      mixer[kColorPhlinkHairline]   = {p[kHairline]};
      mixer[kColorPhlinkAccent]     = {p[kAccent]};
      mixer[kColorPhlinkOnAccent]   = {p[kOnAccent]};
      mixer[kColorPhlinkDanger]     = {p[kDanger]};
      mixer[kColorPhlinkSuccess]    = {p[kSuccess]};
    }
    ```
    Edit `chrome/browser/ui/color/chrome_color_mixers.cc`: add `#include "chrome/browser/ui/color/phlink_color_mixer.h"` (alphabetised). In `AddChromeColorMixers`, insert `AddPhlinkColorMixer(provider, key);` immediately after `AddNativeChromeColorMixer(provider, key);` and before the `if (key.custom_theme)` block (per D-02). Leave the existing comment "Must be the last one in order to override other mixer colors." in place — phlink intentionally violates it; add a one-line comment above the new call: `// phlink: brand-identity overrides; user custom_theme below still wins.`
    Edit `chrome/browser/ui/color/BUILD.gn`: append `phlink_color_id.h`, `phlink_color_mixer.cc`, `phlink_color_mixer.h`, `phlink_palette.cc`, `phlink_palette.h` to the alphabetised `sources` list in the existing `static_library` target.
    Create `phlink_color_mixer_unittests.cc` (per D-12) with a parametrised test over `{ColorMode::kLight, ColorMode::kDark}`:
    - Build a `ui::ColorProvider`, set key.color_mode, call `AddPhlinkColorMixer`.
    - For each of the 11 IDs, assert the resolved color is not `gfx::kPlaceholderColor`.
    - Assert calling twice in a row is idempotent (no DCHECK on duplicate mixer registration).
    Edit `chrome/test/BUILD.gn` `unit_tests` target: append `chrome/browser/ui/color/phlink_color_mixer_unittests.cc` (alphabetised — slot it just below the existing `chrome_color_mixer_unittest.cc` entry if present).
  </action>
  <verify>
    <automated>cd /Volumes/Tools/dev/chromium-src/src &amp;&amp; export PATH="$HOME/depot_tools:/opt/homebrew/bin:$PATH" &amp;&amp; caffeinate -is autoninja -j 8 -C out/Default chrome unit_tests &amp;&amp; out/Default/unit_tests --gtest_filter='Phlink*' 2>&amp;1 | tail -5 | grep -q "PASSED"</automated>
  </verify>
  <done>chrome and unit_tests build clean; PhlinkColorMixerTest passes for both ColorModes.</done>
</task>

<task type="auto">
  <name>Task 3: Refresh patches and produce 0110 patch file</name>
  <files>patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch</files>
  <action>
    From `/Volumes/Tools/dev/phlink`, run `python3 scripts/refresh-patches.py --slot 0110 --subject "phlink: phase 08-01b color mixer foundation (kColorPhlink* IDs + AddPhlinkColorMixer registration)"` (or equivalent existing flow — fall back to `git format-patch -1 --start-number 110 -o patches/` from chromium-src `phlink-wip` HEAD if the helper script doesn't support `--slot`). Resulting patch must be a single commit covering all chromium-src changes in tasks 1+2. Verify it applies cleanly on a fresh tree via `python3 scripts/apply-patches.py --dry-run`.
    Commit message body must reference D-01, D-02, D-09, and the 11 token names from D-08.
  </action>
  <verify>
    <automated>cd /Volumes/Tools/dev/phlink &amp;&amp; ls patches/0110-*.patch &amp;&amp; python3 scripts/apply-patches.py --dry-run 2>&amp;1 | tail -3 | grep -qi "ok\|clean\|success"</automated>
  </verify>
  <done>patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch exists and dry-run-applies cleanly.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| renderer → browser process | Phase 8 work is browser-process only; no new IPC surface. |
| pref store → mixer | (Wired in 08-04, not here.) Pref change must not allow arbitrary SkColor injection. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-08-01b-01 | Tampering | `phlink_palette.cc` literals | accept | All hex values are compile-time `constexpr SkColor`. No runtime mutation path. Tampering requires source-tree write access. |
| T-08-01b-02 | Information Disclosure | telemetry on theme switch | mitigate | This plan adds NO instrumentation. Reviewers reject any UMA/UKM macro in `phlink_color_mixer*.cc` (per CONTEXT §5 carry-forward from Phase 6). |
| T-08-01b-03 | Elevation of Privilege | mixer registration order leaks brand colors into `custom_theme` paths | accept | `key.custom_theme` block runs *after* phlink mixer; user themes always win — confirmed by D-02 ordering. |
</threat_model>

<verification>
- `git -C /Volumes/Tools/dev/chromium-src/src grep -n "AddPhlinkColorMixer(provider, key);" chrome/browser/ui/color/chrome_color_mixers.cc` → exactly 1 match between `AddNativeChromeColorMixer(provider, key);` and `if (key.custom_theme)`.
- `grep -v '^#' chrome/browser/ui/color/phlink_color_id.h | grep -c E_CPONLY` → 11.
- `out/Default/unit_tests --gtest_filter='Phlink*'` → all green.
- `patches/0110-…patch` applies clean.
- No new pref / observer / WebUI changes (those are 08-04).
</verification>

<success_criteria>
1. The phlink mixer is callable, registered, and resolves all 11 `kColorPhlink*` IDs to non-placeholder colors for both Light and Dark modes (placeholder zeros are still "non-placeholder" for the assertion — they're real SkColors with α=0xFF; 08-02/08-03 will overwrite them with the brand hex).
2. Patch 0110 ships and applies cleanly.
3. `unit_tests --gtest_filter='Phlink*'` passes locally.
4. No file outside `chrome/browser/ui/color/`, `chrome/test/BUILD.gn`, and `patches/` is touched.
</success_criteria>

<output>
After completion, create `.planning/phases/08-appearance-subsystem/08-01b-SUMMARY.md` recording: actual lines/files modified, any deviation from this plan, the resolved patch slot (0110), the unit test count delta, and the diff of `chrome_color_mixers.cc` showing the insertion site.
</output>
