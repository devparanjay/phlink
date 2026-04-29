# phlink Profile Bundle Format (`.phlinkbundle`)

> Version: **1**
> Status: **Draft (Phase 9, plan 09-01)**
> Authors: phlink
> Spec scope: encrypted, single-file, cross-platform profile export/import bundle.

## 1. Goals

1. **Local-only portability.** A `.phlinkbundle` file is the only mechanism by which a phlink profile leaves a device. There is no cloud sync (PRD §3.5, §10.1).
2. **Confidentiality + integrity.** The bundle is encrypted with a passphrase-derived key using authenticated encryption.
3. **Cross-platform.** A bundle produced on one OS imports cleanly on macOS, Linux, and Windows. The byte layout is identical across platforms.
4. **Forward-compatible.** The header carries an explicit format version and KDF/AEAD identifiers, so future versions can rotate primitives without breaking the parser surface.
5. **Streamable.** A reader can verify the header, derive the key, and stream-decrypt the payload without loading the entire file into memory.

## 2. Threat model

Assumed attacker capabilities:

- **Bundle theft.** Attacker has full read access to a stolen `.phlinkbundle`.
- **Tamper.** Attacker can modify any byte in transit.
- **Offline brute-force** of the passphrase using GPU/ASIC resources.
- **No** access to the user's RAM at the moment of unseal.

Out-of-scope threats:

- Side channels on the user's machine while phlink is running.
- Quantum adversaries.

Guarantees:

- Without the passphrase, the attacker learns at most: `format_version`, `kdf_id`, `aead_id`, KDF parameters, salt, nonce, payload length. Everything else is sealed.
- Any single-bit modification of the ciphertext, AAD, header, or tag causes `phlink_aead_open` to fail and the importer to refuse the bundle.
- Argon2id (m=64 MiB, t=3, p=1) makes per-guess cost ≥ ~500 ms on commodity GPUs, raising the per-guess cost ≥ 6 orders of magnitude vs PBKDF2-defaults.

## 3. Cryptographic primitives (v1)

| Role | Primitive | Notes |
|------|-----------|-------|
| Passphrase → key | **Argon2id**, m = 65536 KiB (64 MiB), t = 3, p = 1, output 32 bytes | RFC 9106. Salt 16 bytes random per bundle. |
| AEAD | **XChaCha20-Poly1305**, 32-byte key, 24-byte nonce, 16-byte tag | IETF draft / `libsodium` and `chacha20poly1305` Rust crate XChaCha extension. 192-bit random nonce is collision-safe for any reasonable export volume. |
| AAD | The 64-byte fixed-size header (everything before payload length) | Binds header parameters to the ciphertext. |
| RNG | boringssl `RAND_bytes` | Used for salt and nonce generation. |

## 4. On-disk byte layout

All multi-byte integers are little-endian.

```
offset  size   field
------  ----   -----
0x00    4      magic "PHLB"  (0x50 0x48 0x4C 0x42)
0x04    2      format_version (u16)            // 0x0001 for v1
0x06    1      kdf_id          (u8)            // 1 = Argon2id
0x07    1      aead_id         (u8)            // 1 = XChaCha20-Poly1305
0x08    4      argon2_m_kib    (u32)           // memory cost in KiB
0x0C    4      argon2_t        (u32)           // time cost (iterations)
0x10    4      argon2_p        (u32)           // parallelism
0x14    1      salt_len        (u8)            // = 16 in v1
0x15    16     salt            ([16])
0x25    24     nonce           ([24])
0x3D    8      payload_len     (u64)           // ciphertext length, EXCLUDING tag
0x45    pl     ciphertext      ([payload_len]) // sealed tar.zst stream
…       16     aead_tag        ([16])          // Poly1305 authenticator
```

Total header (AAD) size = 0x45 = **69 bytes**.

The encrypted payload is a `zstd`-compressed POSIX `ustar` archive. tar entries:

- Use forward-slash UTF-8 paths.
- Store mtime as int64 unix-epoch seconds.
- Store uid/gid/mode as zeros (no host metadata leakage).

