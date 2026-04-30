# Plan 09-01 — SUMMARY

**Status**: ✅ Complete
**Patch**: 0118 (`patches/0118-phlink-phase-9.01-phlink-crypto-ffi.patch`)
**Commit**: 500fbdd ("phase 9: 09-01 phlink_crypto FFI + bundle format spec (PROF-01)")

## What landed

- New crate `//third_party/phlink_crypto/` (Rust) exposing C ABI:
  - `phlink_kdf_derive` (Argon2id), `phlink_aead_seal` / `phlink_aead_open`
    (XChaCha20-Poly1305), `phlink_random_fill` (boringssl-backed CSPRNG).
- GN integration via `gnrt`; GN target `//third_party/phlink_crypto:phlink_crypto`.
- Format spec: `docs/dev/profile-bundle-format.md` (on-disk layout, version
  negotiation, threat model).
- Unit tests: round-trip seal/open, KDF KAT, version-mismatch rejection,
  tamper-rejection.

## Verification

- `phlink_crypto_unittests` green (KDF + AEAD coverage).
- Format doc reviewed against §10.1 PRD locked decisions.
