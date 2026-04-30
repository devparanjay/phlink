# Settings Guide

> Key settings in phlink and how to find them.

All settings are at `phlink://settings` (or `chrome://settings`).

---

## Appearance

**Path:** `phlink://settings/appearance`

| Setting | What it does |
|---------|-------------|
| Theme | Switch between Light, Dark, and System (follows OS). |
| Font size | Adjusts the default page font size. |
| Page zoom | Sets the default zoom level for all pages. |

---

## Privacy & Security

**Path:** `phlink://settings/privacy`

| Setting | phlink default | Notes |
|---------|---------------|-------|
| Third-party cookies | Blocked | Adjustable per-site via Site Settings. |
| DNS-over-HTTPS | On — Cloudflare 1.1.1.1 | Change provider under **Security → Use secure DNS**. |
| Safe Browsing | Standard | Downloads are scanned locally; no Google reporting. |
| Send "Do Not Track" | Off | DNT is largely ignored by sites; phlink's built-in blocking is more effective. |

---

## Search engine

**Path:** `phlink://settings/search`

Change the default search engine or manage the pre-loaded list.

---

## Passwords

**Path:** `phlink://settings/passwords`

The built-in password manager stores credentials locally, encrypted via your OS keychain (Keychain on macOS, libsecret on Linux, DPAPI on Windows).
No cloud sync.

---

## Adblock

> **Note (alpha):** A dedicated adblock settings page is planned for a future release.
> Current adblock settings are managed via profile preferences.

The adblock engine is on by default.
To disable it for all sites (not recommended), set the `phlink.adblock.enabled` preference to `false` in your profile's `Preferences` JSON file.

---

## Profiles and portability

**Path:** `phlink://portability`

Export or import your profile as an encrypted local bundle.
See [Features → Profile export and import](features.md#profile-export-and-import).

---

## Updates

**Path:** `phlink://settings/help`

Shows the installed version and update status.
Use **Check for updates** to trigger a manual check.
Toggle **Automatically check for updates** to control background update checks.

---

## Flags (advanced)

**Path:** `phlink://flags`

Experimental feature flags inherited from Chromium.
Use with caution; flags may be removed or change behaviour across versions.
