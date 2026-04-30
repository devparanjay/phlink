# Plan 10-07 — Native installer packaging

**Phase**: 10  ·  **Plan**: 10-07  ·  **Atomic patch slot**: phlink-side only (no chromium-src patch)
**Depends on**: 10-03 / 10-04 / 10-05 (helpers must exist)

## Outcome

`installers/` directory **in the phlink repo** with one packaging script per
target:

- `installers/mac/build-dmg.sh` → produces `phlink-{version}-mac-arm64.dmg`
  (signed + notarized in CI, ad-hoc in local dev).
- `installers/linux/build-appimage.sh` → produces `.AppImage` + zsync
  detached `.sig`.
- `installers/linux/build-deb.sh` → produces `.deb`.
- `installers/linux/build-rpm.sh` → produces `.rpm`.
- `installers/windows/build-msi.ps1` → produces signed `.msi` via WiX.

Each script consumes the output of the corresponding chromium-src GN build
(staged by `scripts/build.{sh,ps1}`) and writes artifacts under `dist/`.

## Key steps

1. Author each script. Keep them small, single-purpose, idempotent.
2. Add CI workflow snippets that wire these into the existing matrix from
   Phase 2.
3. Document in `docs/dev/installers.md`.
4. Smoke test in CI: every push produces unsigned artifacts; signed
   artifacts only on tag push.

## Out of scope

Actual cert provisioning + key escrow (10-08).
