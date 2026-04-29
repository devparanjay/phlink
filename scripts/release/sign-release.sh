#!/usr/bin/env bash
# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Signs a phlink release: produces a TUF targets.json + snapshot.json +
# timestamp.json over the supplied artifacts, plus detached gpg
# signatures for the linux artifacts.
#
# Usage:
#   scripts/release/sign-release.sh <artifacts-dir> <version> \
#                                   <targets-key> <gpg-secret-key>
#
# <artifacts-dir>     -- directory containing the installers to sign
#                        (e.g. phlink-<v>-mac-arm64.dmg, .AppImage,
#                         .deb, .rpm, .msi).
# <version>           -- release version, e.g. 0.1.0.
# <targets-key>       -- path to the Ed25519 targets.key (PEM).
# <gpg-secret-key>    -- path to the ASCII-armored gpg secret key.
#
# Output (in <artifacts-dir>):
#   targets.json
#   snapshot.json
#   timestamp.json
#   <each-linux-artifact>.sig

set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "usage: $0 <artifacts-dir> <version> <targets-key> <gpg-secret-key>" >&2
  exit 2
fi

ARTIFACTS="$1"
VERSION="$2"
TARGETS_KEY="$3"
GPG_SECRET="$4"

if [[ ! -d "${ARTIFACTS}" ]]; then
  echo "artifacts dir not found: ${ARTIFACTS}" >&2; exit 1
fi
for k in "${TARGETS_KEY}" "${GPG_SECRET}"; do
  if [[ ! -f "$k" ]]; then echo "missing key: $k" >&2; exit 1; fi
done

# 1. Detached gpg signatures for linux artifacts.
GNUPGHOME="$(mktemp -d -t phlink-sign-gpg.XXXXXX)"
export GNUPGHOME
trap 'rm -rf "${GNUPGHOME}"' EXIT
gpg --batch --import "${GPG_SECRET}"

shopt -s nullglob
for art in "${ARTIFACTS}"/phlink-*.AppImage "${ARTIFACTS}"/phlink_*.deb \
           "${ARTIFACTS}"/phlink-*.rpm; do
  echo "  gpg-signing $(basename "${art}")"
  gpg --batch --yes --detach-sign --armor \
      --output "${art}.sig" "${art}"
done
shopt -u nullglob

# 2. TUF targets.json: name, length, sha256 for each artifact.
python3 - "${ARTIFACTS}" "${VERSION}" "${TARGETS_KEY}" <<'PY'
import base64
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

artifacts_dir, version, targets_key = sys.argv[1:]

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

targets = {}
for name in sorted(os.listdir(artifacts_dir)):
    if any(name.endswith(s) for s in (".dmg", ".AppImage", ".deb",
                                      ".rpm", ".msi", ".exe", ".zip")):
        full = os.path.join(artifacts_dir, name)
        targets[name] = {
            "length": os.path.getsize(full),
            "hashes": {"sha256": sha256_file(full)},
        }

future = (dt.datetime.utcnow() + dt.timedelta(days=30))\
    .strftime("%Y-%m-%dT%H:%M:%SZ")
signed = {
    "_type": "targets",
    "spec_version": "1.0.32",
    "version": int(dt.datetime.utcnow().timestamp()),
    "expires": future,
    "targets": targets,
}

# Canonical-JSON encode (sorted keys, no whitespace).
canon = json.dumps(signed, sort_keys=True, separators=(",", ":")).encode()

# Sign with openssl (Ed25519 raw signature).
sig = subprocess.run(
    ["openssl", "pkeyutl", "-sign", "-inkey", targets_key, "-rawin"],
    input=canon, capture_output=True, check=True,
).stdout
sig_hex = sig.hex()

# Compute keyid = sha256(canonical-JSON of pub key DER).
pub_der = subprocess.run(
    ["openssl", "pkey", "-in", targets_key, "-pubout", "-outform", "DER"],
    capture_output=True, check=True,
).stdout
keyid = hashlib.sha256(pub_der).hexdigest()

envelope = {
    "signed": signed,
    "signatures": [{"keyid": keyid, "sig": sig_hex}],
}
out = os.path.join(artifacts_dir, "targets.json")
with open(out, "w") as f:
    json.dump(envelope, f, separators=(",", ":"), sort_keys=True)
print(f"  wrote {out}  ({len(targets)} targets)")
PY

echo "Done. Sign root.json + snapshot.json + timestamp.json on the"
echo "air-gapped machine; this script intentionally does not."
