# Plan 09-03b — SUMMARY

**Status**: ✅ Complete
**Patch**: 0123 (`patches/0123-phlink-phase-9.03b-import-flow-and-import-card.patch`)
**Commit**: c0e2046 ("phase 9: 09-03b import flow + Import card")

## What landed

- **Importer mojom**: `ImportStatus` enum (kOk, kBadMagic, kUnsupportedVersion,
  kUnknownPrimitive, kBadPassphrase, kIntegrity, kTruncated, kIo,
  kProfileCreationFailed) and `Importer.Import(path, passphrase)` /
  `Importer.ImportFromPickedFile(passphrase)`.
- **`ImportService`** (`ImportBundleToDir`): drives `BundleReader`, verifies
  manifest hashes against extracted bytes, refuses absolute / `..` entries,
  writes into the target profile dir.
- **`ImporterImpl`**: mojo receiver + `SelectFileDialog` for `.phlinkbundle`;
  spins up a fresh profile via
  `ProfileManager::CreateMultiProfileAsync("Imported <ISO ts>")`, then runs
  `ImportBundleToDir` on a USER_BLOCKING worker. On failure, posts a
  best-effort `DeletePathRecursively` to remove the half-populated dir.
- **`PortabilityUI`** binds the new `Importer` interface; i18n strings added
  for all 9 status outcomes.
- **chrome://portability Import card**: passphrase input, "Pick bundle…"
  button, status + imported-profile path display.

## Verification

- 16/16 tests in `phlink_crypto_unittests` green, including new
  `ImportServiceTest.{RejectsEmptyPassphrase, RejectsBadPassphrase,
  RoundTripWritesEntriesIntoDir}`.
- `chrome` builds and codesigns; manual end-to-end import via
  `chrome://portability` produces a new "Imported …" profile populated from
  a previously exported bundle.

## Follow-up / known gaps

- Round-trip **browsertest** (BrowserTest harness, separate from the unit
  tests) is documented as a follow-up; the unit-level round-trip is already
  covered by `RoundTripWritesEntriesIntoDir`.
- On import failure we delete the scratch profile dir but do not unregister
  the entry from `ProfileAttributesStorage`. Acceptable for v1; revisit if
  it shows up as user-visible noise.
