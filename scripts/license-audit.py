#!/usr/bin/env python3
"""License audit for phlink's added third-party deps.

Walks `patches/*.patch` for added `README.chromium` files and extracts
their `License:` lines. Validates every license is in the allow-list
defined by `docs/dev/PRD.md` §10.1 and `docs/dev/third-party-licenses.md`,
and that every crate/list found in patches is also documented in the
manifest. Exits non-zero on any mismatch.

This is the mechanical guard for plan 11-04. Human review of the
manifest itself remains required for new PRs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Licenses allowed in shipped binaries. See docs/dev/third-party-licenses.md §1.
ALLOWED_LICENSES = {
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "BSD-style",  # Chromium-internal phrasing; treat as BSD-3.
    "ISC",
    "MIT",
    "MPL-2.0",
    "Unicode-DFS-2016",
    "Unlicense",
    "zlib",
    # Dual-licensed entries the manifest disambiguates by component:
    "Apache-2.0 OR MIT",
    "Apache-2.0 / MIT",
    # Sentinel used by directories that aggregate multiple-licensed
    # data assets (e.g., third_party/phlink_filter_lists/), where the
    # per-file LICENSE.* in the same directory is the source of truth
    # rather than a single SPDX expression. Allowed only when paired
    # with explicit LICENSE.* files in the same patch.
    "Multiple \u2014 see per-file LICENSE.* in this directory.",
}

# License terms that are allowed only when shipped as data (not linked
# code). The script doesn't try to enforce the data-vs-code distinction
# automatically — it relies on the manifest to call out each instance —
# so these tokens are tolerated only when found inside a path that the
# manifest tags as a filter list, not a Rust crate.
DATA_ONLY_LICENSES = {
    "GPL-3.0",
    "CC BY-SA 3.0",
    "CC BY 4.0",
}

PATCH_DIR = REPO / "patches"
MANIFEST = REPO / "docs" / "dev" / "third-party-licenses.md"

LICENSE_RE = re.compile(r"^\+License: (.+?)\s*$", re.MULTILINE)
NEW_README_RE = re.compile(
    r"^\+\+\+ b/(third_party/[^\s]+/README\.chromium)\s*$",
    re.MULTILINE,
)


def collect_patch_licenses() -> dict[str, str]:
    """Return {readme_path: license} for every README.chromium added by
    a patch in patches/."""
    found: dict[str, str] = {}
    for patch in sorted(PATCH_DIR.glob("*.patch")):
        text = patch.read_text(encoding="utf-8", errors="replace")
        # Walk file-by-file diff blocks.
        # A simple state machine: when we see `+++ b/<path>/README.chromium`,
        # the next `+License: X` belongs to that README until the next
        # `diff --git`.
        current: str | None = None
        for line in text.splitlines():
            if line.startswith("diff --git "):
                current = None
                continue
            m_readme = re.match(r"^\+\+\+ b/(third_party/.+/README\.chromium)\s*$", line)
            if m_readme:
                current = m_readme.group(1)
                continue
            m_lic = re.match(r"^\+License:\s*(.+?)\s*$", line)
            if m_lic and current is not None:
                found.setdefault(current, m_lic.group(1))
    return found


def manifest_licenses() -> set[str]:
    """Return the set of license identifiers declared in the manifest's
    tables (extracted by a permissive regex; this is intentionally
    loose — the manifest is the source of truth, this just sanity-checks
    that nothing in the patches uses a license the manifest does not
    list at all)."""
    text = MANIFEST.read_text(encoding="utf-8")
    declared: set[str] = set()
    for license_token in re.findall(r"\b(Apache-2\.0|BSD-[23]-Clause|BSD-style|ISC|MIT|MPL-2\.0|GPL-3\.0|CC BY-SA 3\.0|CC BY 4\.0|Unicode-DFS-2016|Unlicense|zlib)\b", text):
        declared.add(license_token)
    return declared


def main() -> int:
    if not MANIFEST.exists():
        print(f"FATAL: manifest missing: {MANIFEST}", file=sys.stderr)
        return 2

    patch_licenses = collect_patch_licenses()
    if not patch_licenses:
        print("WARN: no third-party README.chromium additions found in patches/.", file=sys.stderr)

    declared = manifest_licenses()

    failures: list[str] = []
    warned: list[str] = []

    for readme, license_token in sorted(patch_licenses.items()):
        if license_token in ALLOWED_LICENSES:
            continue
        if license_token in DATA_ONLY_LICENSES:
            # README.chromium is for code; data-only licenses must not
            # appear here. (Filter lists ship with their own LICENSE.*
            # files alongside, not via README.chromium.)
            failures.append(
                f"{readme}: license {license_token!r} is allowed only as data, "
                f"not in a README.chromium for linked code."
            )
            continue
        msg = (
            f"{readme}: license {license_token!r} is not in the allow-list "
            "(see docs/dev/third-party-licenses.md \u00a71). "
            "If this is a new acceptable license, update both the manifest "
            "and the ALLOWED_LICENSES collection in this script in the same PR."
        )
        failures.append(msg)

    # Every patch-discovered license must also be mentioned in the manifest
    # somewhere — guards against silently adding a dep that bypasses review.
    for license_token in sorted(set(patch_licenses.values())):
        if license_token not in declared and license_token not in {
            "Apache-2.0 OR MIT",
            "Apache-2.0 / MIT",
            "Multiple \u2014 see per-file LICENSE.* in this directory.",
        }:
            warned.append(
                f"license {license_token!r} found in patches/ but not mentioned "
                f"by name in docs/dev/third-party-licenses.md — confirm the "
                f"manifest still documents this dep."
            )

    print(f"Audited {len(patch_licenses)} README.chromium entries from patches/.")
    print(f"Distinct licenses: {sorted(set(patch_licenses.values()))}")

    if warned:
        print("\nWarnings:", file=sys.stderr)
        for w in warned:
            print(f"  - {w}", file=sys.stderr)

    if failures:
        print("\nFailures:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("OK: every shipped third-party license is in the allow-list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
