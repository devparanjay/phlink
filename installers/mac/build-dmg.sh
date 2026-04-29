#!/usr/bin/env bash
# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Builds a signed phlink.dmg from an already-built phlink.app.
#
# Usage:
#   installers/mac/build-dmg.sh <out-dir> <version> [signing-identity]
#
# <out-dir>           -- chromium-src/out/Default (or wherever phlink.app lives)
# <version>           -- e.g. 0.1.0; baked into the dmg name and CFBundleShortVersionString
# [signing-identity]  -- optional Developer ID Application identity. Falls back to
#                        ad-hoc signing (`-`) which produces an unsigned-for-distribution
#                        dmg suitable only for local smoke tests.
#
# The output is `dist/phlink-<version>-mac-arm64.dmg`. This script
# does NOT notarize -- notarization is a separate CI step (10-08).

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <out-dir> <version> [signing-identity]" >&2
  exit 2
fi

OUT_DIR="$1"
VERSION="$2"
IDENTITY="${3:--}"

APP="${OUT_DIR}/phlink.app"
HELPER="${OUT_DIR}/phlink_update_helper"
DIST_DIR="dist"
DMG_PATH="${DIST_DIR}/phlink-${VERSION}-mac-arm64.dmg"

if [[ ! -d "${APP}" ]]; then
  echo "phlink.app not found at ${APP}; build chrome first." >&2
  exit 1
fi
if [[ ! -x "${HELPER}" ]]; then
  echo "phlink_update_helper not found at ${HELPER}; run autoninja chrome/browser/phlink/updater:update_helpers." >&2
  exit 1
fi

STAGE="$(mktemp -d -t phlink-dmg.XXXXXX)"
trap 'rm -rf "${STAGE}"' EXIT
mkdir -p "${DIST_DIR}"

cp -R "${APP}" "${STAGE}/"
mkdir -p "${STAGE}/phlink.app/Contents/Helpers"
cp "${HELPER}" "${STAGE}/phlink.app/Contents/Helpers/phlink_update_helper"
ln -s /Applications "${STAGE}/Applications"

# Re-sign the bundle so the embedded helper is covered.
codesign --force --deep --sign "${IDENTITY}" --options runtime \
  --entitlements /dev/null \
  "${STAGE}/phlink.app" 2>/dev/null || \
  codesign --force --deep --sign "${IDENTITY}" "${STAGE}/phlink.app"

rm -f "${DMG_PATH}"
hdiutil create \
  -volname "phlink ${VERSION}" \
  -srcfolder "${STAGE}" \
  -ov -format UDZO \
  "${DMG_PATH}"

if [[ "${IDENTITY}" != "-" ]]; then
  codesign --force --sign "${IDENTITY}" "${DMG_PATH}"
fi

echo "wrote ${DMG_PATH}"
