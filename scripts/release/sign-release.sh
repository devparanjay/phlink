#!/usr/bin/env bash
# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# Signs a phlink release: produces TUF targets.json, snapshot.json,
# and timestamp.json over the supplied artifacts, plus detached gpg
# signatures for Linux artifacts.
#
# Usage:
#   scripts/release/sign-release.sh <artifacts-dir> <version> \
#                                   <targets-key> <snapshot-key> \
#                                   <timestamp-key> <gpg-secret-key>
#
# <artifacts-dir>     -- directory containing the installers to sign
#                        (installers plus updater payloads for the same
#                         version).
# <version>           -- release version, e.g. 0.1.0.
# <targets-key>       -- path to the Ed25519 targets.key (PEM).
# <snapshot-key>      -- path to the Ed25519 snapshot.key (PEM).
# <timestamp-key>     -- path to the Ed25519 timestamp.key (PEM).
# <gpg-secret-key>    -- path to the ASCII-armored gpg secret key.
#
# Output (in <artifacts-dir>):
#   targets.json
#   snapshot.json
#   timestamp.json
#   <each-linux-artifact>.sig

set -euo pipefail

if [[ $# -lt 6 ]]; then
    echo "usage: $0 <artifacts-dir> <version> <targets-key> <snapshot-key> <timestamp-key> <gpg-secret-key>" >&2
    exit 2
fi

ARTIFACTS="$1"
VERSION="$2"
TARGETS_KEY="$3"
SNAPSHOT_KEY="$4"
TIMESTAMP_KEY="$5"
GPG_SECRET="$6"

if [[ ! -d "${ARTIFACTS}" ]]; then
    echo "artifacts dir not found: ${ARTIFACTS}" >&2; exit 1
fi
for k in "${TARGETS_KEY}" "${SNAPSHOT_KEY}" "${TIMESTAMP_KEY}" \
                 "${GPG_SECRET}"; do
    if [[ ! -f "$k" ]]; then echo "missing key: $k" >&2; exit 1; fi
done

expected_artifacts=(
    "phlink-${VERSION}-mac-arm64.dmg"
    "phlink-${VERSION}-mac-arm64-update.zip"
    "phlink-${VERSION}-linux-x86_64.AppImage"
    "phlink-${VERSION}-linux-x86_64-update"
    "phlink_${VERSION}_amd64.deb"
    "phlink-${VERSION}-1.x86_64.rpm"
    "phlink-${VERSION}-win-x64.msi"
    "phlink-${VERSION}-win-x64-update.exe"
)

for name in "${expected_artifacts[@]}"; do
    if [[ ! -f "${ARTIFACTS}/${name}" ]]; then
        echo "missing expected release artifact: ${name}" >&2
        exit 1
    fi
done

shopt -s nullglob
release_files=("${ARTIFACTS}"/*)
shopt -u nullglob
for path in "${release_files[@]}"; do
    [[ -f "${path}" ]] || continue
    name="$(basename "${path}")"
    case "${name}" in
        targets.json|snapshot.json|timestamp.json|*.sig) continue ;;
    esac
    allowed=false
    for expected in "${expected_artifacts[@]}"; do
        if [[ "${name}" == "${expected}" ]]; then
            allowed=true
            break
        fi
    done
    if [[ "${allowed}" != true ]]; then
        echo "unexpected release artifact: ${name}" >&2
        exit 1
    fi
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

# 2. TUF metadata: targets over payloads, snapshot over targets,
#    timestamp over snapshot.
python3 - "${ARTIFACTS}" "${VERSION}" "${TARGETS_KEY}" \
    "${SNAPSHOT_KEY}" "${TIMESTAMP_KEY}" <<'PY'
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile

artifacts_dir, version, targets_key, snapshot_key, timestamp_key = sys.argv[1:]
now = dt.datetime.now(dt.timezone.utc)

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def expiry(days):
    return (now + dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")

def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()

def keyid_for(key_path):
    pub_der = subprocess.run(
        ["openssl", "pkey", "-in", key_path, "-pubout", "-outform", "DER"],
        capture_output=True, check=True,
    ).stdout
    return hashlib.sha256(pub_der).hexdigest()

def sign_envelope(signed, key_path):
    canon = canonical(signed)
    with tempfile.NamedTemporaryFile() as message:
        message.write(canon)
        message.flush()
        sig = subprocess.run(
            [
                "openssl", "pkeyutl", "-sign", "-inkey", key_path,
                "-rawin", "-in", message.name,
            ],
            capture_output=True, check=True,
        ).stdout
    return {
        "signed": signed,
        "signatures": [{"keyid": keyid_for(key_path), "sig": sig.hex()}],
    }

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, separators=(",", ":"), sort_keys=True)

def meta_for(path):
    return {
        "length": os.path.getsize(path),
        "hashes": {"sha256": sha256_file(path)},
    }

expected_names = [
    f"phlink-{version}-mac-arm64-update.zip",
    f"phlink-{version}-linux-x86_64-update",
    f"phlink-{version}-win-x64-update.exe",
]

def custom_for(name):
    if name.endswith("-mac-arm64-update.zip"):
        return {
            "version": version,
            "platform": "mac",
            "arch": "arm64",
            "channel": "stable",
            "format": "app-zip",
        }
    if name.endswith("-linux-x86_64-update"):
        return {
            "version": version,
            "platform": "linux",
            "arch": "x86_64",
            "channel": "stable",
            "format": "binary",
        }
    if name.endswith("-win-x64-update.exe"):
        return {
            "version": version,
            "platform": "win",
            "arch": "x64",
            "channel": "stable",
            "format": "exe",
        }
    raise ValueError(f"unclassified update target: {name}")

targets = {}
for name in expected_names:
    full = os.path.join(artifacts_dir, name)
    targets[name] = {
        "length": os.path.getsize(full),
        "hashes": {"sha256": sha256_file(full)},
        "custom": custom_for(name),
    }

role_version = int(now.timestamp())
targets_signed = {
    "_type": "targets",
    "spec_version": "1.0.32",
    "version": role_version,
    "expires": expiry(90),
    "targets": targets,
}
targets_path = os.path.join(artifacts_dir, "targets.json")
write_json(targets_path, sign_envelope(targets_signed, targets_key))
print(f"  wrote {targets_path}  ({len(targets)} targets)")

snapshot_signed = {
    "_type": "snapshot",
    "spec_version": "1.0.32",
    "version": role_version,
    "expires": expiry(30),
    "meta": {"targets.json": {**meta_for(targets_path), "version": role_version}},
}
snapshot_path = os.path.join(artifacts_dir, "snapshot.json")
write_json(snapshot_path, sign_envelope(snapshot_signed, snapshot_key))
print(f"  wrote {snapshot_path}")

timestamp_signed = {
    "_type": "timestamp",
    "spec_version": "1.0.32",
    "version": role_version,
    "expires": expiry(7),
    "meta": {"snapshot.json": {**meta_for(snapshot_path), "version": role_version}},
}
timestamp_path = os.path.join(artifacts_dir, "timestamp.json")
write_json(timestamp_path, sign_envelope(timestamp_signed, timestamp_key))
print(f"  wrote {timestamp_path}")
PY

echo "Done. Root metadata is signed only during the offline key ceremony."
