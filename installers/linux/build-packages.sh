#!/usr/bin/env bash
# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Builds .deb and .rpm packages from a built linux phlink tree using fpm.
#
# Usage:
#   installers/linux/build-packages.sh <out-dir> <version>
#
# Output:
#   dist/phlink_<version>_amd64.deb
#   dist/phlink-<version>-1.x86_64.rpm

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <out-dir> <version>" >&2
  exit 2
fi

OUT_DIR="$1"
VERSION="$2"

if [[ ! -x "${OUT_DIR}/phlink" ]]; then
  echo "phlink binary not found at ${OUT_DIR}/phlink" >&2
  exit 1
fi
if [[ ! -x "${OUT_DIR}/phlink_update_helper" ]]; then
  echo "phlink_update_helper not found at ${OUT_DIR}/phlink_update_helper" >&2
  exit 1
fi

if ! command -v fpm >/dev/null 2>&1; then
  echo "fpm not in PATH; install via 'gem install fpm'" >&2
  exit 1
fi

STAGE="$(mktemp -d -t phlink-pkg.XXXXXX)"
trap 'rm -rf "${STAGE}"' EXIT
mkdir -p dist

mkdir -p "${STAGE}/opt/phlink" "${STAGE}/usr/bin" \
         "${STAGE}/usr/share/applications" \
         "${STAGE}/usr/share/icons/hicolor/256x256/apps"

cp -a "${OUT_DIR}/." "${STAGE}/opt/phlink/"
ln -s /opt/phlink/phlink "${STAGE}/usr/bin/phlink"
ln -s /opt/phlink/phlink_update_helper \
  "${STAGE}/usr/bin/phlink_update_helper"

ICON_SRC="$(dirname "$0")/../../branding/phlink-256.png"
if [[ -f "${ICON_SRC}" ]]; then
  cp "${ICON_SRC}" "${STAGE}/usr/share/icons/hicolor/256x256/apps/phlink.png"
fi

RELEASE_GPG="${PHLINK_RELEASE_GPG:-$(dirname "$0")/../../branding/release.gpg}"
if [[ -f "${RELEASE_GPG}" ]]; then
  mkdir -p "${STAGE}/usr/share/phlink"
  cp "${RELEASE_GPG}" "${STAGE}/usr/share/phlink/release.gpg"
elif [[ "${PHLINK_ALLOW_MISSING_RELEASE_GPG:-0}" == "1" ]]; then
  echo "warning: omitting release.gpg for local smoke build" >&2
else
  echo "release.gpg not found; set PHLINK_RELEASE_GPG or PHLINK_ALLOW_MISSING_RELEASE_GPG=1 for local smoke builds." >&2
  exit 1
fi

cat > "${STAGE}/usr/share/applications/phlink.desktop" <<'EOF'
[Desktop Entry]
Name=phlink
Exec=phlink %U
Icon=phlink
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml_xml;x-scheme-handler/http;x-scheme-handler/https;
EOF

COMMON_ARGS=(
  --name phlink
  --version "${VERSION}"
  --license MPL-2.0
  --vendor "phlink contributors"
  --maintainer "phlink contributors"
  --url "https://github.com/devparanjay/phlink"
  --description "phlink: a privacy-focused, ad-blocking Chromium-based browser."
  --architecture x86_64
  -C "${STAGE}"
  --prefix /
  -s dir
)

fpm "${COMMON_ARGS[@]}" -t deb -p "dist/phlink_${VERSION}_amd64.deb" .
fpm "${COMMON_ARGS[@]}" -t rpm -p "dist/phlink-${VERSION}-1.x86_64.rpm" .

echo "wrote .deb and .rpm to dist/"
