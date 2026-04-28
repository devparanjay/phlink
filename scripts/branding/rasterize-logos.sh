#!/usr/bin/env bash
# Rasterize phlink branding SVGs into the PNG sizes Chromium expects.
#
# Usage: scripts/branding/rasterize-logos.sh <chromium-src-root>
#   <chromium-src-root> defaults to ../chromium-src/src
#
# Targets (must match chrome/app/theme/chromium/):
#   product_logo.svg                 (master, copied through)
#   product_logo_{16,24,48,64,128,256}.png  (color)
#   product_logo_22_mono.png         (monochrome)
#
# Requires: ImageMagick (`magick`).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
SRC_ROOT="${1:-${REPO_ROOT}/../chromium-src/src}"
THEME_DIR="${SRC_ROOT}/chrome/app/theme/chromium"

if [[ ! -d "${THEME_DIR}" ]]; then
  echo "fatal: ${THEME_DIR} not found" >&2
  echo "       pass the chromium src root as \$1" >&2
  exit 2
fi

if command -v rsvg-convert >/dev/null 2>&1; then
  RENDERER=rsvg
elif command -v magick >/dev/null 2>&1; then
  RENDERER=magick
  echo "warning: rsvg-convert not found; falling back to ImageMagick" >&2
  echo "         (install librsvg for higher-fidelity rendering)" >&2
else
  echo "fatal: neither rsvg-convert nor magick found in PATH" >&2
  exit 2
fi

COLOR_SVG="${REPO_ROOT}/branding/product_logo.svg"
MONO_SVG="${REPO_ROOT}/branding/product_logo_mono.svg"

render() {
  # render <svg> <size> <out>
  local svg="$1" size="$2" out="$3"
  if [[ "${RENDERER}" == "rsvg" ]]; then
    rsvg-convert -w "${size}" -h "${size}" "${svg}" -o "${out}"
  else
    magick -background none -density 384 "${svg}" \
           -resize "${size}x${size}" -strip "${out}"
  fi
  echo "wrote ${out}"
}

cp "${COLOR_SVG}" "${THEME_DIR}/product_logo.svg"

for size in 16 24 48 64 128 256; do
  render "${COLOR_SVG}" "${size}" "${THEME_DIR}/product_logo_${size}.png"
done

render "${MONO_SVG}" 22 "${THEME_DIR}/product_logo_22_mono.png"

echo "done."
