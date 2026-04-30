# phlink Features

> What makes phlink different from stock Chromium.

## Ad and tracker blocking (Shield)

phlink ships a built-in ad and tracker blocker powered by `adblock-rust` (Brave, MPL-2.0).
No extension required.

**Default filter lists included:**

- EasyList
- EasyPrivacy
- uBlock Origin defaults (filters, badware, privacy, resource-abuse, unbreak)
- Peter Lowe's ad server list
- Brave-curated MPL-compatible blocklist

**Per-site control:**

Blocking is active on every site by default.
To adjust for a specific site, use the Shield icon in the address bar (coming in a future release).

> **Note (alpha):** The per-site Shield UI toggle is not yet available in dev-0.1.
> Blocking can be toggled globally via the `phlink.adblock.enabled` profile preference.

---

## Privacy-first defaults

phlink sets privacy-protective defaults that stock Chromium does not:

| Feature | phlink default | Chromium default |
|---------|---------------|-----------------|
| Third-party cookies | **Blocked** | Allowed |
| DNS-over-HTTPS | **On (Cloudflare 1.1.1.1)** | Off |
| Network state isolation | **On** | Off |
| Referrer policy | Strict-origin-when-cross-origin | Same |
| Telemetry / crash reports | **Off** | Opt-out |

See [Privacy defaults](privacy.md) for a full list.

---

## Appearance: Light and Dark themes

phlink ships two built-in themes: **Light** and **Dark**.
Both pass WCAG AA contrast requirements.

Switch themes in **phlink://settings/appearance** → **Theme**.
The **System** option follows your OS light/dark preference automatically.

---

## Profile export and import

phlink lets you back up and restore your profile locally.
No cloud sync is involved; everything stays on your device.

**Export:**

1. Navigate to `phlink://portability`.
2. Click **Export profile**.
3. Enter a passphrase (used to encrypt the bundle).
4. Save the `.phlinkprofile` file.

**Import:**

1. Navigate to `phlink://portability`.
2. Click **Import profile**.
3. Choose your `.phlinkprofile` file and enter the passphrase.
4. phlink creates a new profile from the bundle; no existing data is overwritten.

---

## Automatic updates

phlink checks for updates automatically using a TUF-style signed update mechanism.
Updates are verified against Ed25519 signatures before installation.

Manage update settings in **phlink://settings/help**.

> **Note (alpha):** The update server endpoint is configured but the live update infrastructure is not yet operational in dev-0.1.
> Check the [releases page](https://github.com/devparanjay/phlink/releases) for new versions manually in the meantime.

---

## Extension support

phlink supports Chrome extensions installed from the Chrome Web Store.
No Google account is required to install extensions from store URLs.

See [Extension model](../dev/extension-model.md) for developer details.

---

## Default search engine

phlink defaults to **DuckDuckGo**.
The following engines are pre-configured and switchable from **phlink://settings/search**:

- DuckDuckGo (default)
- Brave Search
- Startpage
- Google
- Bing
