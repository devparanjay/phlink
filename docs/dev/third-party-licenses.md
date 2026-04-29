# Third-Party Licenses

> Comprehensive inventory of every third-party dependency, filter list, and asset that ships in a phlink build, with its license. This doc satisfies success criterion §11.3 of [.planning/ROADMAP.md](../../.planning/ROADMAP.md). It does **not** duplicate Chromium's own `LICENSES.chromium.html` — that file already covers the upstream tree. This doc covers what **phlink adds on top** via the patch set in [patches/](../../patches/).
>
> Inventory date: 2026-04-29 (sync with patches `0001`–`0102` on branch `dev-0.1`).

## 1. License compatibility policy

Per [.github/copilot-instructions.md §11](../../.github/copilot-instructions.md) and [PRD.md §10.1](PRD.md):

- **Allowed** in shipped binaries: BSD-2/3-Clause, MIT, Apache-2.0, MPL-2.0, ISC, zlib, Unicode-DFS-2016, Unlicense / public domain.
- **Allowed only as build-tooling / test-only**, never linked into the shipped browser: GPL-2.0, GPL-3.0, LGPL-2.1, LGPL-3.0, AGPL.
- **Forbidden anywhere in the shipped repo**: anything proprietary, anything restricting redistribution, "non-commercial use only", "research use only", or any term the OSI does not list as Open Source.

`docs/dev/PRD.md §10.1` calls out the BSD-3-Clause + MPL-2.0 mix as the existing baseline (Chromium core + adblock-rust). Apache-2.0 and MIT additions are compatible with both.

## 2. Rust crates (vendored via `gnrt`)

Source patch: [patches/0090-phlink-vendor-adblock-rust-0.12.2-via-gnrt.patch](../../patches/0090-phlink-vendor-adblock-rust-0.12.2-via-gnrt.patch). All crates land under `//third_party/rust/<name>/<version>/`.

| Crate | Version | License | Role |
| --- | --- | --- | --- |
| `adblock` | 0.12 | **MPL-2.0** | Brave's `adblock-rust` — phlink's network + cosmetic filter engine. The keystone dependency. |
| `addr` | 0.15 | Apache-2.0 | Public Suffix List domain matching. |
| `flatbuffers` | 25 | Apache-2.0 | Serialization for compiled rule cache. |
| `form_urlencoded` | 1 | Apache-2.0 / MIT | URL form encoding. |
| `idna` | 1 | Apache-2.0 / MIT | IDNA hostname normalization. |
| `idna_adapter` | 1 | Apache-2.0 / MIT | Bridge between `idna` and `unicode-normalization`. |
| `itertools` | 0.13 | Apache-2.0 / MIT | Iterator combinators. |
| `percent-encoding` | 2 | Apache-2.0 / MIT | Percent-encoding helper. |
| `precomputed-hash` | 0.1 | MIT | Hash trait used by `selectors`. |
| `psl` | 2 | Apache-2.0 / MIT | Public Suffix List runtime. |
| `psl-types` | 2 | Apache-2.0 / MIT | Type definitions for `psl`. |
| `regex` | 1 | Apache-2.0 / MIT | Filter parser regex. |
| `rustc-hash` | 1 | Apache-2.0 / MIT | Fast `HashMap` for hot paths. |
| `rustc_version` | 0.4 | Apache-2.0 / MIT | Build-script compiler-version detection. |
| `seahash` | 4 | MIT | Hash algorithm. |
| `semver` | 1 | Apache-2.0 / MIT | Used by `rustc_version`. |
| `thiserror` | 1 | Apache-2.0 / MIT | Error-type derive. |
| `thiserror-impl` | 1 | Apache-2.0 / MIT | Proc-macro half of `thiserror`. |
| `url` | 2 | Apache-2.0 / MIT | URL parsing. |

**Verdict:** all clean. No GPL / LGPL / AGPL anywhere in the linked binary.

## 3. Bundled filter lists

Source patch: [patches/0094-phlink-phase-5-04-bundled-filter-lists.patch](../../patches/0094-phlink-phase-5-04-bundled-filter-lists.patch). All lists land under `//third_party/phlink_filter_lists/lists/` with adjacent `LICENSE.*` files and a Chromium-style `README.chromium`.

