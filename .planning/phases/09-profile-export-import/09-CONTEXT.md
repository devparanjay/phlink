# Phase 9 — Profile Export/Import — CONTEXT

**Phase**: 9
**Slug**: `09-profile-export-import`
**Authored**: 2026-04-29 (`/gsd-discuss-phase 9 --chain`)
**Goal**: Local, encrypted, cross-platform profile-bundle export and import. No cloud sync.
**PRD refs**: §3.5 (Sync v1), §10.1 row "Sync (v1)". **Hard PRD lock**: NO cloud endpoint exists.
**Requirements**: PROF-01, PROF-02, PROF-03.
**Plans (atomic)**:
  - 09-01: Encrypted bundle format spec + crypto primitives
  - 09-02: Export flow (UI + serializer)
  - 09-03: Import flow (UI + verifier + new-profile creation)

---

## Locked decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| **D-01** | KDF: **Argon2id**, m=64 MiB, t=3, p=1, 16-byte salt | OWASP-recommended; GPU/ASIC-resistant; ~500ms on M1 acceptable for export/import. |
| **D-02** | AEAD: **XChaCha20-Poly1305**, 24-byte nonce (random) | 192-bit nonce is random-safe (no counter management). Fast on ARM without AES-NI. boringssl already vendors `chacha20_poly1305`; XChaCha extension is a thin wrapper (~50 LOC) — vendor as a small Rust crate inside `//third_party/phlink_crypto/`. |
| **D-03** | Container: **custom binary header + AEAD-encrypted `tar.zst` payload**. Magic `PHLB`, version u16, kdf-params, salt, nonce, ciphertext, AEAD tag. Streamable. File extension `.phlinkbundle`. | Single file is the most user-friendly artifact. Header+payload separation lets us version the format without re-encrypting payload. tar.zst is the canonical serialization for nested directory trees. |
| **D-04** | Default contents: **bookmarks, history, settings (Preferences JSON), extensions list (IDs + manifest version, NOT extension state/storage), site-engagement scores, search engines.** **NO passwords, NO cookies, NO autofill, NO open tabs by default.** | Smallest blast radius if a bundle is mishandled; passwords/cookies require separate opt-in (deferred to v1.1). Matches PRD §3.5 "no cloud sync" posture extended to local exports. |
| **D-05** | Import semantics: **always create a NEW profile** from the bundle. Never overwrite or merge into the active profile. New profile is named `Imported <timestamp>` and selectable from the profile picker. | Zero data loss; deterministic semantics; deletion of old profile remains a manual user action. |
| **D-06** | UI: **`chrome://settings/portability`** under a new "Profile portability" section. Two cards: Export (passphrase entry, scope checklist preview, save dialog) and Import (file picker, passphrase entry, "create new profile" confirmation). | Discoverable; reuses Phase 8.6 settings surface; consistent with phlink's settings-first posture. |
| **D-07** | Keychain integration: **bundle passphrase NEVER touches OS keychain.** OS keychain continues to hold ONLY the existing Chromium password-store key. User must memorize / write down the bundle passphrase. | Keeps bundle fully portable + self-contained. Eliminates "user forgot passphrase but it's in keychain on another device" UX trap. v1.1 may add opt-in caching. |
| **D-08** | Hard NO cloud endpoints, telemetry, or "phone-home" probes. No HTTP requests issued by export or import code paths. | PRD §10.1 row "Telemetry: None"; PRD §10.1 row "Sync (v1): Local encrypted only"; reinforced by phlink security posture (copilot-instructions §3.2). |
| **D-09** | Cross-platform: bundle format is byte-identical across macOS / Linux / Windows. tar payload uses POSIX entries; paths stored as forward-slash UTF-8; timestamps stored as int64 unix-epoch nanoseconds. No host-specific paths or registry keys inside the payload. | PRD requires cross-platform import. |
| **D-10** | Verification: SHA-256 of payload-plaintext is included as a tar entry `MANIFEST.json` field; AEAD tag covers entire encrypted payload. Import refuses bundles where AEAD tag fails OR `MANIFEST.json::format_version` exceeds the importer's supported max. | Belt-and-suspenders integrity. AEAD alone suffices for tamper detection; the SHA-256 is a debug aid + future re-encrypt support. |

---

## Out of scope (Phase 9)

- Password / cookie / autofill / open-tab export (deferred to v1.1; explicit UI checkbox locked off in v1).
- Cloud sync, account-bound sync, federated sync — **PRD-locked off forever in v1**.
- Bundle inspection / preview UI (deferred).
- Differential / incremental bundle exports.
- Bundle signing by a phlink key (bundles are user-encrypted, not vendor-signed).
- CLI export tooling (deferred to Phase 11 / dev tooling).

## Touchpoints (research preview)

- **chromium-src**: `chrome/browser/profiles/` (profile creation), `components/sync/` (we explicitly DO NOT use), `chrome/browser/ui/webui/settings/` (new portability section), `components/bookmarks/`, `components/history/`, `components/prefs/`.
- **phlink**: new `//third_party/phlink_crypto/` (Rust crate w/ Argon2id + XChaCha20-Poly1305), new `chrome/browser/phlink/portability/` (C++ glue), `chrome/browser/resources/settings/portability_section/` (TS + HTML).
- **Patches projected**: 0118 (crypto crate vendor + GN), 0119 (bundle codec C++ wrapper), 0120 (export/import service), 0121 (settings UI section).

## Verification plan

- Unit tests: KDF vector tests (Argon2 RFC 9106), AEAD vector tests, tar round-trip.
- Integration: export a profile → wipe `--user-data-dir` → import bundle → verify bookmarks/history/settings restored byte-equivalent.
- Cross-platform: run integration on macOS + Linux + Windows runners, byte-compare bundles.
- Branding: phlink-runtime-audit additions for `chrome://settings/portability` and `phlink://settings/portability`.
- Network: zero outbound HTTP during export or import (asserted via `tests/network-capture/`).
