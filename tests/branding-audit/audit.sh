#!/usr/bin/env bash
# tests/branding-audit/audit.sh
#
# Phase 4.7 (BRND-01): regression gate that asserts no unexpected
# "Chromium" / "Google Chrome" strings leaked into the built phlink bundle.
#
# Usage:
#   PHLINK_APP=/path/to/phlink.app ./audit.sh           # explicit
#   ./audit.sh                                          # uses PHLINK_BINARY env (parent dir)
#                                                       # or default chromium-src out path
#
# Exit codes:
#   0  — all matches accounted for in allowlist.txt
#   1  — unexpected matches found
#   2  — bundle not found / setup error

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALLOWLIST="$SCRIPT_DIR/allowlist.txt"

# Resolve the bundle.
if [[ -n "${PHLINK_APP:-}" ]]; then
  APP="$PHLINK_APP"
elif [[ -n "${PHLINK_BINARY:-}" ]]; then
  # PHLINK_BINARY points at .../phlink.app/Contents/MacOS/phlink
  APP="$(dirname "$(dirname "$(dirname "$PHLINK_BINARY")")")"
else
  APP="/Volumes/Tools/dev/chromium-src/src/out/Default/phlink.app"
fi

if [[ ! -d "$APP" ]]; then
  echo "branding-audit: bundle not found at $APP" >&2
  exit 2
fi

MAIN_BIN="$APP/Contents/MacOS/phlink"
FRAMEWORK_DIR="$APP/Contents/Frameworks/phlink Framework.framework/Versions"
if [[ ! -d "$FRAMEWORK_DIR" ]]; then
  echo "branding-audit: framework dir not found under $APP" >&2
  exit 2
fi
# Resolve the versioned framework binary (single subdir typically).
FRAMEWORK_VERSION="$(ls "$FRAMEWORK_DIR" | head -1)"
FRAMEWORK_BIN="$FRAMEWORK_DIR/$FRAMEWORK_VERSION/phlink Framework"

if [[ ! -f "$MAIN_BIN" || ! -f "$FRAMEWORK_BIN" ]]; then
  echo "branding-audit: missing main or framework binary" >&2
  exit 2
fi

# Strip allowlist comments + blanks; treat each remaining line as a fixed string.
# Portable alternative to `mapfile` (macOS bash 3.2 doesn't have it).
ALLOW=()
while IFS= read -r _line; do
  ALLOW+=("$_line")
done < <(grep -vE '^\s*(#|$)' "$ALLOWLIST" || true)

scan() {
  local file="$1"
  strings "$file" | grep -iE '\bchromium\b|google chrome' || true
}

UNEXPECTED=()
TOTAL=0
ACCOUNTED=0

# Lowercase the allowlist once for case-insensitive substring matching.
ALLOW_LC=()
for pat in "${ALLOW[@]}"; do
  ALLOW_LC+=("$(printf '%s' "$pat" | tr '[:upper:]' '[:lower:]')")
done

while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  TOTAL=$((TOTAL+1))
  line_lc="$(printf '%s' "$line" | tr '[:upper:]' '[:lower:]')"
  matched=0
  for pat in "${ALLOW_LC[@]}"; do
    if [[ "$line_lc" == *"$pat"* ]]; then
      matched=1
      break
    fi
  done
  if [[ "$matched" -eq 1 ]]; then
    ACCOUNTED=$((ACCOUNTED+1))
  else
    UNEXPECTED+=("$line")
  fi
done < <(scan "$MAIN_BIN"; scan "$FRAMEWORK_BIN")

if [[ ${#UNEXPECTED[@]} -gt 0 ]]; then
  echo "branding-audit: FAIL — $TOTAL matches scanned, $ACCOUNTED on allowlist, ${#UNEXPECTED[@]} unexpected:" >&2
  printf '  %s\n' "${UNEXPECTED[@]}" | sort -u >&2
  exit 1
fi

echo "branding-audit: PASS — $TOTAL strings matched, all on allowlist."
exit 0
