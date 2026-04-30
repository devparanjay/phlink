# Extension Model

> phlink's posture on browser extensions.

## Summary

phlink ships **no bundled WebExtensions**.
The ad-blocking and privacy features are built-in browser components, not extensions.

---

## Built-in ad blocking is not a WebExtension

The adblock engine (`adblock-rust` via `//chrome/browser/phlink/adblock/`) is a browser-process component.
It operates as a `blink::URLLoaderThrottle` for network blocking and a `RenderFrameObserver` for cosmetic injection.

This means:

- It cannot be disabled by websites (unlike content scripts).
- It has no extension ID and does not appear in `chrome://extensions`.
- It is not subject to Manifest V2 / V3 lifecycle changes.

---

## Chrome Web Store extensions

phlink supports installing extensions from Chrome Web Store URLs directly.
No Google account is required.
The install flow uses the standard Chromium WebStore install path (`//chrome/browser/extensions/`).

> **Note:** phlink does **not** bundle Google services or the Chrome sign-in infrastructure.
> Extensions that require a Google account (e.g., Google Docs Offline, Chrome Remote Desktop) may not work fully.

---

## Curated extension list

> **Note (deferred):** A phlink-curated extension discovery list (a vetted set of recommended extensions surfaced at first run) is planned for Phase 13/14.
> The Chrome Web Store URL install path investigation (to ensure extensions install without Google services) is tracked as Phase 13.

---

## Manifest V2 / V3

phlink follows Chromium's MV3 roadmap.
New bundled functionality targets MV3.
MV2 support is retained as long as upstream Chromium supports it.

---

## Developer reference

- Extension loading: `//chrome/browser/extensions/`
- Adblock component: `//chrome/browser/phlink/adblock/`
- Cosmetic injection: `//chrome/renderer/phlink/adblock/`
- Mojo interface: `//chrome/common/phlink_adblock.mojom`
