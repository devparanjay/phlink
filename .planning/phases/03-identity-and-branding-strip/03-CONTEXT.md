# Phase 3 — Identity & Branding Strip — CONTEXT

> Sourced from upstream Chromium documentation in `.refs/chromium/chromium@main/docs/google_chrome_branded_builds.md` and the locked PRD §10.1 decisions. **Do not** add Google-branded paths or `is_chrome_branded=true` code paths anywhere in this phase.

## Phase Goal (from ROADMAP)

phlink-branded build with all Google services / sign-in stripped, and switchable default search engines preloaded with DuckDuckGo as default.

## Requirements covered

`BRND-01`, `BRND-02`, `BRND-03`, `BRND-04`, `CORE-08`, `CORE-09`.

## Decisions

### D-01 — Brand name and product token

The product name is **phlink** (lowercase `p`). It appears verbatim in the title bar, About dialog, app menu, taskbar, application id, install path, profile path, and User-Agent product token (`phlink/<version>` after the `Chrome/<version>` token, as Brave does).

### D-02 — We patch the `chromium_strings.grd` lane, not the `google_chrome_strings.grd` lane

Per `.refs/chromium/chromium@main/docs/google_chrome_branded_builds.md`, Chromium ships two parallel string lanes:

- `//chrome/app/chromium_strings.grd` — used when `is_chrome_branded = false` (our case; locked in `build/gn-args/common.gni`).
- `//chrome/app/google_chrome_strings.grd` — Google-internal, never our concern.

phlink lives in the chromium lane. We never set `is_chrome_branded = true`. The patches in this phase rewrite the **chromium lane** strings from "Chromium" → "phlink" and the company string from "The Chromium Authors" → "phlink contributors".

### D-03 — Asset replacement, not asset addition

We replace contents of `//chrome/app/theme/chromium/` (and `//components/resources/.../chromium/`) in-place rather than introducing a third brand. This keeps the patch set narrow and the upstream rebase cheap. Stitch-mcp generates the assets per CLAUDE.md tooling rules.

### D-04 — Google services strip strategy

Strip is implemented in three layers, **lightest first**:

1. **GN args** (`build/gn-args/common.gni`, already in Phase 1): `use_official_google_api_keys=false`, blank API keys, `is_chrome_branded=false`. Already neuters most upstream phone-home defaults.
2. **Build-time feature flags**: define a `phlink_disable_*` set of GN args that gate compilation of sign-in, sync, GAIA, Cast Receiver, and the v4 Safe Browsing service. Where upstream already exposes a flag (e.g. `enable_widevine`, `enable_cast_receiver`), set it to false. Where upstream does not (e.g. sync), patch `BUILD.gn` to gate the source set on a phlink flag.
3. **Patches** under `patches/` for the residue: removing UI surfaces, menu items, and settings pages that reference signed-in / sync / casting features. These are MV-style "remove the option entirely" patches, not feature-flag toggles.

Sequence matters: GN args first, then build-flag patches, then UI-strip patches. Each layer reduces the diff the next layer has to produce.

### D-05 — Search-engine list source

The default search-engine list lives in `//components/search_engines/prepopulated_engines.json` and is consumed by the codegen at build time. We patch the JSON to:

- Set DuckDuckGo (`duckduckgo`) as default for **all locales**.
- Keep `brave_search`, `startpage`, `google`, `bing` available.
- Remove default-position entries for Google (so a fresh profile never points at Google).

We do **not** delete Google from the engine list — users can still pick it. We only change the default.

### D-06 — Chrome Web Store URLs without a Google account

The Chrome Web Store install path is patched to:

- Remove the GAIA sign-in prompt before install.
- Use anonymous CWS endpoints where they exist; for endpoints that mandate sign-in, surface a clear "this extension requires a Google account, which phlink does not provide — install manually instead" message.

This is not a clean upstream pattern; expect ~150–300 LOC of patch diff in `chrome/browser/extensions/webstore_install_*` and `chrome/browser/ui/webui/...`.

### D-07 — Curated extension list

The "phlink-vetted" first-run extension discovery list is **content**, not code. It lives at `//chrome/browser/resources/phlink/curated_extensions.json` (a new file we add via patch) and is rendered by a small WebUI surface. The list itself ships under `phlink/curated_extensions.json` in this repo and is mirrored into the Chromium tree by an `apply-patches.py` extension or a build step. We pick the simpler: copy at `gn-gen` time via a script, no patch.

### D-08 — UA product token

