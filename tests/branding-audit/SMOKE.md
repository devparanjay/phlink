# Phase 4.7 Manual Smoke Checklist (BRND-01)

> Run this checklist after every Chromium rebase or whenever `tests/branding-audit/audit.sh` allowlist is touched. Record results in `SMOKE-RESULTS-<YYYY-MM-DD>.md` next to this file. Each item must be **PASS** for the phase verification gate to hold.

## Setup

```bash
open /Volumes/Tools/dev/chromium-src/src/out/Default/phlink.app
```

Use a **clean profile**:

```bash
rm -rf "$HOME/Library/Application Support/phlink"
```

## Items

| # | Surface                    | Where                                     | Expected                                                                 | Result |
|---|----------------------------|-------------------------------------------|--------------------------------------------------------------------------|--------|
| 1 | App menu (macOS menu bar)  | First menu next to Apple                  | Reads "phlink" — no "Chromium", no "Google Chrome"                       |        |
| 2 | About box                  | App menu → About phlink                   | Title "phlink"; version line shows "phlink <version>"                    |        |
| 3 | Window title (default NTP) | New tab window title bar                  | "New Tab" / "phlink" — no "Chromium"                                     |        |
| 4 | Settings landing           | `chrome://settings/`                      | Header reads "Settings"; no banner mentions Chromium / Google Chrome    |        |
| 5 | Version page               | `chrome://version/`                       | First row "phlink <version>"; "Revision" / "OS" rows fine                |        |
| 6 | About-Chromium page        | `chrome://chrome/` redirects to about     | Shows phlink branding only                                               |        |
| 7 | Flags                      | `chrome://flags/`                         | Page header "Experiments" — body may show Chromium internal flag IDs     |        |
| 8 | Help / keyboard shortcuts  | App menu → Help                           | No "Google Chrome Help" / "Chromium Help" link                           |        |
| 9 | Dock icon tooltip          | Hover Dock icon                           | Reads "phlink"                                                           |        |
| 10| Activity Monitor           | Process name                              | "phlink" / "phlink Helper"                                               |        |
| 11| First-run UX               | Fresh profile launch                      | No "Welcome to Chromium" / "Welcome to Google Chrome" string             |        |
| 12| Crash dialog (synthetic)   | Force-quit a tab via Activity Monitor     | "Aw, Snap!" page should reference phlink, not Chromium                   |        |
| 13| Default search engine      | Settings → Search engine                  | DuckDuckGo selected (Phase 3 lock); engine list shows DDG/Brave/Startpage|        |
| 14| Update / sync UI           | Settings → You and phlink                 | No Google sync prompt; no Chromium update banner                         |        |

## How to record results

Copy this file to `SMOKE-RESULTS-<date>.md`, fill the **Result** column with `PASS` / `FAIL: <note>`, and commit alongside any patches applied to fix FAIL rows.

## Known acceptable surfaces (do NOT mark as FAIL)

- `chrome://` URLs themselves (the scheme alias is deferred — see Phase 4.7 CONTEXT D-01).
- `chrome://flags/` flag *names* containing "chromium" (internal flag IDs; not localized).
- DevTools console errors that link to `chromium.googlesource.com` / `issues.chromium.org` (covered by audit allowlist `category: devtools-url`).
- WebGL `GL_RENDERER` reporting "Chromium" (tracked under future fingerprint-hardening phase; allowlisted).
