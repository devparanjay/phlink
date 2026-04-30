---
phase: 08-appearance-subsystem
plan: 02
type: execute
status: complete
wave: 2
patch_slot: "0111"
requirements_landed:
  - APPR-02
chromium_src_commit: 00e7f6c7fd32
phlink_commit: 879eba4
patch_file: patches/0111-phlink-phase-08-02-light-theme-palette.patch
tasks_completed: 3
files_modified:
  - chromium-src://chrome/browser/ui/color/phlink_palette.cc
  - chromium-src://chrome/browser/ui/color/phlink_color_mixer_unittests.cc
metrics:
  unit_tests_added: 1
  unit_tests_passing: 5  # 4 from 08-01b + new LockedHex
  diff_stat: "2 files changed, 45 insertions(+), 13 deletions(-)"
---

# Phase 8 Plan 02: Default Light Theme Summary

Populated `kPhlinkLight[kPhlinkPaletteSize]` in `chrome/browser/ui/color/phlink_palette.cc` with the eleven LOCKED hex literals from CONTEXT D-08 / `.planning/sketches/phase-08/stitch-output.md §2.1`. Added `PhlinkColorMixerLightTest.LockedHex` (one `EXPECT_EQ` per token) so any drift fails the unit-test suite. `kPhlinkDark[]` left zero-filled — 08-03 lands Dark in its own atomic patch.

## Tasks completed

