#!/usr/bin/env python3
"""scripts/refresh-patches.py — regenerate patches/**/*.patch from the Chromium checkout.

Layout convention (mirrors apply-patches.py):
    patches/<reldir>/NNNN-<slug>.patch

Where <reldir> is the path inside the checkout that the patch applies to.
The empty <reldir> applies at the checkout root. A non-empty <reldir>
typically maps to a Chromium submodule.

For each subtree we know about, this script:
  1. Validates that <base>..<head> is a non-empty linear history.
  2. Wipes existing patches in patches/<reldir>/.
  3. Runs `git format-patch <base>..<head> -o patches/<reldir>/`.
  4. Strips noisy headers (commit hashes, dates, signed-off-by) so re-exports
     produce stable diffs.
  5. Renumbers patches in NNNN-<slug>.patch form, preserving slot ranges
     declared via --slot-base (default 1).

Subtrees default to:
    .                                      (the checkout root)
    third_party/search_engines_data/resources

You can override with --subtree (repeatable). Each --subtree must be a path
relative to the checkout root and a git work-tree.

Usage:
    python3 scripts/refresh-patches.py [--base REF] [--head REF] [--checkout DIR]
                                       [--subtree PATH]... [--slot-base N]

Defaults:
    --base       origin/HEAD
    --head       HEAD
    --checkout   ../chromium-src/src
    --slot-base  1   (so patches start at 0001)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


# Lines to strip in-place to keep diffs stable across re-exports.
NOISY_LINE_RE = re.compile(
    r"^(From [0-9a-f]{40} Mon Sep 17 00:00:00 2001"
    r"|Date: .+"
    r"|Signed-off-by: .+)\n",
    re.MULTILINE,
)

# Default subtrees to enumerate, in apply order. Submodules whose contents
# we patch must be listed here. Each entry: (subtree_path, slot_base).
DEFAULT_SUBTREES: tuple[tuple[str, int], ...] = (
    (".", 1),
    ("third_party/search_engines_data/resources", 21),
)


def run(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout


def resolve_base(cwd: Path, requested: str) -> str | None:
    """Resolve `requested` to a usable base ref in this subtree.

    Falls back to the oldest reachable commit (which, for gclient-managed
    submodules with a grafted history, is the upstream-pinned commit) if
    the requested ref does not exist here.
    """
    probe = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", requested],
        cwd=cwd, capture_output=True, text=True,
    )
    if probe.returncode == 0 and probe.stdout.strip():
        return requested
    # Fallback: the parent of the oldest reachable commit. For a shallow
    # graft, `--max-parents=0` returns the graft itself.
    fallback = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        cwd=cwd, capture_output=True, text=True,
    )
    if fallback.returncode != 0:
        return None
    roots = fallback.stdout.strip().splitlines()
    return roots[0] if roots else None


def refresh_subtree(
    *,
    checkout_root: Path,
    subtree: str,
    base: str,
    head: str,
    patches_dir: Path,
    slot_base: int,
) -> int:
    """Refresh patches for one subtree. Returns the count written."""
    cwd = checkout_root if subtree == "." else (checkout_root / subtree)
    if not (cwd / ".git").exists():
        print(f"warn: skipping {subtree}: not a git work-tree", file=sys.stderr)
        return 0

    resolved_base = resolve_base(cwd, base)
    if resolved_base is None:
        print(f"warn: skipping {subtree}: cannot resolve base ref", file=sys.stderr)
        return 0
    if resolved_base != base:
        print(f"    [{subtree}] base {base} not present; using {resolved_base[:12]}")

    # Validate range non-empty in this subtree.
    log = subprocess.run(
        ["git", "log", "--oneline", f"{resolved_base}..{head}"],
        cwd=cwd, capture_output=True, text=True,
    )
    if log.returncode != 0 or not log.stdout.strip():
        # Nothing to do here. Wipe any stale patches in this subtree's dir.
        out_dir = patches_dir if subtree == "." else (patches_dir / subtree)
        if out_dir.is_dir():
            for old in sorted(out_dir.glob("*.patch")):
                old.unlink()
        return 0

    out_dir = patches_dir if subtree == "." else (patches_dir / subtree)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in sorted(out_dir.glob("*.patch")):
        old.unlink()

    # Generate.
    subprocess.run(
        ["git", "format-patch", "--no-signature",
         f"--start-number={slot_base}",
         f"{resolved_base}..{head}", "-o", str(out_dir)],
        cwd=cwd, check=True,
    )

    # Strip noisy headers.
    for patch in sorted(out_dir.glob("*.patch")):
        content = patch.read_text()
        cleaned = NOISY_LINE_RE.sub("", content)
        patch.write_text(cleaned)

    return len(list(out_dir.glob("*.patch")))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default="origin/HEAD")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--checkout", type=Path, default=None)
    parser.add_argument("--patches-dir", type=Path, default=None)
    parser.add_argument("--subtree", action="append", default=None,
                        help="Subtree path (relative to checkout). Repeatable. "
                             "Defaults to root + known submodules. "
                             "Format: PATH or PATH=SLOT_BASE.")
    parser.add_argument("--slot-base", type=int, default=None,
                        help="Override starting NNNN for every subtree (overrides "
                             "per-subtree defaults).")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    checkout = args.checkout or (repo_root.parent / "chromium-src" / "src")
    patches_dir = args.patches_dir or (repo_root / "patches")

    if not (checkout / ".git").exists():
        print(f"error: not a git checkout: {checkout}", file=sys.stderr)
        return 1

    subtrees: tuple[tuple[str, int], ...]
    if args.subtree:
        parsed: list[tuple[str, int]] = []
        for spec in args.subtree:
            if "=" in spec:
                path, slot = spec.split("=", 1)
                parsed.append((path, int(slot)))
            else:
                parsed.append((spec, 1))
        subtrees = tuple(parsed)
    else:
        subtrees = DEFAULT_SUBTREES

    print(f"==> refreshing patches in {patches_dir} from {checkout}")
    print(f"    range: {args.base}..{args.head}")
    print(f"    subtrees: {', '.join(f'{p}@{s}' for p, s in subtrees)}")

    total = 0
    for subtree, default_slot in subtrees:
        slot = args.slot_base if args.slot_base is not None else default_slot
        n = refresh_subtree(
            checkout_root=checkout,
            subtree=subtree,
            base=args.base,
            head=args.head,
            patches_dir=patches_dir,
            slot_base=slot,
        )
        label = subtree if subtree != "." else "<root>"
        print(f"    [{label}] wrote {n} patch(es)")
        total += n

    print(f"==> wrote {total} patch(es) total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
