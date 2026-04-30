# Phase 3 — Identity & Branding Strip — PLAN

**Phase goal:** phlink-branded build with all Google services / sign-in stripped, and switchable default search engines preloaded with DuckDuckGo as default.

**Hard prerequisite:** `../chromium-src/src/` populated by `scripts/sync-chromium.sh`. Without it, no patches can be authored.

## Plans

### 03-01 — Product-string rename

**Goal:** all user-visible "Chromium" references in the chromium-lane GRD strings become "phlink"; `IDS_PRODUCT_NAME` is the single source.

**Files patched** (under `../chromium-src/src/`):

- `chrome/app/chromium_strings.grd` — change `IDS_PRODUCT_NAME` to "phlink", `IDS_SHORT_PRODUCT_NAME` to "phlink", `IDS_PRODUCT_DESCRIPTION` to a 1-sentence phlink tagline, `IDS_ABOUT_VERSION_COMPANY_NAME` to "phlink contributors".
- `chrome/app/generated_resources.grd` — only entries that hardcode "Chromium" instead of using `IDS_PRODUCT_NAME`. Audit; expect 5–15 entries.
- `chrome/installer/util/chromium_strings.grd` (and the macOS/linux installer string lanes if present) — installer text.
- `chrome/common/chrome_constants.cc` — product name constant if hardcoded; replace with the GRD-derived value where possible.

**Patches**: `0001-product-name-strings.patch` … up to `0005-installer-strings.patch`.

**Verification:**

1. `gn gen` + `autoninja chrome` succeeds.
2. Launched binary's title bar reads "phlink".
3. About page's product line reads "phlink".
4. `strings out/Default/chrome | grep -i Chromium | wc -l` is small (single digits). Document residue in `docs/dev/branding-residue.md`.

**Wave:** 1 (parallel with 03-02 asset prep — disjoint files).

---

### 03-02 — Logos, icons, splash, About-page assets

**Goal:** every Chromium-shipped raster/vector asset that represents the product is replaced with phlink's own.

**Pre-step (this repo, no Chromium source needed):** Brief stitch-mcp once for:

1. `product_logo.svg` master (mark only, no wordmark).
2. PNG raster set: 16, 32, 48, 64, 128, 256, 512 px in `assets/branding/png/`.
3. macOS `.icns` built via `iconutil` from raster set.
4. Windows `.ico` built via ImageMagick from raster set.
5. Wordmark lockup SVG for the About page.

Commit `assets/branding/` to the repo. License: BSD-3-Clause (project license).

**Files patched** (replace bytes; `git am` will move binaries fine):

