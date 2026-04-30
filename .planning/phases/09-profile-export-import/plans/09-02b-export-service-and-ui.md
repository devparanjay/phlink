# Plan 09-02b — Export flow (service + Settings WebUI)

**Phase**: 9
**Plan**: 09-02b (follow-up to 09-02)
**Atomic patch slot**: 0121
**Depends on**: 09-01 (patch 0118), 09-02 (patch 0119)

## Outcome

User can navigate to `chrome://settings/portability` (and the
`phlink://settings/portability` alias from Phase 8.6), click **Export**,
enter a passphrase twice, pick a save location, and receive a
`.phlinkbundle` file built by `BundleWriter` (already landed in patch
0119).

## Context

Plan 09-02 originally bundled three things: the codec, the worker
service, and the Settings UI. Patch 0119 landed only the codec — the
security-critical, format-defining piece — so the on-disk layout from
[docs/dev/profile-bundle-format.md](../../../../docs/dev/profile-bundle-format.md)
is locked before any UI surface starts depending on it. This sub-plan
finishes the rest.

## Steps

1. **Service** — `chrome/browser/phlink/portability/export_service.{h,cc}`:
   - Runs on `base::ThreadPool` with `TaskTraits{USER_VISIBLE, MayBlock}`.
   - WAL-checkpoints the live `History` and `Web Data` sqlite DBs into a
     scratch dir before reading (avoid grabbing the live file).
   - Walks the include-list from CONTEXT D-04, feeds bytes into
     `BundleWriter::AddFile`, then `WriteToFile` to a user-chosen path.
   - Reports progress via mojo back to the WebUI (percent + step name).
2. **Mojo** — `chrome/browser/phlink/portability/portability.mojom`:
   - `interface Exporter { Export(string passphrase, mojo_base.mojom.FilePath path) => (ExportStatus status); ObserveProgress(pending_remote<ProgressObserver> observer); }`
   - `interface ProgressObserver { OnProgress(uint32 percent, string step_name); }`
3. **Settings WebUI** —
   `chrome/browser/resources/settings/portability_section/`:
   - `portability_section.ts` — Lit element registered under
     `chrome://settings/portability`.
   - Two-card layout from CONTEXT D-06.
   - Export card: passphrase + confirm fields, "Show what's included"
     expander listing D-04, **Save** button → file picker → mojo call.
   - Progress bar bound to the `ProgressObserver` stream.
4. **Routing** — register `chrome://settings/portability` in
   `chrome/browser/ui/webui/settings/settings_localized_strings_provider.cc`
   and the relevant settings route table.
5. **Patch slot 0121** — single atomic patch.

## Verification

- Manual: launch phlink, export a profile, confirm the produced file is
  parseable by `BundleReader` (see 09-03 unit tests as the spec).
- Network capture: zero outbound HTTP during export
  ([tests/network-capture/](../../../../tests/network-capture/)).
- Branding audit: extend `runtime-audit.py` with `/portability` surfaces
  on both `chrome://` and `phlink://`.

## Out of scope

- Differential / scheduled exports.
- Password / cookie inclusion (deferred to v1.1).
