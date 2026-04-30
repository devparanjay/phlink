# Phase 4 — Telemetry-Free Defaults — PLAN

**Phase goal:** A clean profile launch produces zero outbound telemetry requests; DoH is enabled by default with Cloudflare 1.1.1.1; Quad9 and NextDNS preconfigured.

**Hard prerequisite:** Phase 3 closed (services GN args pinned, branding patches applied). All Phase 4 patches assume the GN baseline from `build/gn-args/common.gni` and the patch tooling from Phase 1/3.

## Plans

### 04-01 — Disable UMA, metrics, crash reporter, Field Trials phone-home, variations seed fetch

**Goal:** `chrome://settings` exposes no metrics-reporting toggle; the metrics service short-circuits before constructing any uploader; the variations service never fetches a seed; the crash reporter never uploads.

**GN arg additions** (`build/gn-args/common.gni`):

```gn
# No UMA upload pipeline compiled in. The histograms machinery still
# builds — components rely on RecordHistogram macros — but the uploader
# is dead.
enable_reporting = false

# No "report a problem" feedback uploader bundled.
enable_feedback_service = false
```

**Files patched** (under `../chromium-src/src/`):

- `chrome/browser/metrics/chrome_metrics_services_manager_client.cc` — `IsMetricsReportingEnabled()` and `IsMetricsReportingForceEnabled()` return `false` unconditionally; `GetMetricsStateManager()` short-circuits log construction.
- `chrome/browser/metrics/chrome_metrics_service_client.cc` — `RegisterPrefs` defaults `metrics::prefs::kMetricsReportingEnabled` to `false` and marks the pref non-user-modifiable.
- `chrome/app/chrome_crash_reporter_client.cc` — `GetCollectStatsConsent()` returns `false`; `GetCrashServerURL()` returns the empty string.
- `components/variations/service/variations_service.cc` — short-circuit `FetchVariationsSeed()` to a no-op; `GetVariationsServerURL()` returns an empty `GURL`.
- `chrome/browser/ui/webui/settings/privacy_review_handler.cc` and `privacy_sandbox_handler.cc` — remove the metrics-reporting and "improve search and browsing" toggles from the settings UI surface (gate behind a `BUILDFLAG(PHLINK_NO_TELEMETRY)`-style check; this also kills any UI string lookups).

**Patches**: `0050-no-metrics-reporting.patch`, `0051-metrics-pref-default-off.patch`, `0060-no-crash-upload.patch`, `0065-no-variations-fetch.patch`, `0066-empty-variations-url.patch`, `0052-hide-metrics-toggle.patch`.

**Verification:**

1. `gn gen` + `autoninja chrome` succeeds.
2. Launched binary's `chrome://settings/privacy` does not contain a metrics-reporting toggle.
3. `out/Default/chrome --user-data-dir=$(mktemp -d)` produces zero requests to `clientservices.googleapis.com`, `clients2.google.com`, `clients4.google.com`.

**Wave:** 1 (foundational; 04-02 and 04-03 depend on this).

---

### 04-02 — DoH defaults: Cloudflare default, Quad9 + NextDNS preconfigured, picker UI

**Goal:** Fresh profile boots with DoH "secure" mode using Cloudflare; the resolver picker on `chrome://settings/security` shows Cloudflare, Quad9, NextDNS as preset options globally, plus the "custom" entry.

**GN arg additions:** none (all wiring is source-side).

**Files patched** (under `../chromium-src/src/`):

- `net/dns/public/doh_provider_entry.cc` — extend `DohProviderEntry::GetList()` so Quad9 (`https://dns.quad9.net/dns-query`) and NextDNS (`https://dns.nextdns.io`) are present with `display_globally=true`. Cloudflare already exists; flip its `display_globally` to true if regional.
- `chrome/browser/net/secure_dns_config.cc` and/or `stub_resolver_config_reader.cc` — change the *startup default* of `SecureDnsConfig::Mode` from `kAutomatic` to `kSecure`, and set the default templates to Cloudflare's URI when the pref is unset on first run.
- `chrome/browser/net/dns_probe_runner.cc` — only if needed; some platforms require an explicit fallback config.
- `components/country_codes/country_codes.cc` (read-only check; do not patch) — confirm the new providers are not gated by country.

