# Plan 09-03 — Import flow

**Phase**: 9
**Plan**: 09-03
**Atomic patch slot**: 0120
**Depends on**: 09-01, 09-02

## Outcome

User can pick a `.phlinkbundle` from disk, enter the passphrase, and phlink
creates a brand-new profile (named `Imported <ISO timestamp>`) populated from
the bundle. The active profile is never touched.

## Steps

1. `BundleReader` (counterpart of `BundleWriter`):
   - `BundleReader::Open(FilePath, passphrase) -> Status`
   - `BundleReader::ListEntries() -> vector<EntryMeta>`
   - `BundleReader::ExtractTo(target_dir) -> Status`
   - Verifies AEAD tag, refuses `format_version > kSupportedMax`, refuses unknown KDF/AEAD ids, validates `MANIFEST.json` per-entry sha256.
2. `import_service`:
   - Calls `ProfileManager::CreateMultiProfileAsync` to mint a fresh profile dir.
   - Extracts bundle into the new profile dir (NOT live: profile is created off-the-record then promoted once verified).
   - Triggers a profile-load on success; user lands in the picker with the new profile available.
3. Mojo: extend `Exporter` interface OR add `Importer` interface with `Import(file_path, passphrase) => (status, new_profile_path)`.
4. WebUI Import card:
   - File picker → passphrase prompt → confirmation modal ("This will create a new profile named …") → progress bar → success toast with "Switch to imported profile" button.
5. Refuse-import error UX:
   - Wrong passphrase: "Could not decrypt bundle. Check the passphrase."
   - Unsupported version: "This bundle was created by a newer version of phlink. Update to import."
   - Tampered/corrupt: "Bundle integrity check failed. The file may be damaged."
6. Patch slot **0120** — single atomic patch.

## Verification

- Round-trip integration test: export a profile → wipe `--user-data-dir` → import bundle → assert bookmarks count, history row count, and preferences key set are byte-equivalent.
- Cross-platform: same bundle imports cleanly on macOS / Linux / Windows runners.
- Negative tests: tampered tag, wrong passphrase, oversized version field — all rejected with correct status code.
- Network capture: zero outbound HTTP during import.
- Branding audit: import success page passes runtime audit.

## Out of scope

- Merge / replace import modes (CONTEXT D-05 locks "always create new").
- Bundle preview before decryption (deferred).
- Differential import.
