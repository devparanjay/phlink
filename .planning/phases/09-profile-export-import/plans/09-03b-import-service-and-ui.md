# Plan 09-03b — Import flow (service + ProfileManager hookup + Import card)

**Phase**: 9
**Plan**: 09-03b (follow-up to 09-03)
**Atomic patch slot**: 0122
**Depends on**: 09-01 (patch 0118), 09-02 (patch 0119), 09-02b (patch 0121),
                09-03 (patch 0120)

## Outcome

User can pick a `.phlinkbundle` from disk, enter the passphrase, and
phlink creates a brand-new profile (named `Imported <ISO timestamp>`)
populated from the bundle. The active profile is never touched.

## Context

Plan 09-03 originally bundled the codec, the worker service, the
ProfileManager hookup, the Import card UI, and the round-trip
integration test. Patch 0120 landed only the codec
(`BundleReader`) plus its six unit tests (round-trip + five negative
paths from the format spec §7). This sub-plan finishes the rest.

## Steps

1. **Service** — `chrome/browser/phlink/portability/import_service.{h,cc}`:
   - Calls `ProfileManager::CreateMultiProfileAsync` to mint a fresh
     profile dir (off-the-record until verified).
   - Calls `BundleReader::OpenFile(path, passphrase)` and routes the
     `BundleReader::Status` enum to the user-facing strings from format
     spec §7.
   - On `kOk`, walks `BundleReader::Entries()` and writes each tar
     virtual path into the new profile dir (validating each entry's
     sha256 against `MANIFEST.json::entries` as a programmer-error
     guard, even though AEAD already covers the whole payload).
   - On success, promotes the profile and surfaces it in the picker.
   - On failure, deletes the scratch profile dir.
2. **Mojo** — extend the `Exporter` interface from 09-02b or add a
   separate `Importer`:
   - `interface Importer { Import(mojo_base.mojom.FilePath path, string passphrase) => (ImportStatus status, mojo_base.mojom.FilePath? new_profile_path); }`
3. **Import card UI** — under `portability_section.ts`:
   - File picker → passphrase prompt → confirmation modal ("This will
     create a new profile named …") → progress bar → success toast with
     a "Switch to imported profile" button.
   - Maps `BundleReader::Status` to the strings from
     [profile-bundle-format.md §7](../../../../docs/dev/profile-bundle-format.md#7-failure-modes-importer).
4. **Round-trip integration test** —
   `chrome/browser/phlink/portability/portability_round_trip_browsertest.cc`:
   - Export a synthetic profile → wipe `--user-data-dir` → import the
     bundle → assert bookmarks count, history row count, and preferences
     key set are byte-equivalent.
   - Cross-platform CI gate (mac / linux / win).
5. **Patch slot 0122** — single atomic patch.

## Verification

- Round-trip integration test (above) passes on all three platforms.
- Negative paths: tampered tag, wrong passphrase, oversized version
  field — all rejected via the corresponding `Status` and surface the
  correct UI string.
- Network capture: zero outbound HTTP during import.
- Branding audit: import success page passes runtime audit.

## Out of scope

- Merge / replace import modes (CONTEXT D-05 locks "always create new").
- Bundle preview before decryption.
- Differential import.
