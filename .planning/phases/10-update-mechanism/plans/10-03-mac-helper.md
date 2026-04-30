# Plan 10-03 — macOS update helper + atomic .app swap

**Phase**: 10  ·  **Plan**: 10-03  ·  **Atomic patch slot**: 0126
**Depends on**: 10-02 (patch 0125)
**Blocks**: 10-06 (UI relaunch button)

## Outcome

A separately-signed `phlink_update_helper` binary inside
`phlink.app/Contents/Helpers/` that, when invoked at the next launch by
`phlink.app/Contents/MacOS/phlink`, atomically swaps the running `.app` for
the staged version and re-execs phlink. Failure rolls back to the previous
bundle.

## Key steps

1. New GN `executable("phlink_update_helper")` target under
   `//chrome/browser/phlink/updater/mac/`. Codesigned with the same
   Developer-ID identity (sealed inside the app bundle).
2. Protocol:
   - phlink launches → checks `Updates/staged.json` → if a newer verified
     version exists, fork+exec `phlink_update_helper --apply
     {staged_dir} {target_app_path}` and exit.
   - Helper extracts the staged `.zip`, verifies the embedded codesign
     signature (`SecCodeCheckValidity`), moves the current `.app` to
     `Updates/{prev_version}/phlink.app`, `renameat` swaps in the new bundle,
     re-execs phlink.
   - On any failure, rolls back the `renameat` and writes a structured
     entry to `update.log`.
3. Unsigned/ad-hoc dev builds: helper detects ad-hoc signature on the
   running phlink and **refuses to swap**. (D-08 fallback rule.)
4. Tests: `phlink_update_helper_unittests` — argument parsing, signature
   verification mocked, rollback path. Plus a manual end-to-end: stage a
   fake `phlink.app` carrying a different `CFBundleVersion`, observe swap.

## Out of scope

Linux (10-04), Windows (10-05), differential updates, channel switching.