1. **Task 1 — Populate kPhlinkLight[].** Replaced the 0x000000 placeholder block with eleven `SkColorSetRGB(...)` literals matching the D-08 Light table verbatim (Canvas #FFFFFF, Surface #F8F4EC, SurfaceAlt #F1EDE5, Card #FFFFFF, Text #1A1A1A, TextMuted #525252, Hairline #E5E0D6, Accent #A8C8E8, OnAccent #1A1A1A, Danger #C0392B, Success #2E8540). Replaced the `TODO: filled by patch 0111` comment with a citation: `// Locked by Phase 8 D-08; source: .planning/sketches/phase-08/stitch-output.md §2.1.`
2. **Task 2 — Light hex assertions.** Appended a non-parametrised `TEST(PhlinkColorMixerLightTest, LockedHex)` to `phlink_color_mixer_unittests.cc`. Constructs `ui::ColorProvider`, sets `key.color_mode = kLight`, calls `AddPhlinkColorMixer`, runs `GenerateColorMapForTesting()`, then 11 explicit `EXPECT_EQ(provider.GetColor(...), SkColorSetRGB(...))` lines — one per token. Used a non-parametrised fixture (rather than extending the existing `PhlinkColorMixerTest` parametrised over both modes) so each Light hex assertion is distinct from Dark — 08-03 will mirror this pattern.
3. **Task 3 — Patch export.** Used `git -C chromium-src format-patch -1 HEAD --stdout > patches/0111-…patch` per the 08-01b learning (refresh-patches.py would renumber every patch from 0001 and break the gap-based slot scheme). Verified clean re-apply via `git reset --hard HEAD~1 && git apply --check 0111-…patch` (`CLEAN_APPLY_OK`), then re-applied + re-committed to restore HEAD; re-exported the patch so its `From <sha>` header matches the final HEAD `00e7f6c7fd32`.

## Verification

* `autoninja -C out/Default unit_tests` → `Build Succeeded: 5 steps` (incremental: 1 TU recompile + relink).
* `autoninja -C out/Default chrome` → `Build Succeeded: 3 steps` (incremental, no behavioral changes outside the palette TU).
* `out/Default/unit_tests --gtest_filter='*Phlink*'` → **5/5 PASSED**:
  * `PhlinkColorMixerLightTest.LockedHex` ✓ (new — 11 EXPECT_EQ)
  * `Modes/PhlinkColorMixerTest.ResolvesAllPhlinkIds/{0,1}` ✓ (unchanged from 08-01b)
  * `Modes/PhlinkColorMixerTest.IdempotentRegistration/{0,1}` ✓ (unchanged from 08-01b)
* `git apply --check patches/0111-…patch` against `HEAD~1` → clean (`CLEAN_APPLY_OK`).
* `grep -c "SkColorSetRGB" chrome/browser/ui/color/phlink_palette.cc` ≥ 11 ✓.

## Hex table actually written (kPhlinkLight)

| Idx | Token       | Hex      | SkColorSetRGB                |
| --- | ----------- | -------- | ---------------------------- |
| 0   | kCanvas     | #FFFFFF  | `0xFF, 0xFF, 0xFF`           |
| 1   | kSurface    | #F8F4EC  | `0xF8, 0xF4, 0xEC`           |
| 2   | kSurfaceAlt | #F1EDE5  | `0xF1, 0xED, 0xE5`           |
| 3   | kCard       | #FFFFFF  | `0xFF, 0xFF, 0xFF`           |
| 4   | kText       | #1A1A1A  | `0x1A, 0x1A, 0x1A`           |
| 5   | kTextMuted  | #525252  | `0x52, 0x52, 0x52`           |
| 6   | kHairline   | #E5E0D6  | `0xE5, 0xE0, 0xD6`           |
| 7   | kAccent     | #A8C8E8  | `0xA8, 0xC8, 0xE8`           |
| 8   | kOnAccent   | #1A1A1A  | `0x1A, 0x1A, 0x1A`           |
| 9   | kDanger     | #C0392B  | `0xC0, 0x39, 0x2B`           |
| 10  | kSuccess    | #2E8540  | `0x2E, 0x85, 0x40`           |

## Deviations from plan

1. **Patch tooling — same as 08-01b.** Plan Task 3 prescribed `python3 scripts/refresh-patches.py --slot 0111`. That tool still renumbers every patch from 0001 and would collapse the gap-based slot layout. Used `git format-patch -1 HEAD --stdout` per the standing 08-01b workaround. Follow-up (still open): teach `scripts/refresh-patches.py` a `--slot N` single-commit-export mode, or document `git format-patch -1` as the canonical single-new-commit path.
2. **`apply-patches.py --dry-run` is a list-only command** (it only prints `would apply N patch(es)` and exits 0 without invoking `git apply --check`). The plan's Task 3 verifier `python3 scripts/apply-patches.py --dry-run | grep -qi "ok|clean|success"` matched on the literal substring `clean` in plan filenames or never matched, depending on input. Replaced with a real verification: `git reset --hard HEAD~1 && git apply --check patches/0111-…patch` from chromium-src — confirmed clean apply, then re-applied and re-committed. Follow-up: `apply-patches.py --dry-run` should run `git apply --check` per patch, not just print the list.
3. **No `chrome/test/BUILD.gn` touch needed.** No new source files were added (only existing TU edits), so the siso BUILD.gn cache hiccup from 08-01b did not recur.
4. **Submodule pointer noise.** As in 08-01b, `git status` shows `M third_party/search_engines_data/resources` — not staged into the phase-08-02 commit. `apply-patches.py --dry-run` requires `--force` to bypass this check; this is benign per project standing rules.

## Threat-mitigation check (per plan threat_model)

| Threat        | Disposition | Status                                                                 |
| ------------- | ----------- | ---------------------------------------------------------------------- |
| T-08-02-01    | mitigate    | ✓ Per-token `EXPECT_EQ` in `LockedHex` test — drift fails CI.          |
| T-08-02-02    | mitigate    | ✓ No new code paths beyond palette literals; zero UMA / network calls. |

## Self-Check: PASSED

* `chrome/browser/ui/color/phlink_palette.cc` modified, contains all 11 D-08 hex literals → FOUND
* `chrome/browser/ui/color/phlink_color_mixer_unittests.cc` modified, contains `PhlinkColorMixerLightTest.LockedHex` → FOUND
* `patches/0111-phlink-phase-08-02-light-theme-palette.patch` exists, applies clean against `HEAD~1` → FOUND
* chromium-src commit `00e7f6c7fd32` → FOUND on `phlink-wip`
* `PhlinkColorMixerLightTest.LockedHex` → PASSED (1 test, 11 assertions)
* `Modes/PhlinkColorMixerTest.{ResolvesAllPhlinkIds,IdempotentRegistration}/{0,1}` → 4/4 still PASSED
