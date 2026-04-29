# Installer build scripts

Cross-platform installer build scripts for phlink. Each script consumes
a pre-built browser tree from a Chromium-side `out/Default/` directory
and emits one signed-or-signable installer artifact.

See [installers/README.md](../../installers/README.md) for prerequisites
and signing notes.

## End-to-end release flow

```sh
# 1. Build the browser + update helper.
cd /path/to/chromium-src/src
autoninja -C out/Default chrome \
                          chrome/browser/phlink/updater:update_helpers \
                          chrome/browser/phlink/updater:phlink_updater_unittests

# 2. Run unit tests.
out/Default/phlink_updater_unittests

# 3. Build platform installer.
cd /path/to/phlink
installers/mac/build-dmg.sh /path/to/chromium-src/src/out/Default 0.1.0
# or
installers/linux/build-appimage.sh /path/to/chromium-src/src/out/Default 0.1.0
# or, on Windows:
pwsh installers/windows/build-msi.ps1 -OutDir C:\src\chromium-src\src\out\Default -Version 0.1.0

# 4. Sign (CI only; see release-keys.md).
```

## Artifacts

| Platform | Artifact                              | Signing            | Notarization      |
| -------- | ------------------------------------- | ------------------ | ----------------- |
| macOS    | `phlink-<v>-mac-arm64.dmg`            | Developer ID       | required (CI)     |
| Linux    | `phlink-<v>-linux-x86_64.AppImage`    | gpg detached       | n/a               |
| Linux    | `phlink_<v>_amd64.deb`                | gpg signed repo    | n/a               |
| Linux    | `phlink-<v>-1.x86_64.rpm`             | rpm-sign + gpg     | n/a               |
| Windows  | `phlink-<v>-win-x64.msi`              | EV Authenticode    | n/a               |

## What the installers don't do

- They don't build the browser. Use `autoninja chrome` first.
- They don't notarize. CI invokes `xcrun notarytool` separately.
- They don't sign. Signing happens in CI with secrets that never
  touch developer machines (see [release-keys.md](release-keys.md)).
- They don't upload. CI publishes the signed artifacts to GitHub
  Releases; phlink's TUF metadata server (deferred) ingests them.
