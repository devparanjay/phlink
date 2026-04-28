# Building phlink locally

> phlink is a Chromium-based browser. Building it requires fetching ~50 GB of Chromium source, ~100 GB of free disk space, and a long initial compile (~1–6 hours depending on hardware). This document walks you through it on macOS, Linux, and Windows.

## Prerequisites

Common to every platform:

- **Git** ≥ 2.30
- **Python** 3.11+
- **~100 GB free disk** in the directory containing this repo
- **~16 GB RAM** (more is faster)

Per-platform tooling:

| Platform | What you need |
|---|---|
| **macOS 12+** | Xcode + command line tools (`xcode-select --install`). Apple Silicon (`arm64`) and Intel both work. |
| **Linux** | A glibc distro on `x86_64`. Ubuntu 22.04+ is the smoothest. Required system packages are installed by depot_tools' `install-build-deps.sh` (see below). |
| **Windows 10/11 (x64)** | Visual Studio 2022 (Community is fine) with the "Desktop development with C++" workload, the Windows 11 SDK (10.0.22621.x), and the WDK. PowerShell 7+. |

phlink does **not** support 32-bit builds.

## 1. Clone phlink and bootstrap

```bash
git clone https://github.com/devparanjay/phlink.git
cd phlink
```

### macOS / Linux

```bash
bash scripts/bootstrap.sh
```

This clones [depot_tools](https://chromium.googlesource.com/chromium/tools/depot_tools.git) to `~/depot_tools` and prints the `PATH` line you need to add to your shell rc (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
export PATH="$HOME/depot_tools:$PATH"
```

### Windows (PowerShell)

```powershell
pwsh scripts/bootstrap.ps1
```

This clones depot_tools to `%USERPROFILE%\depot_tools`. Add it to your PATH for the session:

```powershell
$env:PATH = "$env:USERPROFILE\depot_tools;$env:PATH"
```

To persist, add the same line to your PowerShell profile (`$PROFILE`).

## 2. Fetch Chromium source

This is the slow step. The Chromium source lives **outside** this repo, as a sibling directory:

```
your-workspace/
├── phlink/           # this repo
└── chromium-src/     # Chromium source (created by sync-chromium)
    └── src/
```

### macOS / Linux

```bash
bash scripts/sync-chromium.sh
```

On macOS this wraps the command in `caffeinate` so the machine doesn't sleep during the multi-hour fetch.

On Linux, after the first sync completes, install Chromium's build dependencies:

```bash
cd ../chromium-src/src
./build/install-build-deps.sh
```

### Windows

```powershell
pwsh scripts/sync-chromium.ps1
```

You may need to run this from a "Developer PowerShell for VS 2022" prompt so MSVC tools are on PATH.

## 3. Generate a build directory

```bash
# macOS / Linux
bash scripts/gn-gen.sh

# Windows
pwsh scripts/gn-gen.ps1
```

This concatenates [`build/gn-args/common.gni`](../../build/gn-args/common.gni) with the platform-specific args ([`linux.gn`](../../build/gn-args/linux.gn) / [`mac.gn`](../../build/gn-args/mac.gn) / [`win.gn`](../../build/gn-args/win.gn)) and runs `gn gen out/Default --args="…"` inside `../chromium-src/src/`.

If you want to inspect or tweak the GN args interactively:

```bash
cd ../chromium-src/src
gn args out/Default
```

## 4. Apply phlink patches (Phase 3+ only)

In Phase 1 (where this doc was written), `patches/` is empty and this step is a no-op:

```bash
python3 scripts/apply-patches.py
```

Once real patches exist, run this between `gn-gen` and `build`. The script refuses to apply over a dirty Chromium tree unless you pass `--force`. See [patches/README.md](../../patches/README.md).

## 5. Build

```bash
# macOS / Linux
bash scripts/build.sh

# Windows
pwsh scripts/build.ps1
```

This runs `autoninja -C out/Default chrome` inside the Chromium checkout. The first build takes hours; incremental builds are much faster.

The output binary is currently named `chrome` (or `Chromium.app` on macOS). The phlink rename happens in **Phase 3 — Identity & Branding Strip**.

### Running unit tests

```bash
cd ../chromium-src/src
autoninja -C out/Default unit_tests
out/Default/unit_tests --gtest_filter=YourFilter
```

## Build accelerator (recommended)

[`sccache`](https://github.com/mozilla/sccache) (Apache-2.0/MIT, OSS) caches compiler outputs and dramatically speeds up rebuilds and CI. It's not required for a one-off build but it pays for itself the second time you compile.

```bash
# macOS
brew install sccache

# Linux
cargo install sccache    # or distro package manager

# Windows
scoop install sccache    # or cargo install sccache
```

Then point Chromium at it via `cc_wrapper`:

```bash
echo 'cc_wrapper = "sccache"' >> ../chromium-src/src/out/Default/args.gn
gn gen ../chromium-src/src/out/Default
```

`ccache` works similarly on macOS/Linux. **`goma` and `reclient` are not supported** — they require Google-internal infrastructure and don't fit phlink's "OSS-friendly" stance.

## Common issues

**"`fetch: command not found`"** — depot_tools isn't on your PATH. Re-run the bootstrap step's PATH instructions.

**"out of disk space"** — Chromium genuinely needs ~100 GB. Try a different drive: `bash scripts/bootstrap.sh --force` after moving `../chromium-src/`.

**"too many open files" (macOS)** — bump the limit: `ulimit -n 8192`.

**"build hangs at link step"** — link is RAM-heavy. Set `is_component_build = true` in `args.gn` for development; component builds link faster but produce many `.dylib`/`.so`/`.dll` shards.

**"`gclient sync` fails on Windows"** — make sure you have long-paths support enabled (`git config --system core.longpaths true`) and antivirus exclusions for both `chromium-src\` and your depot_tools dir.

## What's next

Once you have a working binary, see [docs/dev/upstream-tracking.md](upstream-tracking.md) for how phlink stays in sync with Chromium stable and how to author a new patch.
