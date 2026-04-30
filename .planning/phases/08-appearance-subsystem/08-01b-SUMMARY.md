---
phase: 08-appearance-subsystem
plan: 01b
type: execute
status: complete
wave: 1
patch_slot: "0110"
requirements_landed:
  - APPR-01
chromium_src_commit: d8e5afd3b531
phlink_commit: 18ba332
patch_file: patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch
tasks_completed: 3
files_created:
  - chromium-src://chrome/browser/ui/color/phlink_color_id.h
  - chromium-src://chrome/browser/ui/color/phlink_color_mixer.h
  - chromium-src://chrome/browser/ui/color/phlink_color_mixer.cc
  - chromium-src://chrome/browser/ui/color/phlink_palette.h
  - chromium-src://chrome/browser/ui/color/phlink_palette.cc
  - chromium-src://chrome/browser/ui/color/phlink_color_mixer_unittests.cc
  - patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch
files_modified:
  - chromium-src://chrome/browser/ui/color/chrome_color_id.h
  - chromium-src://chrome/browser/ui/color/chrome_color_mixers.cc
  - chromium-src://chrome/browser/ui/color/BUILD.gn
  - chromium-src://chrome/test/BUILD.gn
metrics:
  unit_tests_added: 4
  unit_tests_passing: 4
---

# Phase 8 Plan 01b: Color Mixer Foundation Summary

Type-safe foundation for phlink's appearance subsystem landed: 11 `kColorPhlink*` role-token IDs plus a registered `AddPhlinkColorMixer` slot between `AddNativeChromeColorMixer` and the `key.custom_theme` block (CONTEXT D-02). Palette tables ship zero-filled; 08-02 (Light) and 08-03 (Dark) will fill them in their own atomic patches.

## Tasks completed

1. **Task 1 — IDs + palette skeleton.** Added `phlink_color_id.h` with `PHLINK_COLOR_IDS` macro (11 `E_CPONLY` entries — Canvas, Surface, SurfaceAlt, Card, Text, TextMuted, Hairline, Accent, OnAccent, Danger, Success). Wired into `chrome_color_id.h` umbrella as `CHROME_COLOR_IDS = COMMON_CHROME_COLOR_IDS CHROME_PLATFORM_SPECIFIC_COLOR_IDS PHLINK_COLOR_IDS` — no `kChromeColorsStart` re-seed. Created `phlink_palette.{cc,h}` declaring `kPhlinkLight[11]` / `kPhlinkDark[11]` zero-filled and zero-sized contrast pair tables.
2. **Task 2 — Mixer + registration + tests.** Added `phlink_color_mixer.{cc,h}` exporting `AddPhlinkColorMixer(provider, key)` that branches on `key.color_mode == kDark` and binds each ID to its palette slot. Registered the call in `AddChromeColorMixers` immediately after `AddNativeChromeColorMixer` and before the `key.custom_theme` block, with a one-line comment justifying the override. Added `phlink_color_mixer_unittests.cc` (parametrised over both `ColorMode`s, two tests: `ResolvesAllPhlinkIds`, `IdempotentRegistration`). Wired the new sources into `chrome/browser/ui/color/BUILD.gn` and the unittest into `chrome/test/BUILD.gn` (alphabetical insertion right after `new_tab_page_color_mixer_unittest.cc`).
3. **Task 3 — Patch export.** Used `git format-patch -1 HEAD` from chromium-src and placed the result manually into slot `patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch`. See deviation note below — the project-supplied `scripts/refresh-patches.py` is incompatible with the gap-based slot scheme this plan relies on.

## Verification

