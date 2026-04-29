# phlink Architecture

> Single-page tour of how phlink is structured on top of upstream Chromium. Companion to [PRD.md](PRD.md) (the *what*) and [build.md](build.md) (the *how do I build it*). This doc is the *how does it fit together*.
>
> Last updated: 2026-04-29 (branch `dev-0.1`, patches `0001`–`0102`).

## 1. Repository layout

phlink is **not** a Chromium fork in the git sense. The phlink repo holds a small overlay:

```
phlink/                          # this repo
├── patches/        0001…010N    # ordered patch series applied to upstream src/
├── patches/third_party/         # files added under upstream third_party/ (e.g., search engines)
├── build/gn-args/               # canonical args.gn fragments per platform + common
├── scripts/                     # bootstrap, sync, gn-gen, build, refresh-patches
├── docs/{dev,user}/             # this documentation
├── tests/                       # phlink-only test harnesses (e.g., 60-tab benchmark)
└── branding/                    # logo masters, raster pipeline
```

The actual Chromium checkout lives **outside** this repo at `/Volumes/Tools/dev/chromium-src/src` (developer-local, branch `phlink-wip`). [scripts/apply-patches.py](../../scripts/apply-patches.py) replays `patches/*.patch` onto a clean `chromium/main` checkout. [scripts/refresh-patches.py](../../scripts/refresh-patches.py) regenerates the series from the working tree after a hand-edit.

## 2. The patch series

Each patch is a focused, atomic change that maps 1:1 to a phase or sub-phase plan in [.planning/ROADMAP.md](../../.planning/ROADMAP.md). The numbering encodes *order* (the series applies in numeric order), not phase number — early identity/telemetry patches occupy `0001`–`0012`, the adblock subsystem occupies `0090`–`0100`, privacy posture lives in `0101`–`010N`. New patches append at the end.

A patch must:

1. Apply cleanly on top of the chosen Chromium stable rebase point.
2. Build with the canonical [build/gn-args/common.gni](../../build/gn-args/common.gni).
3. Pass any unit test it adds plus the existing `unit_tests` target.
4. Carry a single-purpose commit message starting with `phlink: ` or `phlink phase NN-MM: `.

