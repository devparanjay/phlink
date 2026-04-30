# Plan 10-01 — TUF protocol spec + in-tree C++ client skeleton

**Phase**: 10
**Plan**: 10-01
**Atomic patch slot**: 0124
**Depends on**: nothing in Phase 10 (foundation)
**Blocks**: 10-02..10-08

## Outcome

1. `docs/dev/update-protocol.md` — full protocol spec (repo layout, role
   files, threshold + expiration policy, canonical-JSON rules, key
   rotation, threat model, client trust pinning).
2. `//chrome/browser/phlink/updater:metadata` GN target with
   `metadata_client.{h,cc}` providing the `TufClient` C++ surface — pure
   in-tree, backed by `crypto::SignatureVerifier` (Ed25519) + `base::JSONReader`
   + `network::SimpleURLLoader`. **No Rust crate vendoring** (see CONTEXT D-01
   pivot).
3. Dev-only `root.json` committed under
   `chrome/browser/phlink/updater/keys/dev_root.json` plus build flag
   `phlink_updater_dev_root` selecting it. Production root is **not**
   committed.
4. Unit tests under `phlink_updater_unittests`:
   `AcceptsValidMetadata`, `RejectsExpiredTimestamp`, `RejectsRollback`,
   `RejectsBadSignature`.

## Steps

1. Author `docs/dev/update-protocol.md` (all 8 sections per CONTEXT D-01..D-12).
2. Generate a dev keyset (Ed25519, offline) and commit only the **public**
   half as `dev_root.json`.
3. Implement `TufClient` C++ surface:
   - `class TufClient { Status FetchTimestamp(); Status FetchSnapshot();
     Status FetchTargets(); std::optional<TargetMeta> LookupTarget(
     std::string_view name) const; }`.
   - Verifies role chain (root signs timestamp+snapshot+targets keys),
     enforces expiration, enforces threshold counts, enforces version
     monotonicity (rollback rejection).
4. Wire build flag + dev root.
5. Unit tests with an in-test fixture TUF repo built at SetUp() using a
   tiny Ed25519 keypair (no network).

## Verification

- `phlink_updater_unittests` green for the 4 named tests.
- `gn check` clean.
- `chrome` builds + codesigns.
- Protocol doc reviewed against PRD §10.1 + Phase 10 CONTEXT D-01..D-04, D-09.

## Out of scope

- Any payload download (10-02).
- Any platform-specific swap helper (10-03..10-05).
- Any UI surface (10-06).
- Real production root keys (10-08).
