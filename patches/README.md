# `patches/` — phlink modifications to upstream Chromium

phlink customizes Chromium primarily via **bundled extensions and components** ([PRD §10.1](../docs/dev/PRD.md)). When that's not enough, we keep a **minimal patch set** here.

## Format

Each patch is a `git format-patch`-style file:

```
NNNN-short-slug.patch
```

- **`NNNN`** — four-digit ordering number (zero-padded). Patches apply in lexicographic order.
- **`short-slug`** — kebab-case description.

Examples:

```
0001-strip-google-services.patch
0010-rename-product-to-phlink.patch
0050-disable-safebrowsing-by-default.patch
```

## Authoring a new patch

You edit Chromium normally as a `git` working tree, then export your commits:

```bash
# In ../chromium-src/src/, after committing your changes on a topic branch:
python3 path/to/phlink/scripts/refresh-patches.py --base origin/HEAD --head HEAD
```

This regenerates `patches/*.patch` from the diff between `--base` and `--head`.

## Applying patches

```bash
python3 scripts/apply-patches.py            # applies all patches/*.patch in order
python3 scripts/apply-patches.py --dry-run  # show what would happen
python3 scripts/apply-patches.py --force    # apply over a dirty Chromium tree
```

The script uses `git am` inside `../chromium-src/src/`.

## Conflict policy

When upstream Chromium changes break a patch:

1. The maintainer attempting the rebase resolves the conflict in-tree.
2. They re-export with `refresh-patches.py`.
3. Commit the updated `.patch` file with the rebase commit, referencing the upstream version.

See [docs/dev/upstream-tracking.md](../docs/dev/upstream-tracking.md) for the full lifecycle.

## Phase 1 status

This directory ships **empty**. Real patches start arriving in Phase 3 (branding strip) and Phase 4 (telemetry strip).