## 3. Layered architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  UI layer:  chrome/browser/resources/settings/  ← Phase 8 entry      │
├──────────────────────────────────────────────────────────────────────┤
│  Browser process:                                                    │
│   - Identity / telemetry strip          patches 0001–0012            │
│   - DoH default + provider list         patch 0006                   │
│   - GAIA / OneGoogleBar / GCM stubs     patches 0008–0010            │
│   - Component updater pin               patches 0099, 0100           │
│   - 3p cookie + state-isolation flips   patches 0101–0102            │
├──────────────────────────────────────────────────────────────────────┤
│  Adblock subsystem (Phase 5):                                        │
│   ┌─────────────────────────────────────────────────────────────┐    │
│   │ chrome/browser/phlink_adblock/                              │    │
│   │  ├─ engine wrapper (cxx bridge → adblock-rust)              │    │
│   │  ├─ URLLoaderThrottle (network-layer block)                 │    │
│   │  └─ Mojo bridge → renderer cosmetic agent                   │    │
│   └─────────────────────────────────────────────────────────────┘    │
│   third_party/rust/adblock/v0_12 (MPL-2.0)  ← gnrt-vendored          │
│   third_party/phlink_filter_lists/ (EasyList, EP, uBO, Brave, PL)    │
├──────────────────────────────────────────────────────────────────────┤
│  Renderer process:                                                   │
│   - Cosmetic agent (CSS injection via WebDocument::InsertStyleSheet) │
│   - Site isolation: ON (PRD §10.1 D-04, never weakened for perf)     │
├──────────────────────────────────────────────────────────────────────┤
│  Network service:                                                    │
│   - Storage partitioned by top-level site (patch 0102)               │
│   - 3p cookies blocked by default (patch 0101)                       │
└──────────────────────────────────────────────────────────────────────┘
```

## 4. Subsystem deep-links

| Subsystem | Phase | Entry doc / patches |
| --- | --- | --- |
| Build / refs cache / patches | 1 | [build.md](build.md), [refs-cache.md](refs-cache.md), [upstream-tracking.md](upstream-tracking.md), patches `0001`–`0002` |
| CI matrix (mac/linux/win) | 2 | [ci.md](ci.md) |
| Identity strip | 3 | patches `0001`–`0002` (BRANDING, IDS_PRODUCT_NAME) |
| Telemetry zeroing | 4 | patches `0003`–`0012` (metrics, crash, variations, NTS, GAIA, OGB, GCM, AIM) |
| Adblock | 5 | patches `0090`–`0100`, [phase-08-scoping.md](phase-08-scoping.md) (settings UI dependency) |
| Privacy defaults | 6 | patches `0006`, `0101`–`0102` |
| Performance | 7 | [tests/benchmark_60tab/](../../tests/benchmark_60tab/) (07-05 only; 07-01..04 deferred to 7.5) |
| Appearance | 8 | [phase-08-scoping.md](phase-08-scoping.md) — implementation deferred |
| Profile export/import | 9 | not started |
| Updater + installers | 10 | not started; current `updates.phlink.invalid` placeholder set in patch `0099` |
| Docs + license audit | 11 | this file, [third-party-licenses.md](third-party-licenses.md), [mcp-workflow.md](mcp-workflow.md) |

## 5. Process model

phlink does not change Chromium's process model. **Site isolation stays ON** ([PRD §10.1 D-04](PRD.md)). All performance gains come from a smarter discarder, throttling, and tab-grouping awareness — never from collapsing renderers into the browser process or weakening sandbox boundaries.

The cosmetic adblock agent runs in the renderer with the same privilege as page CSS — it does not get elevated capabilities and cannot be persuaded by page script to do anything beyond inject site-scoped stylesheets sourced from the trusted browser-process bridge.

## 6. Threading and IPC

- Browser ↔ renderer: Mojo (one phlink-introduced interface in patch `0096`, the cosmetic bridge).
- Browser ↔ network service: existing Chromium URLLoaderThrottle interface (patch `0093`); no new IPC surface.
- Adblock engine: lives on a single sequenced TaskRunner inside the browser process; never touched off-sequence.

See `.refs/chromium/chromium@main/docs/threading_and_tasks.md` and `mojo_and_services.md` for upstream rules. phlink follows them — no `base::ThreadPool::PostTask` from arbitrary threads, no nested message loops in browser code, no synchronous Mojo calls except where upstream already does.

## 7. Where new code goes

| Need | Goes here | Rationale |
| --- | --- | --- |
| New phlink-only browser feature | `chrome/browser/phlink_<feature>/` (new directory) | Keeps phlink code grep-able and easy to lift into an upstream patch. |
| Extension to existing Chrome subsystem | A patch that edits `chrome/browser/<subsystem>/` in place | Smaller diff, easier to rebase across stable bumps. |
| Rust crate | Add to `chromium_crates_io/Cargo.toml`, run `gnrt vendor`, ship the resulting `third_party/rust/<name>/<version>/` in a new patch. | Matches the path adblock-rust took (patch `0090`). |
| First-party data (filter list, search engine, theme token) | `third_party/phlink_<name>/` with `LICENSE`, `README.chromium`, `BUILD.gn`. | Matches Chromium's third-party conventions and keeps the license audit pure-mechanical. |

## 8. What phlink deliberately does **not** do

- No new processes, no new sandboxes, no IPC to a phlink-controlled service.
- No outbound network requests originating from the browser other than what the user initiated, the adblock list updater (gated on consent, Phase 5-07 → Phase 10 hardening), and the TUF update probe (Phase 10).
- No telemetry, no analytics, no opt-in metrics — even on debug builds.
- No proprietary blobs, ever.

These are locked decisions; do not re-litigate without an [PRD §10.1](PRD.md) update.
