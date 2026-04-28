#!/usr/bin/env bash
# scripts/gn-gen.sh — generate a Chromium build dir using phlink's GN args baseline.
#
# Usage:
#   bash scripts/gn-gen.sh [out-dir]
#
# Default out-dir is "out/Default" inside ../chromium-src/src/.

set -euo pipefail

OUT_DIR="${1:-out/Default}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT_DIR="$(dirname "$REPO_ROOT")"
CHROMIUM_SRC="$PARENT_DIR/chromium-src/src"

case "$(uname -s)" in
  Darwin) PLATFORM_FILE="$REPO_ROOT/build/gn-args/mac.gn" ;;
  Linux)  PLATFORM_FILE="$REPO_ROOT/build/gn-args/linux.gn" ;;
  *)
    echo "error: unsupported platform $(uname -s). Use scripts/gn-gen.ps1 on Windows." >&2
    exit 1 ;;
esac
COMMON_FILE="$REPO_ROOT/build/gn-args/common.gni"

if [ ! -d "$CHROMIUM_SRC" ]; then
  echo "error: Chromium source not found at $CHROMIUM_SRC. Run scripts/sync-chromium.sh first." >&2
  exit 1
fi

if ! command -v gn >/dev/null 2>&1; then
  echo "error: gn not on PATH. Make sure depot_tools is on PATH." >&2
  exit 1
fi

# Concatenate common + platform args, strip comments and blank lines, join with spaces.
ARGS=$(cat "$COMMON_FILE" "$PLATFORM_FILE" | sed -e 's/#.*$//' -e '/^[[:space:]]*$/d' | tr '\n' ' ')

echo "==> generating $CHROMIUM_SRC/$OUT_DIR with args from $COMMON_FILE + $PLATFORM_FILE"
cd "$CHROMIUM_SRC"
gn gen "$OUT_DIR" --args="$ARGS"