* `autoninja -C out/Default chrome unit_tests` → both targets built clean (`Build Succeeded: 4524 steps` for the chrome+unit_tests combo, then a 2-step incremental for the unittest pickup after a `touch chrome/test/BUILD.gn` to defeat siso's stale BUILD.gn dep cache).
* `out/Default/unit_tests --gtest_filter='*Phlink*'` → **4 tests, all PASSED** (`Modes/PhlinkColorMixerTest.ResolvesAllPhlinkIds/{0,1}`, `…IdempotentRegistration/{0,1}`).
* `grep -c E_CPONLY chrome/browser/ui/color/phlink_color_id.h` = 11. ✓
* `grep -n "AddPhlinkColorMixer(provider, key);" chrome/browser/ui/color/chrome_color_mixers.cc` = exactly one call between `AddNativeChromeColorMixer(provider, key);` and `if (key.custom_theme)`. ✓

## Deviations from plan

1. **Patch slot tooling.** The plan's Task 3 prescribes `python3 scripts/refresh-patches.py`. That tool wholesale renumbers every patch in `patches/` from 0001 sequentially and does not honour CONTEXT D-09's gap-based slot scheme (e.g., the existing `0090..0102` range with reserved `0110+` block for phase 8). Running it once would have collapsed the prior layout to `0001..0026` and produced a 433k-line diff. I reverted the bulk renumber via `git checkout -- patches/` + `rm` of the leftover `0013..0025` files, then exported the new patch with `git format-patch -1 HEAD --stdout` from chromium-src and saved it directly as `patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch`. **Follow-up needed:** either (a) teach `scripts/refresh-patches.py` to preserve the slot layout (e.g., a `--slot N` mode that exports a single HEAD commit), or (b) document manual `git format-patch -1` as the canonical "single new commit" export path and reserve `refresh-patches.py` for full rebases.
2. **`provider.GenerateColorMap()` API.** The plan implied a public `GenerateColorMap()` on `ui::ColorProvider`; the actual API in `ui/color/color_provider.h` is `GenerateColorMapForTesting()`. Used the testing variant — appropriate for a unittest.
3. **`ColorProvider` construction in test.** `ui::ColorProvider` is default-constructible (no `ColorProviderKey` argument needed) — matches the upstream `new_tab_page_color_mixer_unittest.cc` pattern, so no behavior delta.
4. **Build cache surprise (siso).** First combined `chrome unit_tests` build did not pick up the new `phlink_color_mixer_unittests.cc` source listed in `chrome/test/BUILD.gn` despite siso reporting `Regenerating ninja files`. A subsequent `touch chrome/test/BUILD.gn` + rebuild compiled `phlink_color_mixer_unittests.o` and relinked `unit_tests` cleanly. Documented here in case the same hiccup hits 08-04/08-05.
5. **Submodule-pointer noise.** `git status` on chromium-src persistently shows `M third_party/search_engines_data/resources` (per project standing rules) — was NOT staged into the phlink phase-08-01b commit. Only the 10 phlink files were staged.

## Insertion site (for reviewers)

Excerpt from `chrome/browser/ui/color/chrome_color_mixers.cc`:

```diff
   // Must be the last one in order to override other mixer colors.
   AddNativeChromeColorMixer(provider, key);

+  // phlink: brand-identity overrides; user custom_theme below still wins.
+  AddPhlinkColorMixer(provider, key);
+
   if (key.custom_theme) {
     key.custom_theme->AddColorMixers(provider, key);
   }
```

## Self-Check: PASSED

* `chrome/browser/ui/color/phlink_color_id.h` → FOUND
* `chrome/browser/ui/color/phlink_color_mixer.cc` → FOUND
* `chrome/browser/ui/color/phlink_color_mixer.h` → FOUND
* `chrome/browser/ui/color/phlink_color_mixer_unittests.cc` → FOUND
* `chrome/browser/ui/color/phlink_palette.cc` → FOUND
* `chrome/browser/ui/color/phlink_palette.h` → FOUND
* `patches/0110-phlink-phase-08-01b-color-mixer-foundation.patch` → FOUND
* chromium-src commit `d8e5afd3b531` → FOUND on `phlink-wip`
* phlink commit `18ba332` → FOUND on `dev-0.1`
* Unit tests `Modes/PhlinkColorMixerTest.*` → 4/4 PASSED
