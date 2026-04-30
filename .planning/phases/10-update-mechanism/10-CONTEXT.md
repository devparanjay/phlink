# Phase 10 — Update Mechanism & Installers — CONTEXT

**Phase**: 10 of 12
**Goal** (from ROADMAP): Signed native installers per platform with TUF-style auto-updates and signature verification before any update is applied.
**Requirements**: UPD-01, UPD-02, UPD-03
**Depends on**: Phase 2 (CI), Phase 4 (telemetry-free), Phase 9 (proves Rust/FFI + boringssl integration patterns).
**Mode**: drafted under `gsd-discuss-phase 10 --auto` — recommended defaults locked. User may revisit any decision before plan execution.

---

## Locked decisions

### D-01 — Update framework: TUF (theupdateframework.io), in-tree C++ client

Use a **pure in-tree C++ TUF client** under
`//chrome/browser/phlink/updater/`, backed by:
- `crypto::SignatureVerifier` (Ed25519, boringssl-backed) for role signature
  verification.
- `base::JSONReader` for canonical-JSON parsing of metadata.
- `network::SimpleURLLoader` for HTTPS metadata + payload fetches.

Rationale: the Rust `tuf` crate pulls `hyper` (would duplicate Chromium's
network stack) and `ring` (conflicts with our boringssl-only crypto policy
locked in Phase 9 D-01). Re-implementing the on-disk TUF spec in ~600 LOC
of C++ is cheaper than carrying that conflict, keeps the trust boundary
inside the same boringssl + Chromium IO that everything else in phlink
already trusts, and avoids adding a Rust transitive dep audit burden.

- **Roles**: standard TUF four-role model — `root`, `targets`, `snapshot`,
  `timestamp`.
- **Key types**: Ed25519 only. RSA disallowed for v1.0.
- **Threshold**: root requires `m=2` of `n=3` for rotation; other roles `m=1`.
- **Spec compliance target**: TUF spec v1.0.32. Sub-features explicitly out
  of scope for v1.0: delegated targets, hash-algorithm-agility beyond
  SHA-256, multi-repository "TAP 4" scenarios.

### D-02 — Channels: single `stable` channel for v1.0 alpha

`dev` and `beta` channels are **deferred** to v1.1+. v1.0 ships only `stable`. The on-wire layout already accounts for multiple channels (path-prefixed targets) so the upgrade is a CDN config change, not a client change.

### D-03 — Update server: static-file CDN

No dynamic backend. Bucket layout:

```
/{channel}/metadata/{root,targets,snapshot,timestamp}.json
/{channel}/targets/phlink-{version}-{platform}-{arch}.{ext}
```

CDN choice (CloudFront / Fastly / R2) is an ops decision, not a code one. Client only needs an HTTPS base URL.

### D-04 — Key ceremony

- **Root keys**: offline, on hardware tokens (YubiKey FIPS or equivalent). Documented in `docs/dev/release-keys.md` (deliverable of plan 10-04).
- **Targets / snapshot / timestamp keys**: online, generated and held in CI secrets. Rotated every 6 months. Timestamp expires every 7 days; snapshot every 30 days; targets every 90 days; root every 365 days.

### D-05 — Update check cadence

- Background check: **24h ± 6h jitter**, only on user-active sessions. No timer fires while phlink is suspended/closed.
- Manual check: `chrome://settings/help` (already exists upstream) and `phlink://settings/help` alias.
- **Zero telemetry**: the check is a single GET for `timestamp.json`. User-Agent contains `phlink/{version} ({os}; {arch})` and nothing else. No machine ID, no install ID, no profile ID.

### D-06 — User toggle

Auto-update is **on by default**, with a single toggle in `chrome://settings/help` ("Automatically download phlink updates"). Off-by-default for enterprise/portable builds (gated by a build flag, not a runtime preference).

### D-07 — Delivery format per platform

- **macOS**: download a signed, notarized `.zip` of the new `phlink.app`. Stage into `~/Library/Application Support/phlink/Updates/{version}/`. On next launch (or via "Relaunch" button), an external `phlink_update_helper` swaps the bundle atomically (`renameat2`/`mv`) and re-launches.
- **Linux**:
  - **AppImage**: in-app updater downloads new `.AppImage`, verifies TUF target + GPG detached sig, swaps the file, restarts.
  - **`.deb` / `.rpm`**: **out-of-band** via the system package manager. The in-app updater detects these install modes and disables itself with a "Updates managed by your system package manager" notice.
- **Windows**: download signed `.exe` patch + new payload to `%LOCALAPPDATA%\phlink\Updates\{version}`. On next launch, `phlink_update_helper.exe` performs the `MoveFileEx(MOVEFILE_REPLACE_EXISTING|MOVEFILE_DELAY_UNTIL_REBOOT)` swap. `.msi` is for first install only.

### D-08 — Code signing

