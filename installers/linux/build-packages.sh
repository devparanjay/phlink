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
#   <out-dir>/phlink_<version>_amd64.deb
#   <out-dir>/phlink-<version>-1.x86_64.rpm

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <out-dir> <version>" >&2
  exit 2
fi

OUT_DIR="$1"
VERSION="$2"

if ! command -v fpm >/dev/null 2>&1; then
  echo "fpm not in PATH; install via 'gem install fpm'" >&2
  exit 1
fi

STAGE="$(mktemp -d -t phlink-pkg.XXXXXX)"
trap 'rm -rf "${STAGE}"' EXIT

mkdir -p "${STAGE}/usr/bin" "${STAGE}/usr/share/applications" \
         "${STAGE}/usr/share/icons/hicolor/256x256/apps" \
         "${STAGE}/usr/share/phlink"

cp "${OUT_DIR}/phlink" "${STAGE}/usr/bin/phlink"
[[ -x "${OUT_DIR}/phlink_update_helper" ]] && \
  cp "${OUT_DIR}/phlink_update_helper" "${STAGE}/usr/bin/phlink_update_helper"

ICON_SRC="$(dirname "$0")/../../branding/phlink-256.png"
if [[ -f "${ICON_SRC}" ]]; then
  cp "${ICON_SRC}" "${STAGE}/usr/share/icons/hicolor/256x256/apps/phlink.png"
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

fpm "${COMMON_ARGS[@]}" -t deb -p "${OUT_DIR}/phlink_${VERSION}_amd64.deb" .
fpm "${COMMON_ARGS[@]}" -t rpm -p "${OUT_DIR}/phlink-${VERSION}-1.x86_64.rpm" .

echo "wrote .deb and .rpm to ${OUT_DIR}"
