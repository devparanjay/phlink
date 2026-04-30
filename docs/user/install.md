# Installing phlink

> Step-by-step installation instructions for macOS, Linux, and Windows.
> These instructions cover the current alpha (dev-0.1) builds.

## macOS

### Download

Download the latest `.dmg` from the [GitHub releases page](https://github.com/devparanjay/phlink/releases).

### Install

1. Open the downloaded `.dmg`.
2. Drag `phlink.app` to your `Applications` folder.
3. Eject the disk image.

### First launch (ad-hoc–signed build)

macOS Gatekeeper will block an unsigned or ad-hoc–signed build.
To open it the first time:

1. Right-click (or Control-click) `phlink.app` in Applications.
2. Select **Open**.
3. Click **Open** in the confirmation dialog.

> **Note (alpha):** Developer builds from `out/Default/` (built locally from source) require
> an additional codesign step before Gatekeeper allows launch:
>
> ```sh
> codesign --force --deep --sign - /path/to/out/Default/phlink.app
> ```
>
> Run this once after each build; the ad-hoc signature persists across relaunches
> until the next link.

### Verify

Open phlink and navigate to `phlink://version`.
The version string should match the release tag.

---

## Linux

### AppImage (recommended)

1. Download the `.AppImage` file from the releases page.
2. Make it executable:
   ```sh
   chmod +x phlink-*.AppImage
   ```
3. Launch it:
   ```sh
   ./phlink-*.AppImage
   ```
   No system-wide installation required.

### Debian / Ubuntu (`.deb`)

```sh
sudo dpkg -i phlink_*.deb
sudo apt-get install -f   # resolve any missing dependencies
```

Launch from your application menu or run `phlink` in a terminal.

### Fedora / RHEL (`.rpm`)

```sh
sudo rpm -i phlink_*.rpm
```

### Verify

```sh
phlink --version
```

---

## Windows

### Installer (`.msi`)

1. Download `phlink-*.msi` from the releases page.
2. Double-click the installer.
3. Accept the UAC prompt (if shown) and follow the wizard.
   The default install path is `%LocalAppData%\phlink\`.
4. Launch phlink from the Start menu or `phlink.exe`.

> **Note (alpha):** Authenticode signing is not yet applied to alpha builds.
> Windows SmartScreen may display a warning on first run.
> Click **More info → Run anyway** to proceed.

### Verify

Navigate to `phlink://version` in the address bar.

---

## Building from source

See [docs/dev/build.md](../dev/build.md) for the full developer build guide covering all three platforms.
