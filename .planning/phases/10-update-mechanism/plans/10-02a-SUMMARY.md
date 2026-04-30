# Phase 10 — Plan 10-02a — SUMMARY

**Status:** ✅ shipped
**Patch:** `0126-phlink-phase-10.02a-update-check-scheduler.patch`
**Chromium-src commit:** on `phlink-wip`
**Build:** `phlink_updater_unittests` ✅ + `chrome` ✅ (codesigned)
**Tests:** 7/7 pass (4 metadata + 3 scheduler)

## What shipped

A pure-policy scheduling primitive for periodic update checks. No timer, no
I/O, no inline pref reads — the caller injects a `is_auto_check_enabled`
callback and the scheduler returns the next `base::TimeDelta` (or
`std::nullopt` if disabled). This isolates the cadence policy from the
keyed-service / `PrefService` / `WallClockTimer` plumbing that **plan 10-02b**
will own.

### Files

| file | purpose |
| ---- | ------- |
| `pref_names.h` | `prefs::kAutoCheckEnabled` (bool, default true), `kLastCheckTime`, `kNextCheckTime` (int64 µs since Windows epoch). |
| `update_check_scheduler.h` / `.cc` | `UpdateCheckScheduler` with `kInitialDelay = 5 min`, `kBaseInterval = 24 h`, `kJitter = 6 h`. `ComputeNextDelay(is_first_check)` returns `kInitialDelay` for the first call and `kBaseInterval ± U[-kJitter, +kJitter]` thereafter. |
| `update_check_scheduler_unittest.cc` | 3 tests: nullopt-when-disabled, first-uses-initial-delay, jitter-within-envelope (200 draws, asserts >100 distinct values to catch a deterministic regression). |
| `BUILD.gn` | new `source_set("scheduler")`; wired into `unit_tests`. |

## Issues hit + fixes

* **`base::RepeatingCallback` undefined.** `callback_forward.h` is not
  enough at use sites — switched to `base/functional/callback.h`.
* **`base::RandInt` is `int`-only.** Microsecond-resolution jitter (±6h ≈
  ±2.16 × 10¹⁰) overflows. Switched to `base::RandGenerator(uint64_t)`
  recentered on zero.
* **`base::Value::Dict` / `base::Value::List`.** Recent rename to
  `base::DictValue` / `base::ListValue` re-bit the metadata files in this
  patch's incremental build; reapplied the rename.

## Out of scope (deferred to 10-02b)

* `UpdaterService` keyed-service skeleton + factory.
* `BrowserContextKeyedServiceFactory` registration on the system profile.
* Pref registrar (`PrefService::RegisterBooleanPref` / `RegisterInt64Pref`).
* `base::WallClockTimer` driving `ComputeNextDelay`.
* Network fetch (`network::SimpleURLLoader`) of timestamp / snapshot /
  targets.
* Staging dir + `staged.json` persistence.
* `EmbeddedTestServer`-backed integration tests of the full fetch flow.
