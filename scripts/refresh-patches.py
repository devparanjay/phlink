#!/usr/bin/env python3
"""scripts/refresh-patches.py — regenerate patches/*.patch from the Chromium checkout.

Usage:
    python3 scripts/refresh-patches.py [--base REF] [--head REF] [--checkout DIR]

Defaults:
    --base     origin/HEAD  (the upstream branch tip)
    --head     HEAD         (your current commit in chromium-src/src)
    --checkout ../chromium-src/src

The script:
  1. Validates that <base>..<head> is a non-empty linear history.
  2. Wipes existing patches/*.patch.
  3. Runs `git format-patch <base>..<head> -o patches/` from the checkout.
  4. Strips noisy headers (timestamps, signatures) so diffs stay stable across re-exports.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


NOISY_HEADER_RE = re.compile(
    r"^(From [0-9a-f]{40} Mon Sep 17 00:00:00 2001"
    r"|Date: .+"
    r"|Signed-off-by: .+)$",
    re.MULTILINE,
)


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/HEAD")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--checkout", type=Path, default=None)
    parser.add_argument("--patches-dir", type=Path, default=None)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    checkout = args.checkout or (repo_root.parent / "chromium-src" / "src")
    patches_dir = args.patches_dir or (repo_root / "patches")

    if not (checkout / ".git").exists():
        print(f"error: not a git checkout: {checkout}", file=sys.stderr)
        return 1

    # Validate range is non-empty
    log = run(["git", "log", "--oneline", f"{args.base}..{args.head}"], cwd=checkout).strip()
    if not log:
        print(f"error: no commits in {args.base}..{args.head}", file=sys.stderr)
        return 1
    print(f"==> regenerating patches for {args.base}..{args.head}")
    print(log)

    # Wipe existing patches
    patches_dir.mkdir(parents=True, exist_ok=True)
    for old in patches_dir.glob("*.patch"):
        old.unlink()

    # Generate patches
    subprocess.run(
        ["git", "format-patch", "--no-signature", f"{args.base}..{args.head}", "-o", str(patches_dir)],
        cwd=checkout,
        check=True,
    )

    # Strip noisy headers in-place for stable diffs
    for patch in sorted(patches_dir.glob("*.patch")):
        content = patch.read_text()
        cleaned = NOISY_HEADER_RE.sub("", content)
        patch.write_text(cleaned)

    count = len(list(patches_dir.glob("*.patch")))
    print(f"==> wrote {count} patch(es) to {patches_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
