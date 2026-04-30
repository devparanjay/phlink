# Plan 10-02 — UpdaterService (browser process)

**Phase**: 10
**Plan**: 10-02
**Atomic patch slot**: 0125
**Depends on**: 10-01 (patch 0124)
**Blocks**: 10-03, 10-06

## Outcome

A `phlink::updater::UpdaterService` keyed-service in the browser process
that, on a 24h ± 6h jitter cadence (when the user is active), fetches TUF
metadata via `TufClient`, looks up the target for the running platform/arch,
downloads the payload to a staging dir, and verifies the SHA-256 against
`targets.json`. **No bundle is applied** in this plan — staging only. The
chosen platform for first wiring is **macOS arm64**; other platforms gate to
no-op.

## Steps

1. New GN target `//chrome/browser/phlink/updater:service` with sources
   `updater_service.{h,cc}`, `update_check_scheduler.{h,cc}`,
   `staged_payload.{h,cc}`.
2. `UpdaterService` is a `KeyedService` registered for the system profile
   only (one updater per browser, not per profile).
3. Scheduling:
   - First check 5 minutes after browser startup (post-startup pressure).
   - Subsequent checks every 24h ± 6h jitter, anchored to wall-clock not
     monotonic clock (so a suspended laptop doesn't "owe" checks).
   - Honor `phlink.updates.auto_check_enabled` pref (default true).
4. Fetch flow:
   - `TufClient::FetchTimestamp` → if no change, exit early.
   - On change: `FetchSnapshot` → `FetchTargets` →
     `LookupTarget("phlink-{ver}-mac-arm64.zip")`.
   - If newer version: `network::SimpleURLLoader` GETs the payload to
     `Updates/{version}/payload.zip`. Verify SHA-256 streamed; on mismatch,
     delete and abort.
5. `StagedPayload` records `{version, payload_path, verified_at}` in
   `Updates/staged.json` for plan 10-03 to pick up.
6. Telemetry surface: **none**. Logging only (`VLOG(1)` + `update.log`
   rotated at 1 MB).
7. Build flag `phlink_updater_dev_url` defaulting to a localhost test repo.
   Release builds set this to the real CDN URL via build args.
8. Unit tests under `phlink_updater_unittests`:
   - `UpdaterServiceTest.HonorsAutoCheckPref`.
   - `UpdaterServiceTest.NoOpWhenTimestampUnchanged`.
   - `UpdaterServiceTest.StagesPayloadOnNewVersion` (uses `EmbeddedTestServer`
     hosting a fixture TUF repo).
   - `UpdaterServiceTest.RejectsPayloadWithBadSha256`.
   - `UpdaterServiceTest.HonorsJitterWindow` (mock clock).

## Verification

- All 5 unit tests green.
- Manual: run against a localhost fixture repo; observe `Updates/{ver}/payload.zip`
  plus `staged.json` populated; observe **zero** outbound requests other than
  the metadata + payload GETs (re-run network-capture harness with updater
  pointed at fixture; assert no other hosts).
- `chrome` builds + codesigns; phlink launches without warnings.

## Out of scope

- Applying the staged update (10-03).
- UI (10-06).
- Linux / Windows paths beyond a no-op stub (10-04 / 10-05).
