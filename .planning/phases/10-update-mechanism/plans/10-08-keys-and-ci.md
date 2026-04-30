# Plan 10-08 — Key-ceremony tooling + CI signing pipeline

**Phase**: 10  ·  **Plan**: 10-08  ·  **Atomic patch slot**: phlink-side only
**Depends on**: 10-01 (TUF metadata format)

## Outcome

`scripts/release/` tooling that:

1. Generates a fresh TUF root + targets + snapshot + timestamp keyset
   (Ed25519, age-encrypted at rest), with the **root** key destined for an
   offline YubiKey.
2. Signs metadata for a given release: produces
   `metadata/{root,targets,snapshot,timestamp}.json` ready for upload to
   the CDN.
3. Rotates expired keys (timestamp every 7d, snapshot every 30d, targets
   every 90d).
4. Documents the key ceremony in `docs/dev/release-keys.md` (offline
   environment, attestation, threshold, witnesses).

## Key steps

- `scripts/release/keygen.sh` — `tuf` CLI wrapper, prompts for offline
  storage of root.
- `scripts/release/sign-release.sh <version>` — pulls payloads from the
  Phase 10-07 artifact set, computes SHA-256, populates `targets.json`,
  signs, uploads to CDN bucket via `aws s3 cp` (or equivalent).
- CI hook: a `release-sign.yml` workflow gated on a manual approval that
  pulls online keys from GitHub Actions secrets.

## Out of scope

Actual key generation. This plan ships the **tooling**; real keys are
generated as a one-time ceremony before the v1.0 alpha tag.
