# Phase 10 — Plan 10-02c — SUMMARY

**Status:** ✅ shipped
**Patch:** `0128-phlink-phase-10.02c-metadata-fetcher.patch`
**Build:** `phlink_updater_unittests` ✅ + `chrome` ✅ (codesigned)
**Tests:** 14/14 pass (4 metadata + 3 fetcher + 3 scheduler + 4 service)

## What shipped

`MetadataFetcher` — a per-update-check object that fetches the three
TUF metadata files (`timestamp.json`, `snapshot.json`, `targets.json`)
from a configurable base URL over `network::SimpleURLLoader` and feeds
each body into the matching `TufClient::Ingest*` step. Network failures
and schema failures are surfaced via a single `OnceCallback<void(TufError)>`
result.

### Files

| file | purpose |
| ---- | ------- |
| `metadata_fetcher.h` / `.cc` | `Fetch(TufClient*, ResultCallback)` drives a `Stage` machine across the three roles using `SimpleURLLoader::DownloadToString`. Cookie-less, cache-disabled, `CredentialsMode::kOmit`, `LOAD_DISABLE_CACHE \| LOAD_BYPASS_CACHE \| LOAD_DO_NOT_SAVE_COOKIES`. Annotated via `net::DefineNetworkTrafficAnnotation`. |
| `metadata_fetcher_unittest.cc` | 3 tests over `network::TestURLLoaderFactory.GetSafeWeakWrapper()`: happy path (all three roles), HTTP 500 on timestamp, malformed JSON on timestamp. |
| `metadata_test_helpers.h` / `.cc` | New shared `phlink::updater::test_helpers` namespace exposing the existing fixture builders (`MakeTestKey`, `Envelope`, `BuildRoot/Timestamp/Snapshot/TargetsSigned`, `Bytes`, `ToHex`) so both `metadata_client_unittest.cc` and `metadata_fetcher_unittest.cc` share them. |
| `metadata_client_unittest.cc` | refactored to consume the shared helpers via `using` decls; no behavior change. |
| `BUILD.gn` | new `source_set("fetcher")`, new `testonly source_set("test_helpers")`; `unit_tests` now depends on `:fetcher` + `:test_helpers` + `//net`, `//services/network:test_support`, `//services/network/public/{cpp,mojom}`, `//url`. Test runner switched from `//base/test:run_all_unittests` to `//mojo/core/test:run_all_unittests` so `SimpleURLLoader`'s Mojo plumbing is initialized. |

## Out of scope (deferred)

* **10-02d:** payload (`.zip`) `SimpleURLLoader::DownloadToFile` to
  `Updates/{ver}/payload.zip` + sha256 verify against the `targets.json`
  entry. `staged.json` write of `{version, payload_path, sig_chain}`.
* **10-02e:** `UpdaterServiceFactory` (`KeyedServiceFactory`) +
  system-profile registration; wire `MetadataFetcher` (and the 10-02d
  payload fetcher) into the `CheckCallback` injected into
  `UpdaterService` in 10-02b.
* `EmbeddedTestServer`-backed integration test of the full fetch flow.

## Notes for 10-02d / 10-02e

* `MetadataFetcher` ctor takes `scoped_refptr<network::SharedURLLoaderFactory>`
  and a `GURL base_url` (must end in `/`). The factory will come from
  the system profile's `URLLoaderFactory` in 10-02e.
* `TufClient` is consumed by reference — the fetcher does **not** own it.
  10-02e should construct a `TufClient` via `CreateWithRoot` from the
  pinned `root.json` (10-01b) per check.
* `SimpleURLLoader::BodyAsStringCallback` is
  `OnceCallback<void(std::optional<std::string>)>` in this tree (it
  changed from `unique_ptr<string>`); 10-02d's payload fetcher will
  instead use `DownloadToFile`.
