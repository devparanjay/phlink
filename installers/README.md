# Installers

This directory holds installer-build scripts for phlink. They consume
already-built browser binaries from a Chromium-side `out/Default/`
directory; they do not invoke `gn` or `autoninja` themselves.

| Platform | Script                                      | Output                                     |
| -------- | ------------------------------------------- | ------------------------------------------ |
| macOS    | [installers/mac/build-dmg.sh](mac/build-dmg.sh)             | `phlink-<v>-mac-arm64.dmg`         |
| Linux    | [installers/linux/build-appimage.sh](linux/build-appimage.sh) | `phlink-<v>-linux-x86_64.AppImage` |
| Linux    | [installers/linux/build-packages.sh](linux/build-packages.sh) | `.deb` + `.rpm`                            |
| Windows  | [installers/windows/build-msi.ps1](windows/build-msi.ps1)   | `phlink-<v>-win-x64.msi`           |

## Prerequisites

- **macOS**: Xcode CLT (`hdiutil`, `codesign` ship with macOS). For
  signed dmgs, a Developer ID Application identity in the keychain.
- **Linux (AppImage)**: `appimagetool` on PATH.
- **Linux (deb/rpm)**: [`fpm`](https://github.com/jordansissel/fpm)
  (`gem install fpm`).
- **Windows**: [WiX Toolset 3.x](https://wixtoolset.org/) on PATH.

## Update-helper inclusion

Each installer expects to find the platform-specific update helper
(`phlink_update_helper` or `phlink_update_helper.exe`) sitting next
to the main browser binary in `out-dir`. Build it explicitly:

```sh
autoninja -C out/Default chrome chrome/browser/phlink/updater:update_helpers
```

The mac dmg embeds it under `phlink.app/Contents/Helpers/`; the linux
packages drop it in `/usr/bin/`; the Windows MSI installs it next to
`phlink.exe` under `%LocalAppData%\phlink\`.

## Signing

These scripts produce **unsigned** artifacts by default. Production
signing happens in CI after release-key unlock; see
[release-keys.md](../docs/dev/release-keys.md). For local smoke
tests an ad-hoc signature is fine on macOS.

## Notarization

Mac notarization is **not** wired into `build-dmg.sh`. The CI release
workflow is responsible for invoking `xcrun notarytool submit` after
the dmg is signed with a Developer ID identity.
