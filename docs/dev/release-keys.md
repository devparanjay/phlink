# Release keys

phlink's release-signing infrastructure is split into three keys:

| Key                | Purpose                                                           | Where it lives                              |
| ------------------ | ----------------------------------------------------------------- | ------------------------------------------- |
| **TUF root**       | Re-signs `root.json` on key-rotation. Highest-value secret.       | Air-gapped USB drive, in two physical safes |
| **TUF targets**    | Signs `targets.json`, `snapshot.json`, `timestamp.json` per release | GitHub Actions secret (`PHLINK_TARGETS_KEY`) |
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
- `targets.{key,pub}` — Ed25519, used to sign per-release metadata.
- `release.gpg` — public part for bundling into linux installers.
- `release.gpg.secret` — secret part; air-gap it.

**Immediately after generation:**

1. Copy `root.key` and `release.gpg.secret` to two USB drives, place
   each in a separate physical safe.
2. `shred -u` the on-disk copies of both.
3. Upload `targets.key` and `release.gpg.secret` to GitHub Actions
   secrets (`PHLINK_TARGETS_KEY`, `PHLINK_GPG_SECRET`). The targets
   key is hot because release cadence requires it; mitigation is
   short expiry (30 days, see `sign-release.sh`).
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
  $RUNNER_TEMP/release.gpg.secret
```

Produces:

- `targets.json` — signed with `targets.key`.
- `<artifact>.sig` — gpg detached signatures for each linux artifact.

`snapshot.json` and `timestamp.json` are produced on the air-gapped
signing host and committed to the metadata repo manually for now.
A future patch will move snapshot/timestamp signing online (still
with the targets key) once we have a hosted metadata service.

## Authenticode + Developer ID

Authenticode (Windows) and Developer ID (macOS) signing are NOT
performed by these scripts. They run inside platform-specific CI
runners with hardware-backed credentials and are configured in
`.github/workflows/release.yml` (see plan 10-08b).

## Key rotation

Targets-key rotation is online:

1. Generate new targets key (offline).
2. Sign new `root.json` adding the new key, removing the old, on the
   air-gapped host.
3. Upload new `targets.key` to GitHub Actions secret.
4. Push new `root.json` to the metadata server. Clients refresh root
   per TUF spec; old clients pin the old root and fall back to the
   new on next root-step ladder.

Root-key rotation is a coordinated event documented in a separate
runbook (TODO).
