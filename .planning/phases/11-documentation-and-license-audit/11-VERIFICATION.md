# Phase 11 Verification

## Goal achieved

Phase 11: Documentation & License Audit — all planned deliverables are present and committed.

## Checklist

### Plan 11-01: docs/user/

- [x] `docs/user/install.md` — macOS (Gatekeeper codesign workaround), Linux (AppImage/deb/rpm), Windows (SmartScreen note)
- [x] `docs/user/features.md` — adblock, privacy defaults, themes, profile portability, updates, extensions, search
- [x] `docs/user/settings.md` — appearance, privacy/security, search, passwords, adblock, portability, updates, flags
- [x] `docs/user/troubleshooting.md` — codesign, SmartScreen, FUSE, adblock not blocking, DoH, crash-on-launch
- [x] `docs/user/privacy.md` — cookies, tracking, DNS, referrer, telemetry, Google services, passwords/sync, isolation
- [x] `docs/user/README.md` — index with table linking all 5 docs

### Plan 11-02: docs/dev/ gaps + CI

- [x] `docs/dev/release-process.md` — keygen ceremony, build (all platforms), package (dmg/AppImage/deb/rpm/msi), sign, publish, post-release checklist
- [x] `docs/dev/extension-model.md` — built-in vs WebExtension distinction, CWS support, MV3 posture
- [x] `docs/dev/README.md` — index of all 13 dev docs in categorised table
- [x] `.github/workflows/lint.yml` — `lychee --offline` broken-link step added (`continue-on-error: true`)

### Plans 11-03 through 11-05 (pre-existing, confirmed complete)

- [x] 11-03: License audit pass
- [x] 11-04: CONTRIBUTING.md and governance docs
- [x] 11-05: Third-party license inventory

## Commit

`dcecc08` — "phase 11: documentation and license audit"

## Decisions confirmed

All decisions from `11-CONTEXT.md` were honoured:
- User docs written at practical/user-friendly level (not raw Chromium internals).
- `extension-model.md` is a stub explaining why there are no bundled WebExtensions.
- Both `docs/user/README.md` and `docs/dev/README.md` created as index files.
- Broken-link check is non-blocking (`continue-on-error: true`, lychee offline mode).
