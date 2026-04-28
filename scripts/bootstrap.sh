#!/usr/bin/env bash
# scripts/bootstrap.sh — install depot_tools and prepare the Chromium checkout location.
#
# Usage:
#   bash scripts/bootstrap.sh [--force]
#
# What it does:
#   1. Clones depot_tools to ~/depot_tools (if not already present).
#   2. Prints PATH setup instructions (does NOT modify your shell rc).
#   3. Verifies disk space and prints next steps.
#
# What it does NOT do:
#   - Modify your shell rc files.
#   - Run gclient sync (use scripts/sync-chromium.sh for that).
#
# Refuses to run if ../chromium-src already exists, unless --force is passed.

set -euo pipefail

FORCE=0
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0 ;;
    *)
      echo "error: unknown argument: $arg" >&2
      exit 2 ;;
  esac
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT_DIR="$(dirname "$REPO_ROOT")"
CHROMIUM_SRC="$PARENT_DIR/chromium-src"
DEPOT_TOOLS_DIR="${DEPOT_TOOLS_DIR:-$HOME/depot_tools}"

echo "==> phlink bootstrap"
echo "    repo:           $REPO_ROOT"
echo "    chromium-src:   $CHROMIUM_SRC (sibling)"
echo "    depot_tools:    $DEPOT_TOOLS_DIR"

case "$(uname -s)" in
  Darwin) PLATFORM="mac" ;;
  Linux)  PLATFORM="linux" ;;
  *)
    echo "error: unsupported platform $(uname -s). Use scripts/bootstrap.ps1 on Windows." >&2
    exit 1 ;;
esac

# 1. depot_tools
if [ -d "$DEPOT_TOOLS_DIR/.git" ]; then
  echo "==> depot_tools already cloned at $DEPOT_TOOLS_DIR"
else
  echo "==> cloning depot_tools"
  git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git "$DEPOT_TOOLS_DIR"
fi

# 2. ../chromium-src guardrail
if [ -e "$CHROMIUM_SRC" ] && [ "$FORCE" -ne 1 ]; then
  echo "error: $CHROMIUM_SRC already exists. Re-run with --force to ignore this check." >&2
  exit 1
fi

# 3. Disk space check (Chromium needs ~100 GB)
AVAIL_KB=$(df -k "$PARENT_DIR" | awk 'NR==2 {print $4}')
AVAIL_GB=$((AVAIL_KB / 1024 / 1024))
if [ "$AVAIL_GB" -lt 100 ]; then
  echo "warn: only ${AVAIL_GB} GB free at $PARENT_DIR. Chromium needs ~100 GB."
fi

cat <<EOF

==> bootstrap complete

Next steps:

  1. Add depot_tools to your PATH (do this in your shell rc):

       export PATH="$DEPOT_TOOLS_DIR:\$PATH"

  2. Fetch Chromium source (this will take a long time and a lot of disk):

       bash scripts/sync-chromium.sh

  3. Generate a build directory and build:

       bash scripts/gn-gen.sh
       bash scripts/build.sh

  See docs/dev/build.md for the full procedure on platform $PLATFORM.

EOF
