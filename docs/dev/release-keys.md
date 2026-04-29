# Release keys

phlink's release-signing infrastructure is split across the TUF role keys,
Linux package-signing key, and platform code-signing credentials:

| Key                | Purpose                                                           | Where it lives                              |
| ------------------ | ----------------------------------------------------------------- | ------------------------------------------- |
| **TUF root**       | Re-signs `root.json` on key-rotation. Highest-value secret.       | Air-gapped USB drive, in two physical safes |
| **TUF targets**    | Signs `targets.json` per release                                  | GitHub Actions secret (`PHLINK_TARGETS_KEY`) |
| **TUF snapshot**   | Signs `snapshot.json` per release                                 | GitHub Actions secret (`PHLINK_SNAPSHOT_KEY`) |
| **TUF timestamp**  | Signs `timestamp.json` per release                                | GitHub Actions secret (`PHLINK_TIMESTAMP_KEY`) |
| **gpg release**    | Detached signatures on `.deb` / `.rpm` / `.AppImage`              | GitHub Actions secret (`PHLINK_GPG_SECRET`)  |
| **EV Authenticode** | Signs `phlink.exe` and the MSI on Windows                       | EV smart-card / HSM in CI's Windows runner  |
| **Developer ID**   | Signs `phlink.app` and the dmg on macOS                          | Apple Developer account; CI keychain unlock |

## Initial generation (one-time ceremony)

Run once on a hardened workstation (preferably air-gapped Linux live USB):

```sh
scripts/release/keygen.sh ~/phlink-keys
```

This produces:

- `root.{key,pub}` — Ed25519, used to sign `root.json`.
- `targets.{key,pub}` — Ed25519, used to sign `targets.json`.
- `snapshot.{key,pub}` — Ed25519, used to sign `snapshot.json`.
- `timestamp.{key,pub}` — Ed25519, used to sign `timestamp.json`.
- `release.gpg` — public part for bundling into linux installers.
- `release.gpg.secret` — secret part for CI signing.

**Immediately after generation:**

1. Copy `root.key` and `release.gpg.secret` to two USB drives, place
   each in a separate physical safe.
2. `shred -u` the on-disk copies of both.
3. Upload `targets.key`, `snapshot.key`, `timestamp.key`, and
   `release.gpg.secret` to GitHub Actions secrets (`PHLINK_TARGETS_KEY`,
   `PHLINK_SNAPSHOT_KEY`, `PHLINK_TIMESTAMP_KEY`, `PHLINK_GPG_SECRET`).
   These keys are hot because release cadence requires them; mitigation is
   short metadata expiry (7 days for timestamp, 30 for snapshot, 90 for
   targets; see `sign-release.sh`).
4. Bundle `release.gpg` into the linux installers
   (`installers/linux/build-packages.sh` reads it from
   `branding/release.gpg`).
5. Replace the dev TUF root in
   `chromium-src/src/chrome/browser/phlink/updater/keys/dev_root.json`
   with a production `root.json` signed by `root.key`. This is a
   chromium-side patch (not yet authored; deferred to v1.0 alpha
   tag).

## Per-release signing (CI)

```sh
scripts/release/sign-release.sh \
  ./artifacts \
  0.1.0 \
  $RUNNER_TEMP/targets.key \
   $RUNNER_TEMP/snapshot.key \
   $RUNNER_TEMP/timestamp.key \
  $RUNNER_TEMP/release.gpg.secret
```

Produces:

- `targets.json` — signed with `targets.key`.
- `snapshot.json` — signed with `snapshot.key`.
- `timestamp.json` — signed with `timestamp.key`.
- `<artifact>.sig` — gpg detached signatures for each linux artifact.

`root.json` remains offline-only and is regenerated during root or delegated
role key rotation.

## Authenticode + Developer ID

The checked-in CI scaffold is split across two manual workflows:

- `package-installers.yml` consumes prebuilt Chromium outputs and creates
   unsigned/signable installer artifacts.
- `release-sign.yml` runs inside the `release-signing` GitHub environment and
   signs TUF targets metadata plus Linux detached signatures using
   `PHLINK_TARGETS_KEY`, `PHLINK_SNAPSHOT_KEY`, `PHLINK_TIMESTAMP_KEY`, and
   `PHLINK_GPG_SECRET`.

Authenticode (Windows) and Developer ID (macOS) signing are NOT performed by
`scripts/release/sign-release.sh`. They run inside platform-specific CI runners
with hardware-backed credentials before `release-sign.yml` ingests the final
artifacts.

## Key rotation

Targets, snapshot, and timestamp key rotation is online except for the root
metadata update that authorizes the replacement key:

1. Generate the replacement delegated role key (offline).
2. Sign new `root.json` adding the new key, removing the old, on the
   air-gapped host.
3. Upload the new private key to the matching GitHub Actions secret.
4. Push new `root.json` to the metadata server. Clients refresh root
   per TUF spec; old clients pin the old root and fall back to the
   new on next root-step ladder.

Root-key rotation is a coordinated event documented in a separate
runbook (TODO).
