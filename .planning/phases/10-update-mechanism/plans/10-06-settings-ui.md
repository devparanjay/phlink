# Plan 10-06 — chrome://settings/help update UI

**Phase**: 10  ·  **Plan**: 10-06  ·  **Atomic patch slot**: 0129
**Depends on**: 10-02 (and 10-03 / 10-04 / 10-05 to provide the relaunch action)

## Outcome

`chrome://settings/help` (and the `phlink://settings/help` alias) shows one
of the following states:

- **Up to date** — "phlink is up to date (v{version})."
- **Checking…** — spinner.
- **Update available — relaunch to apply** — primary button triggers the
  helper-mediated swap.
- **Update failed: {reason}** — surfaces the last failure with a "Retry" link.
- **Auto-updates disabled (managed by your system package manager)** — for
  Linux `.deb` / `.rpm` mode (D-07).
- **Auto-updates disabled (unsigned build)** — when running an ad-hoc-signed
  dev build.

A toggle "Automatically download phlink updates" binds to the
`phlink.updates.auto_check_enabled` pref.

## Key steps

1. Add a new `UpdateStatusHandler` mojo interface
   (`//chrome/browser/ui/webui/help/`-adjacent under phlink namespace) that
   exposes `GetState() => UpdateState`, `CheckNow()`, `RelaunchToApply()`,
   `SetAutoCheckEnabled(bool)`.
2. Wire into `AboutHandler` / Settings WebUI via the existing extension
   points (no fork of `about_settings`).
3. i18n strings for all states (English-only for v1.0; localization is its
   own backlog item).
4. Unit + WebUI integration tests:
   `UpdateStatusHandlerTest.{ReportsUpToDate, ReportsAvailable, RelaunchTriggersHelper}`.
