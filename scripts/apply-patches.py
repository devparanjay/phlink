#!/usr/bin/env python3
"""scripts/apply-patches.py — apply patches/**/*.patch to ../chromium-src/src/.

Layout convention:
    patches/<reldir>/NNNN-<slug>.patch

Where <reldir> is the path *inside* the Chromium checkout that the patch
applies to. The empty <reldir> (i.e. patches/*.patch directly) applies at
the checkout root. A non-empty <reldir> typically maps to a Chromium
submodule (e.g. patches/third_party/search_engines_data/resources/...).

Usage:
    python3 scripts/apply-patches.py                 # apply all patches
    python3 scripts/apply-patches.py --dry-run       # show what would happen
    python3 scripts/apply-patches.py --force         # apply over a dirty checkout
    python3 scripts/apply-patches.py --checkout DIR  # use a different checkout

The script:
  1. Locates ../chromium-src/src/ (or --checkout).
  2. Refuses to run on a dirty tree (root + every reldir we touch) unless --force.
  3. Walks patches/ and groups patches by their parent directory.
  4. For each (reldir, [patches...]) group, applies in lexicographic order
     via `git am --3way` with cwd = <checkout>/<reldir>.
  5. On conflict, aborts the in-progress `git am` in that subtree and reports.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def is_clean(cwd: Path) -> bool:
    result = run(["git", "status", "--porcelain"], cwd=cwd)
    return result.stdout.strip() == ""


def collect_patches(patches_dir: Path) -> dict[Path, list[Path]]:
    """Return {reldir_relative_to_patches_dir: [sorted patch paths]}."""
    groups: dict[Path, list[Path]] = {}
    for patch in patches_dir.rglob("*.patch"):
        if not patch.is_file():
            continue
        rel = patch.parent.relative_to(patches_dir)
        groups.setdefault(rel, []).append(patch)
    for rel in groups:
        groups[rel].sort(key=lambda p: p.name)
    return groups


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

    groups = collect_patches(patches_dir)
    total = sum(len(v) for v in groups.values())
    if total == 0:
        print(f"==> no patches in {patches_dir} (nothing to do)")
        return 0

    # Validate every target subtree is a git work-tree and clean (unless --force).
    targets: list[tuple[Path, Path, list[Path]]] = []  # (reldir, abs_cwd, patches)
    for reldir, patches in sorted(groups.items(), key=lambda kv: str(kv[0])):
        abs_cwd = checkout / reldir
        if not abs_cwd.is_dir():
            print(f"error: target directory does not exist: {abs_cwd}", file=sys.stderr)
            return 1
        # A submodule has a .git file (gitlink), the root has a .git dir.
        if not (abs_cwd / ".git").exists():
            print(f"error: not a git work-tree: {abs_cwd}", file=sys.stderr)
            return 1
        if not args.force and not is_clean(abs_cwd):
            print(f"error: {abs_cwd} has uncommitted changes. Use --force to override.",
                  file=sys.stderr)
            return 1
        targets.append((reldir, abs_cwd, patches))

    if args.dry_run:
        print(f"==> would apply {total} patch(es) to {checkout}:")
        for reldir, _abs_cwd, patches in targets:
            label = str(reldir) if str(reldir) != "." else "<root>"
            print(f"    [{label}]")
            for p in patches:
                print(f"      {p.name}")
        return 0

    applied = 0
    for reldir, abs_cwd, patches in targets:
        label = str(reldir) if str(reldir) != "." else "<root>"
        for patch in patches:
            print(f"==> [{label}] applying {patch.name}")
            result = subprocess.run(
                ["git", "am", "--3way", str(patch)],
                cwd=abs_cwd,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(result.stdout)
                print(result.stderr, file=sys.stderr)
                print(f"error: failed to apply {patch.name} in {abs_cwd}; "
                      "aborting in-progress 'git am'.", file=sys.stderr)
                subprocess.run(["git", "am", "--abort"], cwd=abs_cwd, capture_output=True)
                return 1
            applied += 1

    print(f"==> applied {applied} patch(es) successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
