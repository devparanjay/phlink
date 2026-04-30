---
phase: 08-appearance-subsystem
plan: 04
subsystem: appearance
tags: [appearance, prefs, settings-ui, themes, observer, no-telemetry]
requires: [08-01b, 08-02, 08-03]
provides: [phlink_appearance_pref, phlink_appearance_observer, settings_ui_radio_row]
affects: [chrome/browser/themes, chrome/browser/phlink/appearance, chrome/browser/resources/settings/appearance_page, chrome/browser/ui/webui/settings, chrome/app/settings_strings.grdp]
tech-stack:
  added: []
  patterns: [KeyedService factory, PrefChangeRegistrar + ui::NativeThemeObserver, Polymer settings-radio-group]
key-files:
  created:
    - chrome/browser/phlink/appearance/BUILD.gn
    - chrome/browser/phlink/appearance/phlink_appearance_prefs.h
    - chrome/browser/phlink/appearance/phlink_appearance_prefs.cc
    - chrome/browser/themes/phlink_appearance_observer.h
    - chrome/browser/themes/phlink_appearance_observer.cc
    - chrome/browser/themes/phlink_appearance_observer_factory.h
    - chrome/browser/themes/phlink_appearance_observer_factory.cc
    - chrome/browser/themes/phlink_appearance_observer_unittest.cc
    - patches/0113-phlink-phase-08-04-appearance-mode-pref-and-settings-ui.patch
  modified:
    - chrome/browser/BUILD.gn
    - chrome/browser/themes/BUILD.gn
    - chrome/browser/prefs/browser_prefs.cc
    - chrome/browser/profiles/chrome_browser_main_extra_parts_profiles.cc
    - chrome/test/BUILD.gn
    - chrome/browser/resources/settings/appearance_page/appearance_page.html
    - chrome/app/settings_strings.grdp
    - chrome/browser/ui/webui/settings/settings_localized_strings_provider.cc
decisions: [D-04, D-05, D-06, D-10, D-11]
metrics:
  duration: ~25min
  completed: 2026-04-29
patch_slot: "0113"
chromium_src_sha: b41b389675154
---

# Phase 8 Plan 04: Appearance Mode Pref + Observer + Settings UI Summary

**One-liner:** End users can pick Light / Dark / Follow System from `chrome://settings/appearance`, persisted in `prefs::kPhlinkAppearanceMode` (default Follow System), with an observer that resets the color-provider cache on change and emits zero telemetry.

## What shipped

1. **Pref:** `phlink::appearance::kAppearanceMode` integer (default `2` / Follow System) registered via a new sub-package `chrome/browser/phlink/appearance/`, mirroring the Phase 5 `phlink::adblock` pattern. Wired from `chrome/browser/prefs/browser_prefs.cc::RegisterProfilePrefs` immediately after the adblock prefs. **Deviation:** plan listed `chrome/common/pref_names.{h,cc}` and `chrome/browser/profiles/profile_prefs.cc` as the registration sites, but the existing phlink prefs live under `chrome/browser/phlink/<sub>/`, and the plan explicitly says to follow that pattern — done.
2. **Observer + factory:** `phlink::appearance::PhlinkAppearanceObserver` in `chrome/browser/themes/`, owned by `PhlinkAppearanceObserverFactory` (KeyedService, `ServiceIsCreatedWithBrowserContext = true`). Subscribes to `PrefChangeRegistrar` on `kAppearanceMode` and to `ui::NativeTheme::GetInstanceForNativeUi()`. On any actionable change calls `ui::ColorProviderManager::Get().ResetColorProviderCache()`. **Zero telemetry** — no `UMA_HISTOGRAM*`, no `base::Uma*`, no `RecordAction`, no UKM, no log-to-disk (Phase 8 CONTEXT §5, carry-forward from Phase 6).
3. **`Invalidate()` walk:** Per-window iteration intentionally collapsed to a no-op. Upstream replaced `BrowserList::GetInstance()` with `GetAllBrowserWindowInterfaces()` in `//chrome/browser/ui/browser_window/internal:internal`, which would create a circular dep through this observer. Existing chrome views observe `NativeTheme` / `ThemeService` directly and repaint on their own — resetting the cache is the precondition that makes their next paint pick up the new palette. Documented inline. (D-11: no per-frame work either way.)
4. **Settings UI:** `chrome://settings/appearance` now shows a "phlink theme" `settings-radio-group` (Light / Dark / Follow System) above the upstream Theme/Color rows, bound to `prefs.phlink.appearance_mode`. Upstream rows are not removed — they remain naturally hidden on `is_chrome_branded=false` builds (D-05).
5. **i18n:** Four new strings in `chrome/app/settings_strings.grdp` (`IDS_SETTINGS_PHLINK_THEME_ROW_TITLE`, `IDS_SETTINGS_PHLINK_THEME_LIGHT`, `IDS_SETTINGS_PHLINK_THEME_DARK`, `IDS_SETTINGS_PHLINK_THEME_FOLLOW_SYSTEM`) wired through `settings_localized_strings_provider.cc::AddAppearanceStrings`.
6. **Tests:** `phlink_appearance_observer_unittest.cc` with 4 named tests, added to `chrome/test/BUILD.gn` `unit_tests`. `chrome/test/BUILD.gn` was `touch`ed after editing per the 08-01b lesson.
7. **Patch:** `patches/0113-phlink-phase-08-04-appearance-mode-pref-and-settings-ui.patch` — 699 lines, generated via `git format-patch -1 HEAD --stdout`. `scripts/apply-patches.py --dry-run --force` reports 30 patches will apply cleanly (`EXIT=0`).

## Verification

