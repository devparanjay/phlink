#!/usr/bin/env python3
"""Phase 8.5 GRD body-text rewriter.

Replaces literal 'Chromium' with 'phlink' in <message> bodies of GRD files,
preserving:
  - <!-- developer comments -->
  - desc="..." translator-help attributes
  - 'The Chromium Authors' copyright (legal attribution)
  - 'ChromiumOS' (we don't ship ChromeOS)
  - 'Unused in Chromium builds' / 'Not used in Chromium' developer comments
  - <ex>Chromium</ex> translator examples
"""
import re
import sys
from pathlib import Path

PRESERVE = (
    "ChromiumOS",
    "The Chromium Authors",
    "Chromium Authors",
    "Unused in Chromium builds",
    "Not used in Chromium",
    "<ex>Chromium</ex>",
    # We use the same file as Chromium, with...
    "same file as Chromium",
)


def is_skip_line(line: str) -> bool:
    """Lines we never touch: comments, attributes, structural tags."""
    stripped = line.lstrip()
    if stripped.startswith("<!--") or "<!--" in stripped[: stripped.find("Chromium")]:
        return True
    # desc="..." attribute on the same line as Chromium
    if re.search(r'desc="[^"]*Chromium[^"]*"', line):
        # If the ONLY Chromium occurrence is inside desc, skip
        without_desc = re.sub(r'desc="[^"]*"', "", line)
        if "Chromium" not in without_desc:
            return True
    # name="..." attribute
    if re.search(r'name="[^"]*Chromium[^"]*"', line):
        without_name = re.sub(r'name="[^"]*"', "", line)
        if "Chromium" not in without_name:
            return True
    return False


def rewrite_line(line: str) -> str:
    if "Chromium" not in line:
        return line
    if is_skip_line(line):
        return line
    # Preserve protected literals by stashing them
    sentinels = {}
    for i, p in enumerate(PRESERVE):
        if p in line:
            tok = f"\x00PRESERVE{i}\x00"
            sentinels[tok] = p
            line = line.replace(p, tok)
    line = line.replace("Chromium", "phlink")
    for tok, p in sentinels.items():
        line = line.replace(tok, p)
    return line


def main():
    if len(sys.argv) < 2:
        print("usage: phase-8.5-grd-rewrite.py <grd-file> [<grd-file> ...]")
        sys.exit(2)
    total = 0
    for arg in sys.argv[1:]:
        p = Path(arg)
        src = p.read_text()
        out = []
        n = 0
        for ln in src.splitlines(keepends=True):
            new = rewrite_line(ln)
            if new != ln:
                n += 1
            out.append(new)
        if n:
            p.write_text("".join(out))
            print(f"{p}: {n} lines changed")
            total += n
        else:
            print(f"{p}: no changes")
    print(f"total: {total} lines")


if __name__ == "__main__":
    main()
