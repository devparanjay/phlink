# Phase 10 — Plan 10-08 — SUMMARY

**Status:** ✅ shipped
**Patch slot:** phlink-side only
**phlink commits:** `b58431a`, `e82b6dd`
**Validation:** shell syntax ✅, YAML parse ✅, metadata dry run ✅

## What shipped

Release key-generation and signing tooling for TUF-style metadata plus Linux detached signatures.
The release workflow is gated by the `release-signing` GitHub environment and uses distinct Ed25519 keys for TUF targets, snapshot, and timestamp roles.

### Files

| file | purpose |
| ---- | ------- |
| `scripts/release/keygen.sh` | Generates root, targets, snapshot, timestamp, and gpg release keys for the ceremony. |
| `scripts/release/sign-release.sh` | Signs Linux artifacts with gpg and writes signed `targets.json`, `snapshot.json`, and `timestamp.json`. |
| `.github/workflows/release-sign.yml` | Manual environment-gated signing workflow. |
| `docs/dev/release-keys.md` | Key inventory, ceremony, CI secret names, per-release flow, and delegated key rotation. |
| `docs/dev/ci.md` | Documents required signing secrets and CI release boundary. |

## Deviations from Plan

No CDN upload is performed by the script yet; metadata upload remains a release-ops step until phlink has a hosted metadata service.
Root metadata remains offline-only and is regenerated during key ceremony/rotation.

## Issues Encountered

OpenSSL Ed25519 one-shot signing requires a real input file rather than stdin on this machine; `sign-release.sh` now writes canonical role bytes to a temporary file before `pkeyutl -rawin`.
Local `gpg` is not installed, so the full real-gpg dry run could not run here; a fake `gpg` shim was used to exercise the TUF metadata path with temporary Ed25519 keys.

## Self-Check: PASSED

- `git diff --check` passed.
- `bash -n` passed for release scripts.
- Ruby YAML parsing passed for release workflow.
- Dry run produced `targets.json`, `snapshot.json`, `timestamp.json`, and `.AppImage.sig` with temporary keys and fake gpg.

## Next Phase Readiness

Phase 12 can consume signed release artifacts and metadata for the v1.0 alpha release gate.

---
*Phase: 10-update-mechanism*
*Completed: 2026-04-30*