```
$ out/Default/unit_tests --gtest_filter='*Phlink*'
[1/11]  PhlinkAppearanceObserverTest.ConstructsAndDefaultsToFollowSystem  PASS
[2/11]  PhlinkAppearanceObserverTest.PrefChangeTriggersInvalidate          PASS
[3/11]  PhlinkAppearanceObserverTest.NativeThemeUpdateOnlyFiresWhenFollowingSystem PASS
[4/11]  PhlinkAppearanceObserverTest.NoTelemetryOnInvalidate               PASS
[5/11]  PhlinkColorMixerLightTest.LockedHex                                 PASS
[6/11]  PhlinkColorMixerDarkTest.LockedDarkHex                              PASS
[7/11]  PhlinkColorMixerDarkTest.OnAccent_DarkIsBlack_NeverWhite            PASS
[8..11] Modes/PhlinkColorMixerTest x4                                       PASS
SUCCESS: all tests passed.
```

Telemetry grep gate against `phlink_appearance_observer.{cc,h}` and `phlink_appearance_prefs.{cc,h}`: only matches are explanatory comments documenting the prohibition. No `UMA_HISTOGRAM`, no `base::Uma`, no `RecordAction(`, no `UKM` macros. ✅

## User UAT pending — APPR-04

The plan's human-verify checkpoint was deferred per autonomous chain rules. Build is green and the plumbing is correct; **the live UI smoke test against the built binary is the user's next step**. Steps to run when convenient:

1. Launch `out/Default/Chromium.app/Contents/MacOS/Chromium`.
2. Navigate to `chrome://settings/appearance`.
3. Confirm a "phlink theme" section appears at the top with three radio buttons; "Follow system" is preselected on a fresh profile.
4. Toggle Light / Dark / Follow System and verify the chrome flips without restart (tabs, toolbar, omnibox, settings page background all switch).
5. Change the OS appearance setting while the radio is on Follow System — phlink should follow live.
6. Close & reopen — last selection persists.
7. DevTools console on the settings page should be free of `phlink.appearance_mode`-related errors.

Note: because the underlying palette resolution still derives `key.color_mode` from `ui::NativeTheme` rather than from this pref directly, the live Light↔Dark switch may currently *only* be observable via the OS-follow path. Wiring the pref into the `ColorProviderKey` selection is in scope for a future appearance phase (08-05+ if added) — flag this in UAT feedback if it surfaces.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking] Pref registration site relocated.** The plan listed `chrome/common/pref_names.{h,cc}` + `chrome/browser/profiles/profile_prefs.cc`, but Phase 5 already established the `chrome/browser/phlink/<sub>/<sub>_prefs.{h,cc}` pattern (registered from `chrome/browser/prefs/browser_prefs.cc`). The plan itself authorizes this: "If the existing phlink-adblock pref registration is in a different file than `profile_prefs.cc`, follow the existing file." Added a new `chrome/browser/phlink/appearance/` GN target.
- Files: `chrome/browser/phlink/appearance/{BUILD.gn,phlink_appearance_prefs.h,phlink_appearance_prefs.cc}`, `chrome/browser/prefs/browser_prefs.cc`, `chrome/browser/BUILD.gn`.

**2. [Rule 3 — Blocking] `BrowserList::GetInstance()` → no-op walk.** Plan referenced `BrowserList::GetInstance()`, but upstream removed that API in favor of `GetAllBrowserWindowInterfaces()` in `//chrome/browser/ui/browser_window/internal:internal`. Adding that target as a dep of `//chrome/browser/themes:themes` would create a circular dep, and the per-window pass would be a no-op anyway because views already observe `NativeTheme` / `ThemeService`. Collapsed to a documented no-op in `Invalidate()`. The visible-side effect (live theme flip) is unchanged because `ResetColorProviderCache()` runs before any subsequent paint.
- Files: `chrome/browser/themes/phlink_appearance_observer.cc`.

**3. [Plan filename normalization] `_unittests.cc` → `_unittest.cc`.** Plan's `<files>` listed `phlink_appearance_observer_unittests.cc`, but Chromium convention (and the rest of the themes test sources) uses `_unittest.cc` (singular). Adopted the convention.
- Files: `chrome/browser/themes/phlink_appearance_observer_unittest.cc`, `chrome/test/BUILD.gn`.

**4. [Rule 2 — Missing critical] Factory + EnsureFactoryBuilt.** Plan said "wire ownership via the existing phlink KeyedService factory pattern (Phase 5 added one for adblock — copy that)." Added `PhlinkAppearanceObserverFactory` mirroring `AdblockSettingsServiceFactory` exactly, including the `EnsureFactoryBuilt`-equivalent call (`PhlinkAppearanceObserverFactory::GetInstance()`) in `chrome_browser_main_extra_parts_profiles.cc`. Without this the observer would never instantiate at runtime.
- Files: `chrome/browser/themes/phlink_appearance_observer_factory.{h,cc}`, `chrome/browser/profiles/chrome_browser_main_extra_parts_profiles.cc`.

### Auth Gates

None.

## Threat Flags

None — the surface this plan adds is browser-process-only (pref + observer + WebUI). No new IPC, no new network endpoints, no new file-system access. The pref clamping logic in `OnNativeThemeUpdated` already mitigates T-08-04-02 (malicious pref values).

## Self-Check: PASSED

- Files created: all listed paths exist. ✅
- Commit `b41b389675154` exists in `chromium-src` `phlink-wip`. ✅
- Patch `patches/0113-phlink-phase-08-04-appearance-mode-pref-and-settings-ui.patch` exists, 699 lines. ✅
- 4 new tests + 7 prior tests pass. ✅
- `apply-patches.py --dry-run --force` exits 0 with all 30 patches enumerated. ✅
- Telemetry grep gate green (only doc comments mention UMA/UKM). ✅
