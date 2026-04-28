# `patches/` — phlink modifications to upstream Chromium

phlink customizes Chromium primarily via **bundled extensions and components** ([PRD §10.1](../docs/dev/PRD.md)). When that's not enough, we keep a **minimal patch set** here.

## Layout

```
patches/
  NNNN-slug.patch                                   # applies at <chromium-src>/src/
  <reldir>/NNNN-slug.patch                          # applies at <chromium-src>/src/<reldir>/
```

`<reldir>` mirrors a path inside the Chromium checkout. It is typically a
**git submodule** (Chromium pulls many third-party trees as submodules
via `gclient`). Each submodule we touch gets its own subdirectory under
`patches/`, and patches in that subdirectory are applied with
`git am` run from inside that submodule.

Currently active subtrees:

| Subtree | Slot range |
|---|---|
| `.` (chromium/src root) | 0001–0099 (Phase 3 branding) |
| `third_party/search_engines_data/resources` | 0021–0029 (search defaults) |

## Filename format

```
NNNN-short-slug.patch
```

- **`NNNN`** — four-digit ordering number (zero-padded). Patches in the
  same subtree apply in lexicographic order.
- **`short-slug`** — kebab-case description.

## Authoring a new patch

You edit Chromium normally as a `git` working tree, then export your commits.

For changes inside a submodule (e.g. `third_party/search_engines_data/resources`),
commit **inside the submodule** so the diff stays scoped to that subtree.
For root-level changes, commit at `chromium-src/src/`.

```bash
# After committing your changes:
python3 path/to/phlink/scripts/refresh-patches.py
# Default: regenerates patches for every known subtree in this file.
# Override per-subtree slot base if needed:
python3 .../refresh-patches.py --subtree .=1 \
                               --subtree third_party/search_engines_data/resources=21
```

## Applying patches

```bash
python3 scripts/apply-patches.py            # applies all patches/**/*.patch in order
python3 scripts/apply-patches.py --dry-run  # show what would happen
python3 scripts/apply-patches.py --force    # apply over a dirty Chromium tree
```

For each subtree found under `patches/`, the script `cd`s into the matching
location in `../chromium-src/src/` and runs `git am --3way` for the patches there.

## Conflict policy

When upstream Chromium changes break a patch:

1. The maintainer attempting the rebase resolves the conflict in-tree (in the
   correct subtree's git work-tree).
2. They re-export with `refresh-patches.py`.
3. Commit the updated `.patch` file referencing the upstream version.

See [docs/dev/upstream-tracking.md](../docs/dev/upstream-tracking.md) for the
full lifecycle.

## Phase 3 status

Active patches: see the slot-range table above. The Phase 3 plan in
`.planning/phases/03-identity-and-branding-strip/` allocates 0001–0099.