**Patches**: `0080-doh-add-quad9-nextdns.patch`, `0081-doh-default-secure-cloudflare.patch`, `0082-doh-providers-display-globally.patch`.

**Verification:**

1. `chrome://settings/security` → "Use secure DNS" is **on** by default; the dropdown shows Cloudflare (selected), Quad9, NextDNS, plus "Custom".
2. `dig` against the running browser's loopback DoH probe (or `chrome://net-internals/#dns`) confirms requests are going through `cloudflare-dns.com`.
3. Disabling DoH returns to the system resolver (no regression in the "off" path).

**Wave:** 2 (after 04-01 lands so the metrics pref doesn't leak DoH lookup events).

---

### 04-03 — Network-capture test fixture: zero outbound on clean-profile launch

**Goal:** A reproducible Playwright + mitmproxy fixture in `tests/network-capture/` runs in CI on Linux (and locally on mac), boots phlink with a clean profile, idles 60 seconds, and asserts no requests left the box outside an explicit allow-list (DoH bootstrap + component updater).

**New files (this repo):**

- `tests/network-capture/conftest.py` — Pytest fixture that:
  - spawns `mitmdump --listen-port 0 --set block_global=false --quiet -w $TMPDIR/flow.mitm` and parses the chosen port from its stderr.
  - launches phlink via `playwright.chromium.launch({ executablePath, args: ['--proxy-server=127.0.0.1:<port>', '--user-data-dir=$TMPDIR/profile', '--ignore-certificate-errors-spki-list=<mitm_spki>'] })`.
  - on teardown, parses the captured flow file (using `mitmproxy.io.FlowReader`) and exposes the request list as the test return value.
- `tests/network-capture/test_clean_profile.py` — single test:
  - launches the fixture.
  - sleeps 60 seconds.
  - asserts every captured request matches the allow-list regex set: `r"^https://(cloudflare-dns\.com|updates\.phlink\.invalid)/"`.
  - prints the violating requests on failure.
- `tests/network-capture/requirements.txt` — `playwright>=1.45`, `mitmproxy>=11`, `pytest>=8`.
- `.github/workflows/network-capture.yml` — Linux-only job: installs deps, downloads the latest phlink artifact from the CI-build workflow (or builds locally for Phase 4 — gated behind a workflow_dispatch input until Phase 7 makes builds cheap), runs the test, uploads the captured flow on failure.

**Verification:**

1. Local: `pytest tests/network-capture/` is green against an unmodified Chromium build (sanity-check the fixture itself reports plenty of leaks) and against the phlink build (zero leaks).
2. CI: workflow green on Linux. macOS/Windows added in Phase 7 once we have build artifacts there.
3. Failure output: when the test fails, the captured `.mitm` file is uploaded as a CI artifact for triage.

**Wave:** 3 (after 04-01 + 04-02 land, since the assertion will fail otherwise).

---

## Wave plan

| Wave | Plans                | Why                                                       |
|------|----------------------|-----------------------------------------------------------|
| 1    | 04-01                | Foundational; 04-02 and 04-03 both depend on its patches. |
| 2    | 04-02                | DoH defaults, builds on the metrics-free baseline.        |
| 3    | 04-03                | Verification fixture; meaningless until 1 + 2 land.       |

## Patch slot ranges (root subtree)

| Range       | Plan  | Topic                                       |
|-------------|-------|---------------------------------------------|
| 0050–0059   | 04-01 | UMA / metrics                               |
| 0060–0064   | 04-01 | Crash reporter                              |
| 0065–0069   | 04-01 | Variations / field trials                   |
| 0070–0079   | 04-01 | Optimization Guide / Suggest / Feedback / Component Updater (subset; rest deferred to 04-01.b if scope explodes) |
| 0080–0089   | 04-02 | DoH defaults                                |
