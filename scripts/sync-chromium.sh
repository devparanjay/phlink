#!/usr/bin/env bash
# scripts/sync-chromium.sh — fetch and sync Chromium stable into ../chromium-src/.
#
# Usage:
#   bash scripts/sync-chromium.sh [--channel stable]
#
# Requires depot_tools on PATH (run scripts/bootstrap.sh first).

set -euo pipefail

CHANNEL="${1:-stable}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT_DIR="$(dirname "$REPO_ROOT")"
CHROMIUM_SRC="$PARENT_DIR/chromium-src"

if ! command -v fetch >/dev/null 2>&1; then
  echo "error: depot_tools not on PATH. Run scripts/bootstrap.sh and add depot_tools to PATH." >&2
  exit 1
fi

mkdir -p "$CHROMIUM_SRC"
cd "$CHROMIUM_SRC"

if [ ! -d src ]; then
  echo "==> fetching Chromium (this will take a long time)"
  if [ "$(uname -s)" = "Darwin" ]; then
    caffeinate fetch chromium
  else
    fetch chromium
  fi
else
  echo "==> Chromium already fetched, syncing"
  cd src
  git fetch origin
  cd ..
  gclient sync -r "src@refs/branch-heads/$CHANNEL"
fi

echo "==> sync complete: $CHROMIUM_SRC/src"
