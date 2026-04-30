# Privacy Defaults

> phlink's out-of-the-box privacy configuration and what each setting does.

phlink is private by default.
The settings below are active on a clean install with no user configuration required.

---

## Tracking and cookies

| Feature | Default | Notes |
|---------|---------|-------|
| Third-party cookies | **Blocked** | Sites that depend on cross-site cookies will surface a "cookies blocked" icon. Adjustable per-site in Site Settings. |
| Network state isolation | **On** | Cache, HTTP/2 connections, and HSTS state are partitioned by top-level site, preventing cross-site tracking via network state. |
| Tracking query parameter stripping | **On** | Known tracking parameters (e.g., `utm_*`, `fbclid`, `gclid`) are stripped from URLs before navigation. |

---

## Ad and tracker blocking

The built-in adblock engine blocks network-level ad and tracker requests.
Default filter lists: EasyList, EasyPrivacy, uBlock Origin defaults, Peter Lowe's list, Brave's MPL-compatible list.

See [Features → Ad and tracker blocking](features.md#ad-and-tracker-blocking-shield).

---

## DNS

| Feature | Default | Notes |
|---------|---------|-------|
| DNS-over-HTTPS | **On — Cloudflare 1.1.1.1 (no-log policy)** | Prevents DNS queries from being observed in plaintext. Change provider in `phlink://settings/security`. |
| Fallback to system DNS | Off | DoH failures surface as DNS errors rather than falling back to plaintext. |

Preconfigured DoH providers: Cloudflare 1.1.1.1 (default), Quad9, NextDNS.

---

## Referrer policy

Outbound referrer headers are trimmed to **origin only** on cross-origin navigations.
Full referrer paths are never sent to third parties.

---

## Telemetry and crash reports

phlink sends **no telemetry or crash reports** of any kind.
Chromium's metrics, Safe Browsing reporting, and crash-upload pipelines are hard-disabled at the patch level:

- `0003-phlink-hard-disable-metrics-reporting-and-consent.patch`
- `0004-phlink-hard-disable-crash-report-uploads.patch`

There is no opt-in telemetry in phlink v1 and no plan to add any.

---

## Google services

The following Google-originated features are **disabled by default** and cannot be enabled by a user preference (they require a source-level change to re-enable):

- Google account / GAIA sign-in
- Chrome Sync / Chrome Sync server
- Safe Browsing (v4 URL upload)
- Cast receiver
- Google Network Time (NTS)
- One Google Bar (New Tab Page fetch)
- GCM / FCM device registration

---

## Passwords and sync

Passwords are stored locally, encrypted via the OS keychain.
There is no cloud sync in phlink v1.
See [Features → Profile export and import](features.md#profile-export-and-import) for the local encrypted backup option.

---

## Site isolation

Site isolation remains **on at all times**.
Weakening the renderer/browser process boundary for performance is explicitly excluded from phlink's roadmap.
