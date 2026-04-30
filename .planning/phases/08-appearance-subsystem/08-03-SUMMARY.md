---
phase: 08-appearance-subsystem
plan: 03
type: execute
status: complete
wave: 3
patch_slot: "0112"
requirements_landed:
  - APPR-03
chromium_src_commit: a52dd015b85e
phlink_commit: 47e702c
patch_file: patches/0112-phlink-phase-08-03-default-dark-theme.patch
tasks_completed: 3
files_modified:
  - chromium-src://chrome/browser/ui/color/phlink_palette.cc
  - chromium-src://chrome/browser/ui/color/phlink_color_mixer_unittests.cc
metrics:
  unit_tests_added: 2
  unit_tests_passing: 7  # 5 from 08-02 + LockedDarkHex + OnAccent_DarkIsBlack_NeverWhite
  diff_stat: "2 files changed, 71 insertions(+), 12 deletions(-)"
---

# Phase 8 Plan 03: Default Dark Theme Summary

Populated `kPhlinkDark[kPhlinkPaletteSize]` in `chrome/browser/ui/color/phlink_palette.cc` with the eleven LOCKED hex literals from CONTEXT D-08 / `.planning/sketches/phase-08/stitch-output.md §2.2`. Added two unit tests: a per-token `PhlinkColorMixerDarkTest.LockedDarkHex` (mirrors 08-02's `LockedHex` for Dark mode) and a dedicated `PhlinkColorMixerDarkTest.OnAccent_DarkIsBlack_NeverWhite` invariant test that explicitly asserts the foreground color on the pastel-yellow accent is `SK_ColorBLACK` and `!= SK_ColorWHITE`.

## Tasks completed

1. **Task 1 — Populate kPhlinkDark[].** Replaced the eleven `0x000000` placeholder rows with `SkColorSetRGB(...)` literals matching D-08 §Dark verbatim (Canvas #0D0D0D, Surface #181818, SurfaceAlt #1F1F1F, Card #1F1F1F, Text #FFFFFF, TextMuted #A0A0A0, Hairline #2A2A2A, Accent #F5E68A, OnAccent #000000, Danger #F5736B, Success #6FE38A). Replaced the `TODO(phlink): filled by patch 0112` comment with a 4-line citation block tying the file back to D-08, calling out the WCAG 16:1 invariant for `kOnAccent`, and prohibiting future drift to white without re-running stitch validation.
2. **Task 2 — Dark hex assertions + named never-white invariant.** Appended two `TEST(...)` bodies to `phlink_color_mixer_unittests.cc`:
   - `PhlinkColorMixerDarkTest.LockedDarkHex` — 11 explicit `EXPECT_EQ(provider.GetColor(...), SkColorSetRGB(...))` lines, one per token, parallel to the Light version.
   - `PhlinkColorMixerDarkTest.OnAccent_DarkIsBlack_NeverWhite` — three assertions on `provider.GetColor(kColorPhlinkOnAccent)`: `EXPECT_EQ(SkColorSetRGB(0x00,0x00,0x00))`, `EXPECT_EQ(SK_ColorBLACK)`, and `EXPECT_NE(SK_ColorWHITE)`, each with a failure message naming the §2.2 critical rule and the 1.3:1 vs 16:1 contrast figures.
3. **Task 3 — Patch export.** Used `git format-patch -1 HEAD --stdout > patches/0112-…patch` (per the 08-01b/08-02 standing learning — `refresh-patches.py` would renumber every patch from 0001). Verified clean apply via `git reset --hard HEAD~1 && git apply --check patches/0112-…patch` (`CLEAN_APPLY_OK`), then re-applied via `git am` and re-exported so the `From <sha>` header matches the final HEAD `a52dd015b85e`.

## Verification

* `autoninja -C out/Default unit_tests` → `Build Succeeded: 5 steps` (incremental: 1 TU recompile + relink, 1m45s).
* `autoninja -C out/Default chrome` → `Build Succeeded: 3 steps` (incremental, 14s — palette TU only).
* `out/Default/unit_tests --gtest_filter='*Phlink*'` → **7/7 PASSED**:
  * `PhlinkColorMixerLightTest.LockedHex` ✓ (unchanged from 08-02)
  * `PhlinkColorMixerDarkTest.LockedDarkHex` ✓ (new — 11 EXPECT_EQ)
  * `PhlinkColorMixerDarkTest.OnAccent_DarkIsBlack_NeverWhite` ✓ (new — named invariant gate)
  * `Modes/PhlinkColorMixerTest.ResolvesAllPhlinkIds/{0,1}` ✓ (unchanged from 08-01b)
  * `Modes/PhlinkColorMixerTest.IdempotentRegistration/{0,1}` ✓ (unchanged from 08-01b)
* `git apply --check patches/0112-…patch` against `HEAD~1` → `CLEAN_APPLY_OK`.
* Patch `From` header SHA `a52dd015b85e976b995fbcaf8bd70f66ff3d33fe` matches chromium-src `phlink-wip` HEAD.

## Hex table actually written (kPhlinkDark)

| Idx | Token       | Hex      | SkColorSetRGB                |
| --- | ----------- | -------- | ---------------------------- |
| 0   | kCanvas     | #0D0D0D  | `0x0D, 0x0D, 0x0D`           |
| 1   | kSurface    | #181818  | `0x18, 0x18, 0x18`           |
| 2   | kSurfaceAlt | #1F1F1F  | `0x1F, 0x1F, 0x1F`           |
| 3   | kCard       | #1F1F1F  | `0x1F, 0x1F, 0x1F`           |
| 4   | kText       | #FFFFFF  | `0xFF, 0xFF, 0xFF`           |
| 5   | kTextMuted  | #A0A0A0  | `0xA0, 0xA0, 0xA0`           |
| 6   | kHairline   | #2A2A2A  | `0x2A, 0x2A, 0x2A`           |
| 7   | kAccent     | #F5E68A  | `0xF5, 0xE6, 0x8A`           |
| 8   | kOnAccent   | **#000000** | **`0x00, 0x00, 0x00`** ← never white |
| 9   | kDanger     | #F5736B  | `0xF5, 0x73, 0x6B`           |
| 10  | kSuccess    | #6FE38A  | `0x6F, 0xE3, 0x8A`           |

## Deviations from plan

1. **Patch tooling — same as 08-01b / 08-02.** Plan Task 3 prescribed `python3 scripts/refresh-patches.py --slot 0112`. That tool still renumbers every patch from 0001 and would collapse the gap-based slot layout (0090–0102 / 0110–0111). Used `git format-patch -1 HEAD --stdout` per the standing workaround. Follow-up still open: teach `scripts/refresh-patches.py` a `--slot N` single-commit-export mode.
2. **`apply-patches.py --dry-run` does not run `git apply --check`.** Same 08-02 deviation: it only prints `would apply N patch(es)` and exits 0. Replaced the plan's `apply-patches.py --dry-run | grep -qi "ok|clean|success"` verifier with a real `git reset --hard HEAD~1 && git apply --check` round-trip, which confirmed clean apply.
3. **Submodule pointer noise.** `git status` shows `M third_party/search_engines_data/resources` — not staged into the phase-08-03 commit. Benign per project standing rules.
4. **Test fixture name uses `PhlinkColorMixerDarkTest`** (the plan suggested `PhlinkColorMixerDarkTest.OnAccentIsBlackNotWhite` "or whatever the plan specifies"; the plan §Task 2 specified `OnAccent_DarkIsBlack_NeverWhite`). Used the plan's exact name.

## Threat-mitigation check (per plan threat_model)

| Threat        | Disposition | Status                                                                 |
| ------------- | ----------- | ---------------------------------------------------------------------- |
| T-08-03-01    | mitigate    | ✓ `OnAccent_DarkIsBlack_NeverWhite` test names the §2.2 rule and asserts both `EXPECT_EQ(SK_ColorBLACK)` and `EXPECT_NE(SK_ColorWHITE)`. |
| T-08-03-02    | mitigate    | ✓ Per-token `EXPECT_EQ` in `LockedDarkHex` test — drift fails CI.       |

## Self-Check: PASSED

* `chrome/browser/ui/color/phlink_palette.cc` modified, contains all 11 D-08 Dark hex literals → FOUND
* `chrome/browser/ui/color/phlink_color_mixer_unittests.cc` modified, contains both `LockedDarkHex` and `OnAccent_DarkIsBlack_NeverWhite` → FOUND
* `patches/0112-phlink-phase-08-03-default-dark-theme.patch` exists, applies clean against `HEAD~1` → FOUND
* chromium-src commit `a52dd015b85e` → FOUND on `phlink-wip`
* `PhlinkColorMixerDarkTest.LockedDarkHex` → PASSED (1 test, 11 assertions)
* `PhlinkColorMixerDarkTest.OnAccent_DarkIsBlack_NeverWhite` → PASSED (1 test, 3 assertions; never-white invariant)
* `PhlinkColorMixerLightTest.LockedHex` + 4 parametrised tests → 5/5 still PASSED
