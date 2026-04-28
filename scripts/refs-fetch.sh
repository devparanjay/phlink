#!/usr/bin/env bash
# scripts/refs-fetch.sh — download an upstream docs snapshot into .refs/.
#
# Usage:
#   bash scripts/refs-fetch.sh \
#     --name <project> --version <version> --ecosystem <bucket> \
#     --url <source-url> --license <SPDX-id> [--notes "..."] [--dry-run]
#
# Layout produced:
#   .refs/<ecosystem>/<name>@<version>/source.<ext>
#   .refs/<ecosystem>/<name>@<version>/MANIFEST.json
#
# Validates MANIFEST.json against scripts/refs/MANIFEST.schema.json
# (best-effort — skipped if `python3 -m jsonschema` is unavailable).

set -euo pipefail

usage() {
  sed -n '2,16p' "$0"
}

NAME=""
VERSION=""
ECOSYSTEM=""
URL=""
LICENSE=""
NOTES=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --name)      NAME="$2"; shift 2 ;;
    --version)   VERSION="$2"; shift 2 ;;
    --ecosystem) ECOSYSTEM="$2"; shift 2 ;;
    --url)       URL="$2"; shift 2 ;;
    --license)   LICENSE="$2"; shift 2 ;;
    --notes)     NOTES="$2"; shift 2 ;;
    --dry-run)   DRY_RUN=1; shift ;;
    -h|--help)   usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

for required in NAME VERSION ECOSYSTEM URL LICENSE; do
  if [ -z "${!required}" ]; then
    echo "error: --${required,,} is required" >&2
    usage
    exit 2
  fi
done

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMA="$REPO_ROOT/scripts/refs/MANIFEST.schema.json"
DEST="$REPO_ROOT/.refs/$ECOSYSTEM/$NAME@$VERSION"
mkdir -p "$DEST"

FETCH_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EXT="${URL##*.}"
case "$EXT" in
  tar.gz|tgz|tar|zip|gz|bz2|xz|html|md|txt|json) : ;;
  *) EXT="bin" ;;
esac
SOURCE_PATH="$DEST/source.$EXT"

if [ "$DRY_RUN" -eq 1 ]; then
  echo "[dry-run] would download $URL -> $SOURCE_PATH"
  SHA256="0000000000000000000000000000000000000000000000000000000000000000"
else
  echo "==> downloading $URL"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" -o "$SOURCE_PATH"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$URL" -O "$SOURCE_PATH"
  else
    echo "error: neither curl nor wget is available" >&2
    exit 1
  fi
  SHA256="$(shasum -a 256 "$SOURCE_PATH" | awk '{print $1}')"
fi

cat > "$DEST/MANIFEST.json" <<EOF
{
  "name": "$NAME",
  "version": "$VERSION",
  "ecosystem": "$ECOSYSTEM",
  "source_url": "$URL",
  "fetch_date": "$FETCH_DATE",
  "license": "$LICENSE",
  "sha256_of_archive": "$SHA256"$( [ -n "$NOTES" ] && printf ',\n  "notes": "%s"' "$NOTES" )
}
EOF

echo "==> wrote $DEST/MANIFEST.json"

# Best-effort schema validation
if command -v python3 >/dev/null 2>&1 && python3 -c "import jsonschema" 2>/dev/null; then
  python3 -c "
import json, sys
import jsonschema
schema = json.load(open('$SCHEMA'))
inst = json.load(open('$DEST/MANIFEST.json'))
jsonschema.validate(inst, schema)
print('==> MANIFEST.json validates against schema')
"
else
  echo "==> (skipped schema validation: python3 / jsonschema not available)"
fi
