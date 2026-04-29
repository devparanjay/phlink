#!/usr/bin/env python3
# Copyright 2026 The phlink Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""WCAG 2.2 AA contrast audit — phlink Phase 8 D-07 lint mirror.

Pure-Python (stdlib only) reproduction of the gtest gate landed by patch
0114 (chrome/browser/ui/color/phlink_color_contrast_unittests.cc). Runs at
lint time (no Chromium build required) so palette regressions are caught
before the chromium-side gtest layer is reached.

Source of truth for hex literals:
  * --src-file flag, or
  * env CHROMIUM_SRC + chrome/browser/ui/color/phlink_palette.cc, or
  * patches/0111-…patch + patches/0112-…patch fallback inside the phlink
    repo (CI-friendly — no chromium-src checkout needed), or
  * --self-test (hardcoded D-08 hex values from stitch-output.md §2.3).

WCAG 2.2 SC 1.4.3 / 1.4.11 thresholds:
    normal text     >= 4.5:1
    non-text UI     >= 3.0:1   (currently empty — hairlines are decorative
                                per stitch-output.md §2.3 and excluded
                                from the gate; structural slot retained)

See also: .planning/phases/08-appearance-subsystem/08-CONTEXT.md D-07, D-12.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Palette index aliases (must match phlink_palette.h enum PhlinkToken).
# ---------------------------------------------------------------------------
TOKENS = [
    "kCanvas",
    "kSurface",
    "kSurfaceAlt",
    "kCard",
    "kText",
    "kTextMuted",
    "kHairline",
    "kAccent",
    "kOnAccent",
    "kDanger",
    "kSuccess",
]
PALETTE_SIZE = len(TOKENS)
TOKEN_INDEX = {name: i for i, name in enumerate(TOKENS)}

# ---------------------------------------------------------------------------
# Pair tables — mirror chrome/browser/ui/color/phlink_palette.cc.
# ---------------------------------------------------------------------------
PAIRS_NORMAL = [
    ("kText", "kCanvas"),
    ("kText", "kSurface"),
    ("kText", "kCard"),
    ("kText", "kSurfaceAlt"),
    ("kTextMuted", "kCanvas"),
    ("kTextMuted", "kSurface"),
    ("kOnAccent", "kAccent"),
]

PAIRS_NON_TEXT: list[tuple[str, str]] = []  # see module docstring.

THRESHOLD_NORMAL = 4.5
THRESHOLD_NON_TEXT = 3.0

# ---------------------------------------------------------------------------
# D-08 hex values (from stitch-output.md §2.1/§2.2). --self-test ground truth.
# ---------------------------------------------------------------------------
SELF_TEST_LIGHT = [
    (0xFF, 0xFF, 0xFF),  # kCanvas
    (0xF8, 0xF4, 0xEC),  # kSurface
    (0xF1, 0xED, 0xE5),  # kSurfaceAlt
    (0xFF, 0xFF, 0xFF),  # kCard
    (0x1A, 0x1A, 0x1A),  # kText
    (0x52, 0x52, 0x52),  # kTextMuted
    (0xE5, 0xE0, 0xD6),  # kHairline
    (0xA8, 0xC8, 0xE8),  # kAccent
    (0x1A, 0x1A, 0x1A),  # kOnAccent
    (0xC0, 0x39, 0x2B),  # kDanger
    (0x2E, 0x85, 0x40),  # kSuccess
]

SELF_TEST_DARK = [
    (0x0D, 0x0D, 0x0D),  # kCanvas
    (0x18, 0x18, 0x18),  # kSurface
    (0x1F, 0x1F, 0x1F),  # kSurfaceAlt
    (0x1F, 0x1F, 0x1F),  # kCard
    (0xFF, 0xFF, 0xFF),  # kText
    (0xA0, 0xA0, 0xA0),  # kTextMuted
    (0x2A, 0x2A, 0x2A),  # kHairline
    (0xF5, 0xE6, 0x8A),  # kAccent
    (0x00, 0x00, 0x00),  # kOnAccent
    (0xF5, 0x73, 0x6B),  # kDanger
    (0x6F, 0xE3, 0x8A),  # kSuccess
]

