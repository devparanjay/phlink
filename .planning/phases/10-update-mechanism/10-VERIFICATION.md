# Phase 10 Verification — Update Mechanism & Installers

**Status:** PASSED
**Verified:** 2026-04-30

## Scope Verified

Phase 10 delivers the signed-update and installer release chain for v1 alpha:

- TUF-style metadata client with signed root, timestamp, snapshot, and targets roles.
- Snapshot-to-target byte binding via length and SHA-256 before `targets.json` parsing.
- Metadata fetch, payload fetch, staging, update-check pipeline, and updater service wiring.
- Stable updater trust-root runtime path: `resources/phlink/keys/root.json` on unbundled platforms and `Contents/Resources/phlink/keys/root.json` in the macOS bundle.
- Native installer scripts for macOS DMG/update zip, Linux AppImage/deb/rpm/update payload, and Windows MSI/update exe.
- Release key ceremony and per-release signing scripts.
- GitHub Actions packaging and release-sign workflows with provenance gates before TUF key materialization.

## Security Gates

- `timestamp.json` pins `snapshot.json` by length and SHA-256.
- `snapshot.json` pins `targets.json` by length and SHA-256.
- Release signing only accepts the expected eight installer/update artifacts.
- Release TUF `targets.json` contains exactly the three updater payload targets with explicit `version`, `platform`, `arch`, `channel`, and `format` metadata.
- Package workflows validate Chromium build-run provenance before downloading artifacts.
- Package provenance records artifact SHA-256 digests, updater root SHA-256, compiled `phlink_product_version`, and `phlink_updater_dev_root=false`.
- Linux package provenance records the bundled public `release.gpg` SHA-256.
- `release-sign.yml` verifies package provenance, expected updater root SHA-256, product version, dev-root disablement, Linux public-key hash, macOS platform signing, and Windows Authenticode signing before materializing TUF/GPG signing keys.
- `release-sign.yml` verifies generated Linux detached signatures with `PHLINK_GPG_PUBLIC` before upload.

## Validation Run

- `clang-format` / `gn format` on changed Chromium files: passed.
- `autoninja -j 8 -C out/Default phlink_updater_unittests chrome`: passed.
- `out/Default/phlink_updater_unittests`: 38/38 passed.
- `codesign --force --deep --sign - out/Default/phlink.app`: passed.
- Trust root staged at `out/Default/resources/phlink/keys/root.json`: passed.
- macOS `build-dmg.sh` smoke with ad-hoc signing and new resource path: passed.
- `git diff --check` in phlink and Chromium checkouts: passed.
- `bash -n` on tracked shell scripts: passed.
- `python -m compileall -q scripts`: passed.
- Ruby YAML parse of `package-installers.yml` and `release-sign.yml`: passed.
- Embedded Python heredocs in both release workflows compile: passed.
- VS Code diagnostics for changed workflows/scripts/docs: no errors.
- `sign-release.sh` dry run with temporary Ed25519 keys and fake GPG shim: passed; emitted three update targets and snapshot-pinned `targets.json` metadata.
- GSD code review gate: passed with 0 critical, 0 warning, 0 info findings.

## Known Local Tooling Gap

Local `gpg` and Python `ruff` are not installed in the configured environment.
The release workflow contains the real CI GPG verification gate; the local `sign-release.sh` smoke used a fake GPG shim to exercise the TUF metadata path.

## Result

Phase 10 satisfies UPD-01, UPD-02, and UPD-03 for the repository-controlled release pipeline.
Actual production release execution still requires the protected CI secrets, Apple/Windows signing credentials, and a hosted metadata/artifact publishing operation at release time.
