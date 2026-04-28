# Tracking upstream Chromium

> phlink tracks **Chromium stable**. We rebase on each stable bump. This doc explains the rebase cadence, the patch lifecycle, and the conflict-resolution playbook.

## Rebase cadence

- **Trigger:** new Chromium stable channel release ([release schedule](https://chromiumdash.appspot.com/schedule)).
- **SLA:** phlink picks up the new stable within **two weeks** of upstream release in normal weeks, **48 hours** for security-only point releases.
- **Owner:** rotating maintainer. The rebase is tracked as a GitHub issue with the milestone tag `chromium-stable-<MAJOR>`.

We do not track `dev` or `canary`. We do not pin to a specific point release between bumps unless a security release demands it.

## Patch model

Customizations land via two mechanisms, in this order of preference:

1. **Bundled extensions / components** — preferred. Lives entirely inside this repo and never touches Chromium source.
2. **Minimal patch set** in [`patches/`](../../patches/) — used only when (1) is impossible (e.g. modifying default search engines, branding, telemetry strip, integrating `adblock-rust` at the network layer).

Anything that *can* be an extension *should* be an extension. The patch set must stay small and well-justified.

## Patch lifecycle

### Authoring a new patch

You work inside the Chromium checkout (`../chromium-src/src/`) as a normal git tree:

```bash
cd ../chromium-src/src
git checkout -b phlink/disable-foo origin/HEAD
# … edit files, build, test …
git commit -am "phlink: disable foo by default

Why: <rationale>
Tracking issue: phlink#NNN
"
```

When the change is ready, export it to phlink:

```bash
cd path/to/phlink
python3 scripts/refresh-patches.py --base origin/HEAD --head phlink/disable-foo
```

This regenerates everything in `patches/`. Review the diff, commit it to phlink:

```bash
git add patches/
git commit -m "Add patch: disable foo by default

Refs #NNN
"
```

Open the PR against `phlink/main`.

### Naming convention

`NNNN-short-slug.patch` — see [patches/README.md](../../patches/README.md).

Reserve number ranges loosely:

| Range | Purpose |
|---|---|
| 0001–0099 | Branding & identity (Phase 3) |
| 0100–0199 | Telemetry strip (Phase 4) |
| 0200–0299 | Adblock integration hooks (Phase 5) |
| 0300–0399 | Privacy hardening (Phase 6) |
| 0400–0499 | Performance (Phase 7) |
| 0500–0599 | Appearance / UI (Phase 8) |
| 0900+ | Misc / one-offs |

These are guidelines, not enforcement — apply order is purely lexicographic.

## Rebase playbook

When a new Chromium stable lands:

1. **Bump the upstream pin.** Update `scripts/sync-chromium.sh` if we pin a specific channel ref, otherwise `gclient sync` picks up the new tip.
2. **Re-fetch Chromium source.**
   ```bash
   cd ../chromium-src/src
   git fetch origin
   git checkout origin/HEAD
   gclient sync
   ```
3. **Try applying the patch set.**
   ```bash
   cd path/to/phlink
   python3 scripts/apply-patches.py
   ```
4. **If clean:** rebuild, run the smoke suite, ship.
5. **If `git am` reports a conflict:** the script aborts and reports the offending patch. Resolve in-tree:
   ```bash
   cd ../chromium-src/src
   git am --3way patches/NNNN-foo.patch    # or use the path the apply script printed
   # … resolve conflicts in your editor …
   git add -u
   git am --continue
   ```
   Then **regenerate the patch** so the resolution is captured:
   ```bash
   cd path/to/phlink
   python3 scripts/refresh-patches.py --base <new-upstream-tip> --head HEAD
   ```
6. **Update the changelog.** Note the upstream version bump and any patches that needed manual conflict resolution.
7. **PR title:** `chore: rebase on Chromium <MAJOR>.<MINOR>.<BUILD>.<PATCH>`.

## When to drop a patch

Drop a patch when **upstream has incorporated equivalent behavior**, e.g.:

- Chromium adds a feature flag for what we were patching.
- Chromium changes the default to match phlink's default.

Document the drop in the rebase PR (`Removed: 0123-foo.patch — superseded by upstream flag <name>`).

## When to upstream a patch

Some phlink patches are good citizens for upstream Chromium. Send them via Gerrit (`crrev.com`) following the [Chromium contribution process](../../.refs/chromium/chromium@main/docs/contributing.md). Keep the local patch in phlink until the Gerrit CL lands and rolls into stable.

## Reference

- [PRD §10.1 — Build base](PRD.md) — locked decision to track Chromium stable
- [`.refs/chromium/chromium@main/docs/contributing.md`](../../.refs/chromium/chromium@main/docs/contributing.md) — upstream contribution process
- [`patches/README.md`](../../patches/README.md) — patch format
- [`docs/dev/build.md`](build.md) — local build procedure
