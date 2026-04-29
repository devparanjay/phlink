#!/usr/bin/env bash
# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Generates the phlink release-signing key set:
#
#   - One offline TUF root keypair (Ed25519). The private half MUST be
#     copied to an air-gapped machine immediately and the on-disk copy
#     wiped (`shred -u`). Used only for re-signing the root role and
#     for key-rotation events.
#
#   - Three online TUF keypairs (Ed25519). The targets, snapshot, and
#     timestamp keys live on the release CI runner and sign their own
#     TUF roles on each release.
#
#   - One gpg keypair for Linux package signing (deb/rpm/AppImage).
#
# Usage:
#   scripts/release/keygen.sh <output-dir>
#
# This script is run ONCE per release-key-rotation. Output:
#   <output-dir>/root.key            (Ed25519 private)
#   <output-dir>/root.pub            (Ed25519 public)
#   <output-dir>/root.json           (TUF root metadata, unsigned)
#   <output-dir>/targets.key
#   <output-dir>/targets.pub
#   <output-dir>/snapshot.key
#   <output-dir>/snapshot.pub
#   <output-dir>/timestamp.key
#   <output-dir>/timestamp.pub
#   <output-dir>/release.gpg         (ASCII-armored public)
#   <output-dir>/release.gpg.secret  (ASCII-armored secret -> CI secret)

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <output-dir>" >&2
  exit 2
fi

OUT="$1"
mkdir -p "${OUT}"
chmod 700 "${OUT}"

if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl not on PATH" >&2; exit 1
fi
if ! command -v gpg >/dev/null 2>&1; then
  echo "gpg not on PATH" >&2; exit 1
fi

generate_ed25519() {
  local prefix="$1"
  openssl genpkey -algorithm ED25519 -out "${OUT}/${prefix}.key"
  openssl pkey -in "${OUT}/${prefix}.key" -pubout -out "${OUT}/${prefix}.pub"
  chmod 600 "${OUT}/${prefix}.key"
  chmod 644 "${OUT}/${prefix}.pub"
  echo "  generated ${prefix}.{key,pub}"
}

echo "Generating TUF root key..."
generate_ed25519 root

echo "Generating TUF targets key..."
generate_ed25519 targets

echo "Generating TUF snapshot key..."
generate_ed25519 snapshot

echo "Generating TUF timestamp key..."
generate_ed25519 timestamp

echo "Generating gpg release key..."
GNUPGHOME="$(mktemp -d -t phlink-gpg.XXXXXX)"
export GNUPGHOME
trap 'rm -rf "${GNUPGHOME}"' EXIT
cat > "${GNUPGHOME}/keygen.batch" <<'EOF'
%echo Generating phlink release gpg key
Key-Type: EDDSA
Key-Curve: ed25519
Key-Usage: sign
Subkey-Type: ECDH
Subkey-Curve: cv25519
Subkey-Usage: encrypt
Name-Real: phlink release
Name-Email: release@phlink.dev
Expire-Date: 2y
%no-protection
%commit
%echo done
EOF
gpg --batch --generate-key "${GNUPGHOME}/keygen.batch"
gpg --armor --export release@phlink.dev > "${OUT}/release.gpg"
gpg --armor --export-secret-keys release@phlink.dev > "${OUT}/release.gpg.secret"
chmod 600 "${OUT}/release.gpg.secret"
chmod 644 "${OUT}/release.gpg"

cat <<EOF

Done.

Generated:
  ${OUT}/root.key            -> AIR-GAP THIS, then shred local copy.
  ${OUT}/root.pub            -> bake into chrome/browser/phlink/updater/keys/dev_root.json
  ${OUT}/targets.key         -> upload to CI secret store (GitHub Actions secret).
  ${OUT}/targets.pub
  ${OUT}/snapshot.key        -> upload to CI secret store (GitHub Actions secret).
  ${OUT}/snapshot.pub
  ${OUT}/timestamp.key       -> upload to CI secret store (GitHub Actions secret).
  ${OUT}/timestamp.pub
  ${OUT}/release.gpg         -> bundle into linux installers as /usr/share/phlink/release.gpg
  ${OUT}/release.gpg.secret  -> upload to CI secret store (GitHub Actions secret).

Next steps: see docs/dev/release-keys.md.
EOF