# ---------------------------------------------------------------------------
# WCAG 2.2 luminance + contrast.
# ---------------------------------------------------------------------------


def _channel(c: int) -> float:
    s = c / 255.0
    return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def contrast_ratio(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    l1 = relative_luminance(c1)
    l2 = relative_luminance(c2)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


# ---------------------------------------------------------------------------
# Palette parsing.
# ---------------------------------------------------------------------------
_RGB_RE = re.compile(
    r"SkColorSetRGB\(\s*0x([0-9A-Fa-f]{2})\s*,\s*0x([0-9A-Fa-f]{2})\s*,\s*0x([0-9A-Fa-f]{2})\s*\)"
)
_BLOCK_RE = re.compile(
    r"kPhlink(?P<mode>Light|Dark)\s*\[kPhlinkPaletteSize\]\s*=\s*\{(?P<body>.*?)\};",
    re.DOTALL,
)


def parse_palette_text(text: str) -> dict[str, list[tuple[int, int, int]]]:
    """Extract Light + Dark palettes from phlink_palette.cc-style text."""
    result: dict[str, list[tuple[int, int, int]]] = {}
    for m in _BLOCK_RE.finditer(text):
        mode = m.group("mode").lower()
        body = m.group("body")
        colors = [
            (int(r, 16), int(g, 16), int(b, 16))
            for r, g, b in _RGB_RE.findall(body)
        ]
        if len(colors) != PALETTE_SIZE:
            raise ValueError(
                f"phlink palette {mode!r} block has {len(colors)} entries, "
                f"expected {PALETTE_SIZE}"
            )
        result[mode] = colors
    if "light" not in result or "dark" not in result:
        raise ValueError(
            "could not locate kPhlinkLight[] and kPhlinkDark[] blocks"
        )
    return result


def parse_palette_file(path: Path) -> dict[str, list[tuple[int, int, int]]]:
    return parse_palette_text(path.read_text(encoding="utf-8"))


def parse_palette_from_patches(
    patch_light: Path, patch_dark: Path
) -> dict[str, list[tuple[int, int, int]]]:
    """Fallback: extract palette from patch hunks (CI without chromium-src)."""
    text = patch_light.read_text(encoding="utf-8") + "\n" + patch_dark.read_text(
        encoding="utf-8"
    )
    # Strip leading patch markers ("+", " ") so _BLOCK_RE / _RGB_RE work.
    cleaned_lines = []
    for line in text.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith(("+", " ")):
            cleaned_lines.append(line[1:])
    return parse_palette_text("\n".join(cleaned_lines))


# ---------------------------------------------------------------------------
# Audit.
# ---------------------------------------------------------------------------


def audit(
    palette: list[tuple[int, int, int]],
    pairs: list[tuple[str, str]],
    threshold: float,
    mode: str,
) -> list[tuple[str, str, str, float, float]]:
    """Return list of (mode, fg_name, bg_name, ratio, threshold) failures."""
    failures = []
    for fg, bg in pairs:
        fg_rgb = palette[TOKEN_INDEX[fg]]
        bg_rgb = palette[TOKEN_INDEX[bg]]
        ratio = contrast_ratio(fg_rgb, bg_rgb)
        if ratio < threshold:
            failures.append((mode, fg, bg, ratio, threshold))
    return failures


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def _print_table(
    palettes: dict[str, list[tuple[int, int, int]]], stream=sys.stdout
) -> None:
    print(
        f"{'Mode':<6} {'Foreground':<22} {'Background':<22} "
        f"{'Ratio':>7}  {'Min':>5}  Status",
        file=stream,
    )
    print("-" * 78, file=stream)
    for mode_name, palette in palettes.items():
        for fg, bg in PAIRS_NORMAL:
            ratio = contrast_ratio(
                palette[TOKEN_INDEX[fg]], palette[TOKEN_INDEX[bg]]
            )
            status = "PASS" if ratio >= THRESHOLD_NORMAL else "FAIL"
            print(
                f"{mode_name:<6} "
                f"{fg + ' ' + _hex(palette[TOKEN_INDEX[fg]]):<22} "
                f"{bg + ' ' + _hex(palette[TOKEN_INDEX[bg]]):<22} "
                f"{ratio:>6.2f}:1  {THRESHOLD_NORMAL:>4.1f}  {status}",
                file=stream,
            )
        for fg, bg in PAIRS_NON_TEXT:
            ratio = contrast_ratio(
                palette[TOKEN_INDEX[fg]], palette[TOKEN_INDEX[bg]]
            )
            status = "PASS" if ratio >= THRESHOLD_NON_TEXT else "FAIL"
            print(
                f"{mode_name:<6} "
                f"{fg + ' ' + _hex(palette[TOKEN_INDEX[fg]]):<22} "
                f"{bg + ' ' + _hex(palette[TOKEN_INDEX[bg]]):<22} "
                f"{ratio:>6.2f}:1  {THRESHOLD_NON_TEXT:>4.1f}  {status}",
                file=stream,
            )


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def _resolve_default_src() -> Path | None:
    env = os.environ.get("CHROMIUM_SRC")
    if env:
        candidate = Path(env) / "chrome/browser/ui/color/phlink_palette.cc"
        if candidate.is_file():
            return candidate
    here = Path(__file__).resolve().parent.parent
    candidate = (
        here.parent
        / "chromium-src"
        / "src"
        / "chrome/browser/ui/color/phlink_palette.cc"
    )
    if candidate.is_file():
        return candidate
    return None


def _resolve_patch_fallback() -> tuple[Path, Path] | None:
    here = Path(__file__).resolve().parent.parent / "patches"
    light = here / "0111-phlink-phase-08-02-light-theme-palette.patch"
    dark = here / "0112-phlink-phase-08-03-default-dark-theme.patch"
    if light.is_file() and dark.is_file():
        return light, dark
    return None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="phlink WCAG-AA contrast audit (D-07 lint mirror)."
    )
    p.add_argument(
        "--src-file",
        type=Path,
        help="path to chrome/browser/ui/color/phlink_palette.cc",
    )
    p.add_argument(
        "--self-test",
        action="store_true",
        help="run against hardcoded D-08 hex (no chromium-src needed).",
    )
    p.add_argument("src_positional", nargs="?", type=Path, help=argparse.SUPPRESS)
    args = p.parse_args(argv)

    if args.self_test:
        palettes = {"Light": SELF_TEST_LIGHT, "Dark": SELF_TEST_DARK}
        source = "<self-test: D-08 hardcoded>"
    else:
        src = args.src_file or args.src_positional or _resolve_default_src()
        if src and src.is_file():
            palettes_raw = parse_palette_file(src)
            source = str(src)
        else:
            fallback = _resolve_patch_fallback()
            if not fallback:
                print(
                    "ERROR: could not locate phlink_palette.cc or patch fallback. "
                    "Pass --src-file or --self-test.",
                    file=sys.stderr,
                )
                return 2
            palettes_raw = parse_palette_from_patches(*fallback)
            source = f"<patch fallback: {fallback[0].name} + {fallback[1].name}>"
        palettes = {"Light": palettes_raw["light"], "Dark": palettes_raw["dark"]}

    print(f"phlink contrast audit — source: {source}\n")
    _print_table(palettes)

    failures = []
    for mode_name, palette in palettes.items():
        failures += audit(palette, PAIRS_NORMAL, THRESHOLD_NORMAL, mode_name)
        failures += audit(palette, PAIRS_NON_TEXT, THRESHOLD_NON_TEXT, mode_name)

    print()
    if failures:
        print(f"FAIL — {len(failures)} pair(s) below WCAG-AA threshold:")
        for mode_name, fg, bg, ratio, threshold in failures:
            print(f"  {mode_name}: ({fg}, {bg}) = {ratio:.2f}:1 < {threshold:.1f}")
        return 1

    total = len(palettes) * (len(PAIRS_NORMAL) + len(PAIRS_NON_TEXT))
    print(f"PASS — 0 failures across {total} gated pair(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