- **macOS**: Developer ID Application + Apple notarization. CI must hold the cert + notary credentials. **Fallback for unsigned dev builds**: ad-hoc `codesign --sign -` (already used in `scripts/build.sh`); auto-update is **disabled** at runtime when the running binary is ad-hoc-signed.
- **Windows**: Authenticode with EV cert. Same fallback rule — unsigned builds disable auto-update.
- **Linux**: GPG-signed APT/DNF repo metadata + AppImage zsync `.sig`. Detached signature verified by the updater before swap.

### D-09 — Updater telemetry: **ZERO**

PRD §10.1 hard rule. No analytics, no install pings, no failure beacons. Update failures are surfaced **only** in `chrome://settings/help` and a local log file (`~/.config/phlink/update.log`, rotated, max 1 MB).

### D-10 — Rollback

- TUF expiration on `timestamp.json` (7 days) ensures stale clients detect drift.
- Client keeps the **previous** version's bundle on disk (`Updates/{prev_version}/`) for 7 days post-update. If the new version crashes during the first 60 seconds of its first launch, the helper auto-rolls back. Best-effort, not guaranteed.
- A user-visible "Roll back last update" button is **deferred** to v1.1+.

### D-11 — In-tree boundaries

- Updater **client** lives in `chrome/browser/phlink/updater/` (C++ orchestration + Rust `tuf` crate via `cargo_crate`).
- Update **helpers** (the per-platform out-of-process swap binaries) live in `chrome/utility/phlink/update_helper_{mac,win,linux}/`.
- Installer **packaging** (`.dmg`, `.msi`, `.deb`/`.rpm`/AppImage build scripts) lives in `phlink-side` `installers/` (this repo, not chromium-src) — invoked by CI, not by the GN build.

### D-12 — Update applies before / after restart

Always **after** restart. We never hot-swap a running bundle. This keeps the trust boundary simple: the only code that can write into the install dir is the small, separately-signed `phlink_update_helper`.

---

## Plans (provisional — locked in `gsd-plan-phase 10`)

1. **10-01** — Vendor `tuf` Rust crate via gnrt + add `phlink_updater_metadata` GN target + write `docs/dev/update-protocol.md` (TUF metadata layout, key ceremony, expiration policy). [Atomic patch]
2. **10-02** — `UpdaterService` in browser process: 24h ± jitter check, downloads `timestamp.json` → `snapshot.json` → `targets.json`, stages payload to `Updates/{version}/`. Single-platform first (macOS), telemetry-free. [Atomic patch]
3. **10-03** — `phlink_update_helper` macOS swap binary (separate `executable` GN target, ad-hoc-signed in dev / Developer-ID in release). Atomic `.app` swap + relaunch. [Atomic patch]
4. **10-04** — Linux AppImage updater path + `phlink_update_helper_linux`. `.deb` / `.rpm` detect-and-disable logic. [Atomic patch]
5. **10-05** — Windows updater path + `phlink_update_helper.exe` + `MoveFileEx` swap. [Atomic patch]
6. **10-06** — `chrome://settings/help` integration: "phlink is up to date" / "Update available — relaunch to apply" / failure surface. Toggle wired to a new pref `phlink.updates.auto_check_enabled`. [Atomic patch]
7. **10-07** — `installers/` packaging scripts: `.dmg` (macOS), `.AppImage` + `.deb` + `.rpm` (Linux), `.msi` (Windows). CI invocation only. [Atomic patch]
8. **10-08** — Key-ceremony tooling + offline root keygen script + CI signing pipeline scaffold (no actual keys committed). [Atomic patch]

Plans 10-01 / 10-02 / 10-03 are the critical path for a v1.0 alpha self-update on macOS. 10-04 / 10-05 unblock cross-platform parity. 10-06 / 10-07 / 10-08 are required for shipping but lower-criticality from a code perspective.

---

## Open questions deferred to plan stage

- Exact wire format for `.zip` payload checksum: `targets.json` already carries SHA-256 per TUF; we won't add a second checksum.
- Whether to bundle `phlink_update_helper` inside `phlink.app/Contents/Helpers/` (recommended, mirrors Chromium Helper apps) or as a sibling. **Recommendation**: inside, for codesign sealing parity.
- Linux: should we ship a default `phlink.repo` (DNF) and `phlink.list` (APT) in the package post-install? **Recommendation**: yes for `.rpm`/`.deb`, no for AppImage.

These are implementation details, not blocking decisions.

---

## Out of scope for Phase 10

- Differential / binary-diff updates (Courgette / bsdiff). Deferred to v1.1+.
- Multi-channel UX (channel switcher in settings). Deferred to v1.1+.
- Enterprise mass-deployment policies (Group Policy, MDM profiles). Deferred to a dedicated phase post-v1.0.
- Crash-loop detection and rollback heuristics beyond the simple "first 60 s of first launch" rule.
