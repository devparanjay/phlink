# 10-01a — SUMMARY

**Patch slot**: 0124 (chromium-src commit on `phlink-wip`; phlink commit `bc519f7` on `dev-0.1`).

## Shipped

- `docs/dev/update-protocol.md` (333-line patch). Locks the on-the-wire
  TUF subset, role schema, verification staircase, threat model, key
  rotation cadence, privacy posture, and failure logging.

## Pivot vs. original 10-01 plan

CONTEXT D-01 was rewritten from "vendor Rust `tuf` crate via gnrt" to
"in-tree C++ TUF client backed by `crypto::SignatureVerifier` (Ed25519,
boringssl) + `base::JSONReader` + `network::SimpleURLLoader`".

Reason: the Rust `tuf` crate transitively pulls `hyper` (would duplicate
Chromium's network stack) and `ring` (conflicts with Phase 9 D-01
boringssl-only crypto policy). ~600 LOC of in-tree C++ is cheaper than
carrying that conflict.

## Deferred to 10-01b (next atomic patch slot 0125)

- `//chrome/browser/phlink/updater:metadata` GN target.
- `metadata_client.{h,cc}` — `class TufClient` C++ surface.
- `dev_root.json` keypair + `phlink_updater_dev_root` build flag.
- `phlink_updater_unittests` with the four named tests.

## Verification

- chromium-src `git format-patch -1` → 333 lines, applied cleanly.
- phlink-side `git push origin dev-0.1` clean.
- No build/codesign required (docs-only patch).
