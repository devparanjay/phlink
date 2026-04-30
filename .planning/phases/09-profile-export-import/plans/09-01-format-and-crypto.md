# Plan 09-01 — Encrypted bundle format spec + crypto primitives

**Phase**: 9 — Profile Export/Import
**Plan**: 09-01
**Atomic patch slot**: 0118
**Depends on**: nothing in Phase 9 (foundation)
**Blocks**: 09-02, 09-03

## Outcome

A working, GN-built `//third_party/phlink_crypto/` Rust crate exposing a stable
C ABI (`#[no_mangle] extern "C"`) for:

- `phlink_kdf_derive(passphrase, salt, params, out_key32)` — Argon2id key derivation.
- `phlink_aead_seal(key32, nonce24, aad, plaintext, out_ciphertext)` — XChaCha20-Poly1305 AEAD.
- `phlink_aead_open(key32, nonce24, aad, ciphertext, out_plaintext)` — AEAD decrypt + verify.
- `phlink_random_fill(buf, len)` — boringssl-backed CSPRNG.

Plus a written spec doc `docs/dev/profile-bundle-format.md` describing the
on-disk layout, version negotiation, and threat model.

## Steps

1. Write `docs/dev/profile-bundle-format.md` (this repo, not chromium-src):
   - Magic `PHLB` (4 bytes).
   - Format version `u16 le`.
   - KDF id `u8` (1 = Argon2id).
   - KDF params: `m_kib u32 le`, `t u32 le`, `p u32 le`, `salt_len u8`, `salt[salt_len]` (16).
   - AEAD id `u8` (1 = XChaCha20-Poly1305).
   - Nonce `[24]`.
   - Payload length `u64 le`.
   - Payload ciphertext `[payload_length]` (covers `tar.zst` of profile dir).
   - AEAD tag `[16]` (Poly1305).
   - Header (everything before ciphertext) is the AEAD AAD.
2. Create `//third_party/phlink_crypto/` (chromium-src tree):
   - `Cargo.toml`: deps `argon2 = "0.5"`, `chacha20poly1305 = "0.10"` (XChaCha20 feature), `zeroize = "1"`.
   - `src/lib.rs`: 4 `extern "C"` functions above; `#[repr(C)]` param structs.
   - `BUILD.gn` driven by `gnrt` (mirror Phase 5 adblock-rust pattern, patch 0090).
   - Header `phlink_crypto.h` — exported via `cargo-c`-style manual hand-write (mirrors adblock cxx pattern).
3. Update `//build/rust/cargo_crate.gni` consumers list as needed (gnrt regen).
4. Wire a tiny C++ smoke test under `chrome/browser/phlink/crypto/` that:
   - Calls `phlink_kdf_derive` with an Argon2id RFC 9106 test vector and asserts equality.
   - Calls AEAD seal/open round-trip with a known vector.
5. Build target: `chrome` plus the new test target.
6. Patch slot **0118** — single atomic patch.

## Verification

- `gn check` clean.
- `autoninja chrome` succeeds.
- Smoke test target runs and asserts pass on macOS dev build.
- `docs/dev/profile-bundle-format.md` rendered.

## Out of scope

- C++ codec wrapper (lives in 09-02 / 09-03).
- UI (lives in 09-02 / 09-03).