- `chrome/app/theme/chromium/product_logo_*.png` (all sizes)
- `chrome/app/theme/chromium/product_logo.svg`
- `chrome/app/theme/chromium/mac/app.icns`
- `chrome/app/theme/chromium/win/chromium.ico` (rename target keeps "chromium" — that's a path, not a string)
- `components/resources/default_100_percent/chromium/product_logo_*.png` and `default_200_percent`
- About-page logo asset under `chrome/browser/resources/settings/`

**Patches**: `0006-product-logos.patch` … `0010-about-page-logo.patch`.

**Verification:**

1. Launch the build; confirm window icon, dock/taskbar icon, and About-page logo all show phlink's mark.
2. macOS: `Get Info` on the .app shows the phlink icon.
3. Windows: taskbar pin shows phlink icon.

**Wave:** 1 (assets) → Wave 2 (patches that consume the assets, after fetch completes).

---

### 03-03 — Google services strip

**Goal:** sign-in, sync, GAIA, Cast Receiver, and Safe Browsing v4 phone-home are off at compile time. Their UI surfaces are removed.

**GN args** (extend `build/gn-args/common.gni`):

```gn
enable_cast_receiver = false
enable_widevine = false
enable_gaia_services = false   # phlink-introduced; gate added in patch 0011
safe_browsing_mode = 0         # 0 = no Safe Browsing service
```

**Patches** (`0011`–`0020`):

- `0011-add-enable-gaia-services-flag.patch` — declares `enable_gaia_services` GN arg + `BUILDFLAG(ENABLE_GAIA_SERVICES)`; gates `chrome/browser/signin/`, `components/signin/`, `google_apis/gaia/` source sets.
- `0012-disable-sync-service.patch` — gates `components/sync/` and `chrome/browser/sync/` behind same flag.
- `0013-remove-signin-ui.patch` — drops the sign-in menu item, sign-in promos, and the profile-picker "sign in" affordance.
- `0014-remove-sync-settings-page.patch` — removes the Settings → People → Sync page entirely.
- `0015-disable-cast-ui.patch` — even with `enable_cast_receiver=false`, some "Cast…" menu items remain because they're sender-side. Strip them.
- `0016-disable-safebrowsing-v4-pingback.patch` — neutralizes the v4 update fetcher; we will revisit local-only Safe Browsing in a future phase.
- `0017-disable-field-trial-fetch.patch` — removes the variations-seed fetcher's network call. (Phase 4 will revisit; this is the brand-strip-related half.)
- `0018-remove-chrome-welcome-signin.patch` — drops the "sign in to Chrome" first-run promo.
- `0019-remove-google-apps-ntp.patch` — drops the Google-apps shortcut row from the New Tab Page.
- `0020-strip-help-google-feedback.patch` — `Help → Send Feedback` opened a Google form. Remove the menu item.

**Verification:**

1. Build succeeds.
2. No menu item, settings page, or NTP element references "sign in", "sync", "Google", or "Cast" except where the user explicitly added a Cast extension.
3. Network capture on launch: zero requests to `accounts.google.com`, `clients4.google.com`, `safebrowsing.google.com`, `clientservices.googleapis.com`. (Phase 4 will tighten this further.)

**Wave:** 3 (depends on 03-01 strings landing first to avoid string-table merge conflicts).

---

### 03-04 — Default search engine: DuckDuckGo

**Goal:** fresh profile points at DuckDuckGo. Brave Search, Startpage, Google, Bing remain selectable.

**Files patched:**

- `components/search_engines/prepopulated_engines.json` — set DDG as default for every locale entry; ensure `brave_search`, `startpage` exist with correct keywords (`brave`, `sp`); keep `google` and `bing` selectable.
- `components/search_engines/template_url_prepopulate_data.cc` — adjust the per-country default-id arrays if upstream codegen still embeds them post-JSON.

**Patches** `0021`–`0023`.

**Verification:**

1. Fresh profile: address bar query routes to `duckduckgo.com/?q=...`.
2. Settings → Search engine shows DDG selected, with Brave/Startpage/Google/Bing in the list.
3. Engine icons render correctly (favicons fetch from each engine domain on first use — that's expected non-Google traffic).

**Wave:** 2 (independent of 03-03; can land in parallel).

---

### 03-05 — Chrome Web Store install without Google account

**Goal:** `chrome.google.com/webstore/...` install flow works without a Google sign-in. Where upstream gates an action behind sign-in, we either bypass or surface a clear error.

**Files patched:**

- `chrome/browser/extensions/webstore_installer.cc` and `webstore_install_with_prompt.cc` — bypass the sign-in precondition.
- `chrome/browser/ui/webui/webstore/...` — remove the "sign in to install" prompt UI; replace with a normal install confirmation.
- `chrome/browser/extensions/install_verifier.cc` — Chromium's install verifier is already a no-op when Google APIs are blank. Confirm; no patch likely needed.

**Patches** `0024`–`0026`. Expect ~150–300 LOC.

**Verification:**

1. Visit `chrome.google.com/webstore/detail/<some-popular-extension>/...`.
2. Click Add to phlink → install flow completes without a sign-in modal.
3. Extension loads and runs.

**Risk:** the CWS may server-side-require sign-in for some endpoints; document those as known limitations in `docs/user/extensions.md` (Phase 11).

**Wave:** 3.

---

### 03-06 — Curated phlink-vetted extension list (first-run discovery)

**Goal:** on first launch (or via a settings entry), the user sees a small phlink-curated list of recommended extensions with one-click install via the patched CWS path from 03-05.

**Repo-side deliverables (no Chromium source needed):**

- `phlink/curated_extensions.json` — schema: `[{id, name, description, category, cws_url, why_recommended}]`. Initial list: uBlock Origin Lite (we ship our own adblock; this is for users who want extra), Bitwarden, Privacy Badger, Wayback Machine, ClearURLs.
- `docs/dev/curated-extensions.md` — criteria for inclusion (OSS, no telemetry, MV3-ready), review process, removal process.
- A copy step in `scripts/gn-gen.{sh,ps1}` that copies `phlink/curated_extensions.json` into `../chromium-src/src/chrome/browser/resources/phlink/` before `gn gen` runs. (No Chromium-side patch needed for the file itself.)

**Chromium-side patches `0027`–`0030`:**

- `0027-add-curated-extensions-resource.patch` — registers the JSON as a resource bundle entry.
- `0028-add-curated-extensions-webui.patch` — minimal `chrome://phlink-extensions` WebUI page that reads the JSON and renders cards.
- `0029-first-run-curated-extensions-step.patch` — wires the new WebUI into the first-run experience.
- `0030-settings-curated-extensions-link.patch` — Settings → Extensions has a "Recommended for phlink" link to the WebUI.

**Verification:**

1. Fresh profile launch: first-run shows the curated list.
2. Click "Install" on one — completes without sign-in (depends on 03-05).
3. Visit `chrome://phlink-extensions` → list renders.
4. Settings → Extensions → "Recommended for phlink" link works.

**Wave:** 4 (depends on 03-05).

## Dependency graph

```
fetch chromium (Phase 1.x sync) [blocking, in progress]
  ├─► Wave 1: 03-01 (strings), 03-02 pre-step (assets via stitch-mcp)
  │     └─► Wave 2: 03-02 patches (consume assets), 03-04 (search engines)
  │           └─► Wave 3: 03-03 (Google services strip), 03-05 (CWS path)
  │                 └─► Wave 4: 03-06 (curated extensions UI)
```

## Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Chromium fetch fails or times out | High | Re-run `scripts/sync-chromium.sh`; fall back to `gclient sync` manually |
| `enable_gaia_services` flag has unforeseen build dependents | Medium | Land 0011 in isolation first, fix follow-on build breaks one by one |
| CWS server-side requires sign-in for the extensions on the curated list | Medium | Re-curate list around extensions that don't gate; update curated-extensions.md |
| `prepopulated_engines.json` codegen schema changed in current Chromium stable | Medium | Read the codegen Python in `components/search_engines/` first; adapt |
| Patch conflicts on next Chromium rebase | Low (this phase) → Medium (long-term) | Phase 3 patches are deliberately small and target leaf files |

## Out of scope (do not creep)

- Telemetry strip → Phase 4.
- DoH defaults → Phase 4.
- Real Safe Browsing replacement → future phase.
- Final logo polish / wordmark refinement → Phase 12.
- Localizing phlink strings beyond en-US → Phase 11/12.
