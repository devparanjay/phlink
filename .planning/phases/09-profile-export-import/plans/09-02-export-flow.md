# Plan 09-02 — Export flow

**Phase**: 9
**Plan**: 09-02
**Atomic patch slot**: 0119
**Depends on**: 09-01

## Outcome

User can navigate to `chrome://settings/portability`, click **Export**, enter a
passphrase twice (Argon2 KDF runs in a worker), pick a save location, and
receive a `.phlinkbundle` file containing tar.zst of:

- `Bookmarks` (JSON file from profile dir)
- `History` (sqlite, copied with WAL checkpoint)
- `Preferences` (JSON)
- `Web Data` (sqlite — search engines, autofill *off* by default)
- `MANIFEST.json` (format version, export timestamp, sha256 of each entry, included-categories list)

Excluded by default per CONTEXT D-04: `Login Data`, `Cookies`, `Network/Cookies`,
`Sessions/`, `Tabs/`, anything containing decryptable credentials.

## Steps

1. C++ codec wrapper `chrome/browser/phlink/portability/bundle_writer.{h,cc}`:
   - `BundleWriter::Open(FilePath, passphrase) -> Status`
   - `BundleWriter::AddFile(virtual_path, content_bytes)` — accumulates into in-memory tar.
   - `BundleWriter::Finalize()` — zstd-compresses tar (use existing `//third_party/zstd`), seals with `phlink_crypto`, writes file, zeroizes key.
   - tar implementation: simple POSIX ustar (handwritten, ~150 LOC). Forward-slash paths, UTF-8.
2. Service `chrome/browser/phlink/portability/export_service.{h,cc}`:
   - Runs on `base::ThreadPool` (USER_VISIBLE).
   - Snapshots history with `sql::Database::Raze`-style WAL checkpoint, copies to a temp file before reading (to avoid grabbing the live DB).
   - Walks the include-list from D-04, feeds bytes into `BundleWriter`.
   - Reports progress via mojo to the WebUI.
3. Mojo: `chrome/browser/phlink/portability/portability.mojom` —
   - `interface Exporter { Export(passphrase, file_path) => (status); GetProgress() => (percent, current_step); }`
4. WebUI: `chrome/browser/resources/settings/portability_section/`:
   - `portability_section.ts` — Polymer/Lit element under settings.
   - Two-card layout from CONTEXT D-06.
   - Export card: passphrase + confirm, "Show what's included" expander (read-only checklist of D-04), Save button → `chrome.fileSystem.chooseEntry`-equivalent → mojo call.
   - Progress bar bound to `GetProgress`.
5. Settings registration: add to `chrome/browser/ui/webui/settings/settings_localized_strings_provider.cc` and route `chrome://settings/portability`.
6. Patch slot **0119** — single atomic patch.

## Verification

- Unit: `BundleWriter` round-trip in-memory test (via 09-03's reader once it lands; for 09-02 alone, assert file is non-empty + parseable header).
- Manual: launch phlink, navigate to `chrome://settings/portability` and `phlink://settings/portability` — both load.
- Network capture: zero outbound HTTP during export (assert via `tests/network-capture/`).
- Branding audit: extend `runtime-audit.py` with `/portability` surfaces.

## Out of scope

- Import (lives in 09-03).
- Differential / scheduled exports.
- Password / cookie inclusion (deferred v1.1).
