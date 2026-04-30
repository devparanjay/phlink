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
- `root.json` — signed TUF root metadata authorizing the initial role keys.
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
4. Upload `release.gpg` to the package workflow as `PHLINK_GPG_PUBLIC`.
   Local packaging can also pass `PHLINK_RELEASE_GPG=/path/to/release.gpg`;
   omission is allowed only with `PHLINK_ALLOW_MISSING_RELEASE_GPG=1` for
   smoke builds.
5. Set `phlink_updater_dev_root=false` and
   `phlink_updater_root_json="/path/to/root.json"` for release builds.
   The build copies that signed root metadata to
   `resources/phlink/keys/root.json`; macOS packaging embeds the same file
   under `Contents/Resources/phlink/keys/root.json`. Record the SHA-256 of
   this production `root.json`; release signing requires it as
   `expected_updater_root_sha256`.

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

- `package-installers.yml` consumes prebuilt Chromium outputs only after
   validating the Chromium build run's workflow path, ref, commit SHA, and
   repository. It signs and verifies macOS and Windows artifacts, validates
   `phlink_updater_dev_root=false`, records the compiled
   `phlink_product_version`, records the packaged updater root SHA-256, and
   uploads per-platform provenance manifests with artifact SHA-256 digests.
- `release-sign.yml` runs inside the `release-signing` GitHub environment. It
   validates the package workflow run, checks each provenance manifest and
   macOS/Windows platform-signing gate, verifies the Linux package public key
   hash matches `PHLINK_GPG_PUBLIC`, verifies the updater root hash matches
   `expected_updater_root_sha256`, and only then materializes
   `PHLINK_TARGETS_KEY`, `PHLINK_SNAPSHOT_KEY`, `PHLINK_TIMESTAMP_KEY`, and
   `PHLINK_GPG_SECRET`. After signing, it verifies Linux detached signatures
   with the same public key before upload.

Authenticode (Windows) and Developer ID (macOS) signing are NOT performed by
`scripts/release/sign-release.sh`. They run inside platform-specific CI runners
with protected CI credentials before `release-sign.yml` ingests the final
artifacts. Required CI credentials are `PHLINK_MACOS_DEVELOPER_ID_P12`,
`PHLINK_MACOS_DEVELOPER_ID_PASSWORD`, `PHLINK_MACOS_KEYCHAIN_PASSWORD`,
`PHLINK_APPLE_ID`, `PHLINK_APPLE_APP_PASSWORD`, `PHLINK_APPLE_TEAM_ID`,
`PHLINK_WINDOWS_SIGNING_CERT_PFX`, `PHLINK_WINDOWS_SIGNING_CERT_PASSWORD`,
and `PHLINK_GPG_PUBLIC`.

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
