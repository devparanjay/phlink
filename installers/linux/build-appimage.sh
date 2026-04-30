#!/usr/bin/env bash
# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Builds a phlink.AppImage from an already-built linux phlink tree.
#
# Usage:
#   installers/linux/build-appimage.sh <out-dir> <version>
#
# Requires: appimagetool, mksquashfs (linuxdeploy is optional).
# Output:   dist/phlink-<version>-linux-x86_64.AppImage

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <out-dir> <version>" >&2
  exit 2
fi

OUT_DIR="$1"
VERSION="$2"
DIST_DIR="dist"
APPIMG_OUT="${DIST_DIR}/phlink-${VERSION}-linux-x86_64.AppImage"

if [[ ! -x "${OUT_DIR}/phlink" ]]; then
  echo "phlink binary not found at ${OUT_DIR}/phlink" >&2
  exit 1
fi
if [[ ! -x "${OUT_DIR}/phlink_update_helper" ]]; then
  echo "phlink_update_helper not found at ${OUT_DIR}/phlink_update_helper" >&2
  exit 1
fi
if ! command -v appimagetool >/dev/null 2>&1; then
  echo "appimagetool not in PATH; install it from https://appimage.github.io/appimagetool/" >&2
  exit 1
fi

APPDIR="$(mktemp -d -t phlink-appdir.XXXXXX)"
trap 'rm -rf "${APPDIR}"' EXIT
mkdir -p "${DIST_DIR}"

mkdir -p "${APPDIR}/usr/bin" "${APPDIR}/usr/lib/phlink" \
         "${APPDIR}/usr/share/applications" \
         "${APPDIR}/usr/share/icons/hicolor/256x256/apps"

cp -a "${OUT_DIR}/." "${APPDIR}/usr/lib/phlink/"
ln -s ../lib/phlink/phlink "${APPDIR}/usr/bin/phlink"
ln -s ../lib/phlink/phlink_update_helper \
  "${APPDIR}/usr/bin/phlink_update_helper"

# Find icon. Prefer the rasterized branding output.
ICON_SRC="$(dirname "$0")/../../branding/phlink-256.png"
if [[ -f "${ICON_SRC}" ]]; then
  cp "${ICON_SRC}" "${APPDIR}/phlink.png"
  cp "${ICON_SRC}" "${APPDIR}/usr/share/icons/hicolor/256x256/apps/phlink.png"
fi

RELEASE_GPG="${PHLINK_RELEASE_GPG:-$(dirname "$0")/../../branding/release.gpg}"
if [[ -f "${RELEASE_GPG}" ]]; then
  mkdir -p "${APPDIR}/usr/share/phlink"
  cp "${RELEASE_GPG}" "${APPDIR}/usr/share/phlink/release.gpg"
elif [[ "${PHLINK_ALLOW_MISSING_RELEASE_GPG:-0}" == "1" ]]; then
  echo "warning: omitting release.gpg for local smoke build" >&2
else
  echo "release.gpg not found; set PHLINK_RELEASE_GPG or PHLINK_ALLOW_MISSING_RELEASE_GPG=1 for local smoke builds." >&2
  exit 1
fi

cat > "${APPDIR}/phlink.desktop" <<'EOF'
[Desktop Entry]
Name=phlink
Exec=phlink %U
Icon=phlink
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml_xml;x-scheme-handler/http;x-scheme-handler/https;
EOF
cp "${APPDIR}/phlink.desktop" \
   "${APPDIR}/usr/share/applications/phlink.desktop"

cat > "${APPDIR}/AppRun" <<'EOF'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/lib/phlink/phlink" "$@"
EOF
chmod +x "${APPDIR}/AppRun"

ARCH=x86_64 appimagetool "${APPDIR}" "${APPIMG_OUT}"
echo "wrote ${APPIMG_OUT}"