| List | File | License | Source / upstream |
| --- | --- | --- | --- |
| EasyList | `lists/easylist.txt` | **CC BY-SA 3.0** + GPL-3.0 (dual) — phlink relies on the CC BY-SA branch. | https://easylist.to/easylist/easylist.txt |
| EasyPrivacy | `lists/easyprivacy.txt` | CC BY-SA 3.0 + GPL-3.0 (dual) — CC branch. | https://easylist.to/easylist/easyprivacy.txt |
| Peter Lowe's Ad and Tracking server list | `lists/peter_lowe.txt` | **CC BY 4.0** | https://pgl.yoyo.org/adservers/ |
| uBlock Origin filters (core) | `lists/ubo-filters.txt` | **GPL-3.0**, used **as data, not code** (no GPL code is linked into the binary) | https://github.com/uBlockOrigin/uAssets `filters/filters.txt` |
| uBlock Origin badware | `lists/ubo-badware.txt` | GPL-3.0 (data) | uAssets `filters/badware.txt` |
| uBlock Origin privacy | `lists/ubo-privacy.txt` | GPL-3.0 (data) | uAssets `filters/privacy.txt` |
| uBlock Origin resource-abuse | `lists/ubo-resource-abuse.txt` | GPL-3.0 (data) | uAssets `filters/resource-abuse.txt` |
| uBlock Origin unbreak | `lists/ubo-unbreak.txt` | GPL-3.0 (data) | uAssets `filters/unbreak.txt` |
| Brave-specific | `lists/brave-specific.txt` | **MPL-2.0** | brave/adblock-lists `brave-lists/brave-specific.txt` |

**Note on GPL-licensed filter lists:** these are shipped as **data** consumed by the MPL-2.0 `adblock-rust` parser — no GPL code is compiled into the binary. This is the same posture Brave Browser uses (see Brave's own `LICENSES.chromium.html`). The lists live alongside `LICENSE.ublock` (GPL-3.0 verbatim copy) so the source distribution is self-contained.

If a future filter list arrives under license terms incompatible with redistribution-as-data, it does not ship by default; users may add it via the user-supplied list mechanism (Phase 5-06b, deferred).

## 4. Bundled assets

| Asset | Path | License | Source |
| --- | --- | --- | --- |
| phlink branding (BRANDING file, IDS_PRODUCT_NAME, app icons) | `chrome/app/theme/phlink/...` (via patches `0001`, `0002`) | This repo's BSD-3-Clause (matches Chromium's `//chrome/app/theme/chromium/`). | First-party. |
| Search engine data (DuckDuckGo default + Brave/Startpage/Google/Bing preloads) | [patches/third_party/search_engines_data/resources/](../../patches/third_party/search_engines_data/resources/) | BSD-3-Clause (Chromium prepopulated_engines.json patch format). | First-party data, derived from upstream Chromium structure. |

No third-party fonts, images, sounds, or video ship as part of phlink's customizations.

## 5. Components explicitly **not** linked

These are commonly-shipped Chromium components that phlink hard-disables (see patches `0003`–`0012`, `0011`–`0012`) and therefore does **not** redistribute or rely on:

- Google Update / Omaha
- Google Cast Receiver, Widevine CDM
- GAIA Cookie Manager, One Google Bar, AIM probe
- Network Time Service polling, Variations seed fetch
- GCM device check-in / registration

These remain present in the upstream Chromium source we build against, but are short-circuited in the binary. They contribute no additional license obligations to phlink.

## 6. Verification

Until the Phase 11-04 CI license-compatibility check lands, this file is the authoritative reviewer-facing manifest. PRs adding any new dependency **must** add a row here in the same PR or be rejected. The check itself (Phase 11-04) will mechanically diff this file against `git ls-tree`-derived inventory and fail when the two disagree.

## 7. Upstream Chromium

Everything in the upstream Chromium tree is governed by [`LICENSES.chromium.html`](https://chromium.googlesource.com/chromium/src/+/main/LICENSES.chromium.html) generated at build time from the source `LICENSE` files. phlink does not duplicate that catalog here; the build emits the same file into the shipped binary's `Resources/` (or equivalent) directory unchanged.
