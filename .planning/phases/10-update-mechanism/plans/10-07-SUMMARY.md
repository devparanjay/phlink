# Phase 10 — Plan 10-07 — SUMMARY

**Status:** ✅ shipped
**Patch slot:** phlink-side only
**phlink commits:** `3f602a8`, `e82b6dd`
**Validation:** shell syntax ✅, YAML parse ✅, signing dry run support ✅

## What shipped

Cross-platform installer packaging scripts that consume existing Chromium `out/Default` outputs and write release artifacts under `dist/`.
The manual `package-installers.yml` workflow downloads prebuilt browser artifacts and runs the platform packaging scripts without fetching or building Chromium on GitHub-hosted runners.

### Files

| file | purpose |
| ---- | ------- |
| `installers/mac/build-dmg.sh` | Builds `dist/phlink-<version>-mac-arm64.dmg`, embeds the helper, and ad-hoc signs locally. |
| `installers/linux/build-appimage.sh` | Builds `dist/phlink-<version>-linux-x86_64.AppImage`. |
| `installers/linux/build-packages.sh` | Builds `dist/phlink_<version>_amd64.deb` and `dist/phlink-<version>-1.x86_64.rpm`. |
| `installers/windows/build-msi.ps1` | Builds `dist/phlink-<version>-win-x64.msi` with WiX. |
| `.github/workflows/package-installers.yml` | Manual macOS/Linux/Windows packaging workflow using prebuilt Chromium outputs. |
| `docs/dev/installers.md`, `installers/README.md`, `docs/dev/ci.md` | Release packaging docs and CI boundary notes. |

## Deviations from Plan

CI packaging is manual and consumes prebuilt Chromium artifacts instead of producing unsigned artifacts on every push; this preserves the repo's Phase 2 CI budget and avoids a multi-hour Chromium build on hosted runners.

## Issues Encountered

The initial scripts wrote artifacts back into `out/Default`; follow-up commit `e82b6dd` aligned every platform script to the planned `dist/` contract.

## Self-Check: PASSED

- `git diff --check` passed.
- `bash -n` passed for shell installer/release scripts.
- Ruby YAML parsing passed for both new workflows.

## Next Phase Readiness

Packaged artifacts flow into 10-08 signing metadata and Linux detached signatures.

---
*Phase: 10-update-mechanism*
*Completed: 2026-04-30*