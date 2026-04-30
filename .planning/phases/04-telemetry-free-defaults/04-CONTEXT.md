# Phase 4 — Telemetry-Free Defaults — CONTEXT

> Sourced from upstream Chromium source under `/Volumes/Tools/dev/chromium-src/src/` (metrics services manager client, variations service, secure DNS config) and PRD §3 (locked privacy posture) and §10.1 (locked product decisions).

## Phase Goal (from ROADMAP)

A clean profile launch produces zero outbound telemetry requests; DoH is enabled by default with Cloudflare 1.1.1.1; Quad9 and NextDNS are preconfigured; user can pick or enter custom.

## Requirements covered

`TELM-01`, `TELM-02`, `TELM-03`, `TELM-04`.

## Decisions

### D-01 — Defense in depth at three layers

phlink locks down telemetry at three independent layers so no single upstream rebase can silently re-enable phone-home:

1. **GN args** — disable opt-in at compile time wherever Chromium exposes a flag (`enable_reporting`, etc.).
2. **Source patches** — flip the `MetricsServicesManagerClient::IsMetricsReportingEnabled()` answer to a hard `false`, and short-circuit the variations seed fetch and the crash reporter uploader so even if the pref is somehow flipped on (corruption, tampering), no request leaves the box.
3. **Network-capture test** — a Playwright + mitmproxy fixture launches a clean profile and asserts zero outbound requests in the first 60 seconds.

If any one layer is missed by an upstream change, the other two still hold the line.

### D-02 — UMA / metrics: hard-off, no opt-in path in v1

Chromium's metrics pipeline is gated by `MetricsServicesManagerClient::IsMetricsReportingEnabled()` (chrome/browser/metrics/chrome_metrics_services_manager_client.cc). Even with `is_chrome_branded=false`, the consent pref still exists; we patch the client to return `false` unconditionally and remove the toggle from `chrome://settings`. PRD §3.5 forbids any opt-in UI in v1.

### D-03 — Crash reporter: disabled by default, no opt-in

`enable_reporting=false` (GN) plus a patch to `chrome/app/chrome_crash_reporter_client.cc` to make `GetCollectStatsConsent()` return `false`. We do **not** rip out Crashpad — local minidumps in `<profile>/Crashpad/` are useful for self-debugging — we only block the uploader. The "Send crash reports" UI is removed.

### D-04 — Variations seed fetch: disabled

`VariationsService` fetches `https://clientservices.googleapis.com/chrome-variations/seed`. Even with no UMA, a fresh Chromium contacts that URL on first run to receive A/B-test configuration. We:

- Set `disable_fieldtrial_testing_config=true` (already pinned in Phase 3) so the test seed is not baked in.
- Patch `VariationsService::CreateLowEntropyProvider`-adjacent code to no-op the seed fetch.
- Override the variations URL to the empty string (defense in depth — invalid URLs short-circuit the fetcher).

### D-05 — Network-time, safety-tips, optimization-guide, omnibox-suggest: all blocked

Chromium has a long tail of services that "phone home" on first idle:

- `network::NetworkTimeTracker` → `clients2.google.com/time/`
- `safe_browsing::SafeBrowsingDatabaseManager` → covered by `safe_browsing_mode=0` (Phase 3).
- `optimization_guide::OptimizationGuideService` → `optimizationguide-pa.googleapis.com`
- `OmniboxSuggestProvider` → `clients1.google.com/complete/search` (the default suggest URL is set per search engine; DDG default fixes this for the user-visible flow, but we also disable the network suggest for the no-engine-yet startup window).
- `chrome://feedback` upload endpoint
- Component updater (`update.googleapis.com`) — see D-06.

We disable each by default and add them to the network-capture allow-list-violation set.

### D-06 — Component updater: stays on, but pointed at our own update endpoint

Component updater pulls non-code data (CRL sets, certificate revocation, origin trial tokens, hyphenation, etc.). We can't ship without it. PRD §10.1 specifies TUF-style signed updates (Phase 10). For Phase 4:

- Keep component updater enabled.
- Patch the default update URL constants to phlink's updater endpoint (placeholder constant `PHLINK_COMPONENT_UPDATE_URL` resolved in Phase 10).
- Until Phase 10 lands the real endpoint, this URL points at `https://updates.phlink.invalid/` so any leak fails fast and visibly rather than reaching Google.

### D-07 — DoH default: Cloudflare 1.1.1.1, automatic mode

Per PRD §10.1: Cloudflare 1.1.1.1 (no-log) default; Quad9 and NextDNS preconfigured; custom resolver supported.

Chromium's DoH config lives in:
- `net/dns/public/doh_provider_entry.{h,cc}` — built-in provider list.
- `chrome/browser/net/secure_dns_config.cc` — config + persistence.
- `chrome/browser/net/stub_resolver_config_reader.cc` — startup wiring.

phlink ships a patch that:
- Sets `kDnsOverHttpsMode` default to `secure` (was `automatic`).
- Sets `kDnsOverHttpsTemplates` default to Cloudflare's template (`https://cloudflare-dns.com/dns-query`).
- Adds Quad9 and NextDNS to the `DohProviderEntry` list with `display_globally=true` so they appear in the picker on first launch on any locale.

The picker UI in `chrome://settings/security` already supports "Custom DNS provider" — no patch needed there.

### D-08 — Test fixture: Playwright + mitmproxy, clean profile, 60-second window

Plan 04-03 stands up a fixture that:
- Launches phlink with `--user-data-dir=<tmp>` (clean profile) under mitmproxy.
- Idles for 60 seconds.
- Asserts the captured request set is empty (or is exactly the allow-list of `cloudflare-dns.com` for DoH bootstrap).
- Runs in CI on Linux (mac/Windows added once the build finishes there).

Playwright's `chromium.launch({ executablePath })` accepts an arbitrary Chromium binary, so the fixture works against the phlink build artifact directly — no DevTools-protocol surgery needed.

### D-09 — Patch slot ranges

Phase 4 slot ranges (root subtree):

- `0050-0059` — UMA / metrics gate patches
- `0060-0064` — Crash reporter
- `0065-0069` — Variations / field trials
- `0070-0079` — Optimization Guide / Network Time / Suggest / Feedback / Component Updater URLs
- `0080-0089` — DoH defaults

Sub-tree slot ranges allocated as needed.

## Hard rules pulled in from PRD §3

- **No outbound telemetry** (TELM-01, TELM-02). Hard rule. Rejecting any change that adds one.
- **No opt-in path for telemetry in v1** (TELM-02). Locked.
- **DoH on by default** (TELM-03, TELM-04). Locked.

## Out of scope

- DoH picker UI redesign — picker already exists; we only seed the provider list.
- Removing Crashpad entirely — keeps local diagnostics, only the uploader is blocked.
- Replacing the component updater with TUF — that's Phase 10.
- A user-visible "advanced privacy settings" panel — that's Phase 6.
