#!/usr/bin/env python3
"""scripts/apply-patches.py — apply patches/*.patch to ../chromium-src/src/.

Usage:
    python3 scripts/apply-patches.py                 # apply all patches
    python3 scripts/apply-patches.py --dry-run       # show what would happen
    python3 scripts/apply-patches.py --force         # apply over a dirty checkout
    python3 scripts/apply-patches.py --checkout DIR  # use a different checkout

The script:
  1. Locates ../chromium-src/src/ (or --checkout).
  2. Refuses to run on a dirty tree unless --force.
  3. Applies patches/*.patch in lexicographic order via `git am`.
  4. On conflict, aborts the in-progress `git am` and reports the offender.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def is_clean(checkout: Path) -> bool:
    result = run(["git", "status", "--porcelain"], cwd=checkout)
    return result.stdout.strip() == ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", type=Path, default=None,
                        help="Path to the Chromium 'src' directory. Defaults to ../chromium-src/src relative to this repo.")
    parser.add_argument("--patches-dir", type=Path, default=None,
                        help="Path to the patches directory. Defaults to <repo>/patches.")
    parser.add_argument("--dry-run", action="store_true", help="List patches, don't apply.")
    parser.add_argument("--force", action="store_true", help="Apply over a dirty tree.")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    checkout = args.checkout or (repo_root.parent / "chromium-src" / "src")
    patches_dir = args.patches_dir or (repo_root / "patches")

    if not checkout.is_dir() or not (checkout / ".git").exists():
        print(f"error: not a git checkout: {checkout}", file=sys.stderr)
        return 1
    if not patches_dir.is_dir():
        print(f"error: patches directory not found: {patches_dir}", file=sys.stderr)
        return 1

    patches = sorted(p for p in patches_dir.glob("*.patch") if p.is_file())
    if not patches:
        print(f"==> no patches in {patches_dir} (nothing to do)")
        return 0

    if not is_clean(checkout) and not args.force:
        print(f"error: {checkout} has uncommitted changes. Use --force to override.", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"==> would apply {len(patches)} patch(es) to {checkout}:")
        for p in patches:
            print(f"    {p.name}")
        return 0

    for patch in patches:
        print(f"==> applying {patch.name}")
        result = subprocess.run(
            ["git", "am", "--3way", str(patch)],
            cwd=checkout,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            print(f"error: failed to apply {patch.name}; aborting in-progress 'git am'.", file=sys.stderr)
            subprocess.run(["git", "am", "--abort"], cwd=checkout, capture_output=True)
            return 1

    print(f"==> applied {len(patches)} patch(es) successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