Set via patch in `//content/common/user_agent.cc` to append ` phlink/<version>` after the existing Chromium product token. We do **not** strip the `Chrome/<version>` token — site-compat depends on it (Brave, Edge, Vivaldi all keep it).

### D-09 — Patch slot allocation

This phase consumes patch slots `0001`–`0030` per `docs/dev/upstream-tracking.md`. Concretely:

| Range | Plan | Topic |
|---|---|---|
| 0001–0005 | 03-01 | Product-string rename (chromium_strings.grdp + .grd updates) |
| 0006–0010 | 03-02 | Logos / icons / splash / About-page assets |
| 0011–0020 | 03-03 | Google-services strip (sign-in, sync, GAIA, Cast, SBv4) |
| 0021–0023 | 03-04 | Search-engine prepopulated_engines.json edits |
| 0024–0026 | 03-05 | CWS-install path without Google account |
| 0027–0030 | 03-06 | First-run curated-extension UI surface |

If a plan goes over its allotment, renumber rather than overrun the next plan's range.

### D-10 — User-visible string convention

Where strings can be derived programmatically from the `IDS_PRODUCT_NAME` GRD message, we **do not** hardcode "phlink". We change `IDS_PRODUCT_NAME` once and let the rest follow. Hardcoded fallbacks like "Chromium" in `chrome/installer/...` get rewritten to "phlink" because the installer string tables are their own thing.

### D-11 — Splash / first-run / About page

- About page: lives in `chrome/browser/resources/settings/about_page/`. Replace the Chromium logo asset, change "Chromium" string to "phlink", replace the credits link with `chrome://credits` (which already exists upstream).
- First-run experience: phlink hides the upstream "sign in to Chrome" first-run page entirely (it's behind a feature flag we'll force-off in 03-03). The replacement is a 2-page first-run that says *"Welcome to phlink. Default search is DuckDuckGo. Adblock is on."* and offers the curated-extension list (03-06).

### D-12 — Stitch-mcp tasks

Three logo deliverables required for Phase 3:

1. **product_logo** — square mark, target raster sizes 16/32/48/64/128/256/512 px and an SVG master. Used in window icon, taskbar, About page.
2. **app_icon_mac** — `.icns` bundle (built from the master via `iconutil`).
3. **app_icon_win** — `.ico` bundle (built from the master via ImageMagick).
4. **splash_logo** (optional, only if upstream still has a splash on Windows) — wider lockup with wordmark.

We brief stitch-mcp once, in 03-02. Output goes to `assets/branding/` in this repo and is wired into the Chromium tree via patches in slot 0006–0010.

### D-13 — License / trademark

phlink's logo is original work licensed under the project's existing license (BSD-3-Clause). We do **not** import any Google or Chromium trademarked asset. We do **not** import any third-party logo set. The phlink wordmark uses an OSS font (Inter or similar; finalize in 03-02).

### D-14 — Verification approach

Per-plan verification is in `03-PLAN.md`. Phase-level verification:

1. Build phlink locally (Phase 1 procedure). Launch.
2. Search the running binary for stray "Chromium"/"Google" strings: `strings phlink | grep -iE 'chromium|google'`. Expect only legitimate residue (e.g. `Chrome/<version>` UA token, Mojo type names, internal class names). Document the allowlist of "expected residue" in `docs/dev/branding-residue.md`.
3. Open Settings → About; confirm name + logo + version display correctly.
4. Open a fresh profile; confirm DuckDuckGo is the default search.
5. Capture network on launch — confirm zero requests to `*.google.com`, `*.googleapis.com`, `*.gstatic.com`, `*.gvt1.com`, `*.googleusercontent.com`. (The deeper telemetry verification is Phase 4; this is the smoke check.)
6. Confirm UA contains ` phlink/<version>`.

### D-15 — Out of scope for Phase 3

- Telemetry strip (UMA, crash reporter, variations) — that's **Phase 4**. Phase 3 only handles Google **services / sign-in / sync / Cast / SafeBrowsing-v4** wiring.
- DoH defaults — **Phase 4**.
- Adblock — **Phase 5**.
- Theme engine — **Phase 8**. Phase 3's branding work uses Chromium's existing theming primitives.
- Final logo design polish — Phase 12 may revisit.

### D-16 — Blocking dependency

All six plans in this phase **require a populated `../chromium-src/` tree** (Phase 1 sync completed). Without source, we cannot author the patches against real line numbers and surrounding context. The fetch is currently in progress (terminal `0d99d787-a1ff-498d-b2d7-fc6efb267be3`).

### D-17 — Working branch

Continue on `dev-0.1`. No need for a per-phase branch — the project's commit graph keeps phases atomic at commit granularity.
