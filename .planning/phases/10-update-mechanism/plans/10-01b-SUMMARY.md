# Phase 10 — Plan 10-01b — SUMMARY

**Status:** ✅ shipped
**Patch:** `0125-phlink-phase-10.01b-tuf-client-skeleton.patch`
**Chromium-src commit:** `b0318a1` on `phlink-wip`
**Build:** `phlink_updater_unittests` ✅ + `chrome` ✅ (codesigned)
**Tests:** 4/4 pass

## What shipped

In-tree pure-C++ TUF v1.0.32 metadata client. No Rust crate, no `hyper`, no `ring`
— honours Phase 9 D-01 (boringssl-only crypto) and stays off the network on the
verification path.

### Files (under `chrome/browser/phlink/updater/`)

| file | purpose |
| ---- | ------- |
| `canonical_json.h` / `.cc` | TUF-flavour canonical JSON encoder: sorted keys (lex byte order), no whitespace, integers only, rejects floats / blobs. |
| `metadata_client.h` / `.cc` | `TufClient` — `CreateWithRoot`, `IngestTimestamp`, `IngestSnapshot`, `IngestTargets`, `LookupTarget`. Threshold Ed25519 verification via `crypto::sign::Verify`, expires/rollback/version-pin checks, length+SHA-256 pinning across the timestamp→snapshot→targets chain. SHA-256 via boringssl `::SHA256`. |
| `keys/dev_root.json` | 1-of-1 dev trust root. Ships only when `phlink_updater_dev_root=true` (default for now); plan 10-08 swaps in production root. |
| `metadata_client_unittest.cc` | 4 tests: `AcceptsValidMetadata`, `RejectsExpiredTimestamp`, `RejectsRollback`, `RejectsBadSignature`. |
| `phlink_updater.gni` | `phlink_updater_dev_root` build arg. |
| `BUILD.gn` | `source_set("canonical_json")`, `source_set("metadata")`, `test("phlink_updater_unittests")`, `copy("dev_root_json")` → `$root_out_dir/phlink/keys/`. |

Also: wired `//chrome/browser/phlink/updater:phlink_updater_unittests` into the
`chrome_test_targets` group in `//BUILD.gn`.

## Verification policy (locked here, ratified by tests)

* Unknown signature `keyid` → silently ignored (TUF-spec compliant).
* Known `keyid` + bad signature bytes → **fail closed** (`kBadSignature`).
* Threshold counts **distinct** valid `keyid`s.
* `spec_version` must start with `"1.0."` else `kUnsupportedSpec`.
* `expires` parsed via `base::Time::FromUTCString`; missing/malformed → `kBadJson`.
* Each role's `version` must be **strictly greater** than the cached one
  (rollback protection) **except** snapshot/targets which must **equal** their
  pinned version from the parent role.
* Snapshot bytes are length-checked and SHA-256-checked against the
  timestamp pin **before** the JSON is even parsed.

## Issues hit + fixes

* **`base::Value::Dict` / `base::Value::List` no longer exist.** Recent
  Chromium renamed these to `base::DictValue` / `base::ListValue` (see
  `base/values.h:43,242`). All references updated.
* **`raw_ptr<>` required for class fields.** The internal `Envelope` struct's
  two pointers triggered the chromium-rawptr plugin. Switched to
  `raw_ptr<const base::Value>` + `raw_ptr<const base::ListValue>` and added
  `#include "base/memory/raw_ptr.h"`.
* **Out-of-line ctor/dtor required.** chromium-style flagged `TargetMeta` and
  the private `RoleSpec` nested struct. Added explicit declarations in the
  header and `= default` definitions in the cc.
* **Missing `#include "base/strings/string_util.h"`** for `base::ToLowerASCII`.
  Needed by the unit-test helper that lower-cases `base::HexEncode` output
  (the new `HexEncode` returns uppercase).

## Out of scope (deferred to later 10-0x plans)

* Network fetch of the metadata chain (10-02 `UpdaterService`).
* Persistence of last-known-good versions across runs (10-02).
* Targets payload download + per-platform application (10-03/04/05).
* Settings UI surfaces (10-06).
* Installers / per-OS update channels (10-07).
* Production root + signing/CI (10-08).
