# Troubleshooting

> Solutions to common issues in the phlink alpha (dev-0.1).

---

## macOS: "phlink.app is damaged and can't be opened"

**Cause:** macOS Gatekeeper is blocking an ad-hoc–signed or unsigned build.

**Fix (downloaded installer):**

1. Right-click `phlink.app` in Finder.
2. Select **Open**.
3. Click **Open** in the dialog.

**Fix (local build from `out/Default/`):**

```sh
codesign --force --deep --sign - /path/to/out/Default/phlink.app
```

Run this command after every build.
Gatekeeper will accept the ad-hoc signature on subsequent launches.

---

## macOS: App crashes immediately after launch (local build)

**Cause:** Missing or stale codesign on the binary or a helper.

**Fix:**

```sh
codesign --force --deep --sign - /path/to/out/Default/phlink.app
```

If the crash persists, check the Console.app crash log for the specific binary or framework that was rejected.

---

## Filter lists not loading / adblock not blocking (clean profile)

**Cause:** The bundled filter lists are compiled into the binary at build time.
If you built from source and the `gen_bundled_rules.py` step was skipped or failed, the engine initialises with an empty rule set.

**Diagnosis:**

1. Open `phlink://flags`.
2. Search for `phlink-adblock`.
3. If the flag shows **Disabled**, the adblock component was not built correctly.

**Fix (build from source):**

Ensure `phlink_adblock_bundled_rules` is listed as a dependency in your `gn args` and rerun:

```sh
autoninja -C out/Default chrome
```

---

## Linux: AppImage fails to start ("FUSE not available")

**Cause:** Some Linux distributions (notably Ubuntu 22.04+) do not install FUSE 2 by default.

**Fix:**

```sh
sudo apt-get install libfuse2
```

Or extract and run without FUSE:

```sh
./phlink-*.AppImage --appimage-extract-and-run
```

---

## Windows: SmartScreen blocks the installer

**Cause:** The alpha MSI is not yet Authenticode-signed.

**Fix:**

1. Click **More info** in the SmartScreen dialog.
2. Click **Run anyway**.

SmartScreen warnings will disappear once the release MSI carries an Authenticode signature (planned for the v1.0 stable release).

---

## DNS-over-HTTPS is not working

**Verification:**

1. Navigate to `phlink://settings/security`.
2. Confirm **Use secure DNS** is toggled on.
3. The provider should show **Cloudflare (1.1.1.1)**.

If DoH appears off, check whether a system-managed policy or an enterprise MDM profile is overriding the setting.

---

## Getting help

- File a bug: [github.com/devparanjay/phlink/issues](https://github.com/devparanjay/phlink/issues)
- Developer documentation: [docs/dev/README.md](../dev/README.md)