The first tar entry MUST be `MANIFEST.json` with this shape:

```json
{
  "format_version": 1,
  "exporter_version": "phlink/0.1.0",
  "exported_at_utc": "2026-04-29T20:45:00Z",
  "categories": ["bookmarks", "history", "preferences", "search_engines"],
  "entries": [
    { "path": "Bookmarks", "sha256": "…hex…", "size": 12345 },
    …
  ]
}
```

Implementations MUST verify each entry's sha256 against `MANIFEST.json::entries`
after extraction. Mismatch is a hard import failure even though AEAD already
covers the whole payload — this catches programming errors in the
serializer/deserializer themselves, not just adversarial tampering.

## 5. Default-included categories (v1)

Per Phase 9 CONTEXT D-04:

- `Bookmarks` — JSON bookmark file from profile dir
- `History` — sqlite, copied from a WAL checkpoint
- `Preferences` — JSON
- `Web Data` — sqlite (search engines, autofill **off**)
- `MANIFEST.json` — see §4

**Excluded by default in v1:**

- `Login Data` (passwords) — keychain-bound; deferred to v1.1
- `Cookies`, `Network/Cookies` — high-blast-radius
- `Sessions/`, `Tabs/` — tied to local OS state
- Anything the importer would not be able to reuse cross-OS

## 6. Version negotiation

- Importer reads `format_version` first.
- If `format_version > kSupportedMaxFormatVersion`, importer refuses with `ERR_UNSUPPORTED_VERSION` and surfaces a UI message asking the user to update phlink.
- If `format_version < kSupportedMinFormatVersion`, importer refuses with `ERR_VERSION_TOO_OLD` (no v1 bundles will ever hit this; reserved for future deprecations).
- If `kdf_id` or `aead_id` is unknown, importer refuses with `ERR_UNKNOWN_PRIMITIVE`.

## 7. Failure modes (importer)

| Status code | Trigger | User message |
|-------------|---------|---------------|
| `ERR_BAD_MAGIC` | Magic ≠ `PHLB` | "This file is not a phlink bundle." |
| `ERR_UNSUPPORTED_VERSION` | `format_version` too high | "This bundle was created by a newer version of phlink. Update to import." |
| `ERR_UNKNOWN_PRIMITIVE` | Unknown KDF/AEAD id | Same as `ERR_UNSUPPORTED_VERSION`. |
| `ERR_BAD_PASSPHRASE` | AEAD tag mismatch | "Could not decrypt bundle. Check the passphrase." |
| `ERR_INTEGRITY` | sha256 mismatch on a tar entry | "Bundle integrity check failed. The file may be damaged." |
| `ERR_TRUNCATED` | EOF before declared `payload_len` + tag | Same as `ERR_INTEGRITY`. |

## 8. Reference implementation

- KDF + AEAD primitives: `//third_party/phlink_crypto/` (Rust crate, C ABI).
- Bundle codec: `chrome/browser/phlink/portability/bundle_writer.{h,cc}`, `bundle_reader.{h,cc}`.
- Service: `chrome/browser/phlink/portability/{export,import}_service.{h,cc}`.
- UI: `chrome/browser/resources/settings/portability_section/`.

## 9. Test vectors

To be added in plan 09-01 alongside the C++ smoke test. Each AEAD vector
includes (key, nonce, aad, plaintext, expected_ciphertext, expected_tag). Each
Argon2id vector follows RFC 9106 §5.

## 10. Non-goals (v1)

- Bundle signing by a phlink-vendor key — bundles are user-encrypted, not vendor-signed.
- Differential / incremental bundles.
- Cloud-hosted bundles.
- Federated identity / account-linked sync.
- Bundle preview before decryption.

## 11. Future versions (informational)

- v2 may add: opt-in password category (with separate per-category subkey), opt-in cookie category, embedded compression algorithm field (currently fixed as zstd).
- Format version bumps follow the rule: any change that the v1 reader cannot safely ignore requires a major version bump.
