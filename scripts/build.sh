#!/usr/bin/env bash
# scripts/build.sh — build phlink (currently named "chrome" pre-rename — see Phase 3).
#
# Usage:
#   bash scripts/build.sh [out-dir] [target]

set -euo pipefail

OUT_DIR="${1:-out/Default}"
TARGET="${2:-chrome}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT_DIR="$(dirname "$REPO_ROOT")"
CHROMIUM_SRC="$PARENT_DIR/chromium-src/src"

if ! command -v autoninja >/dev/null 2>&1; then
  echo "error: autoninja not on PATH. Make sure depot_tools is on PATH." >&2
  exit 1
fi

cd "$CHROMIUM_SRC"
echo "==> autoninja -C $OUT_DIR $TARGET"
autoninja -C "$OUT_DIR" "$TARGET"
