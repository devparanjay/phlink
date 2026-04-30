# Plan 10-05 — Windows updater path (MoveFileEx swap)

**Phase**: 10  ·  **Plan**: 10-05  ·  **Atomic patch slot**: 0128
**Depends on**: 10-02

## Outcome

On Windows, after `UpdaterService` stages a payload, `phlink_update_helper.exe`
runs at next launch and replaces the install via
`MoveFileEx(MOVEFILE_REPLACE_EXISTING|MOVEFILE_DELAY_UNTIL_REBOOT)` if the
binary is locked, else immediate `MoveFileEx`. Authenticode signature on
the new payload is verified via `WinVerifyTrust` before any swap.

## Key steps

1. New `phlink_update_helper.exe` GN executable target under
   `//chrome/browser/phlink/updater/win/`.
2. Authenticode verification with `WinVerifyTrust` + EV cert pinning to the
   phlink publisher subject (D-08).
3. Atomic swap with `MoveFileEx` + UAC awareness (per-user installs use
   `%LOCALAPPDATA%`, no UAC prompt).
4. Unit tests: signature-pinning rejects mismatched subject; swap-locked
   path uses `MOVEFILE_DELAY_UNTIL_REBOOT`.

## Open

`.msi` is for first install only (handled in 10-07). The updater never
invokes msiexec.
