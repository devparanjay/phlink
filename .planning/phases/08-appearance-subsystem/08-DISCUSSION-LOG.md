# Phase 8 — Appearance Subsystem (DISCUSSION-LOG)

> Audit log for `/gsd-discuss-phase 8 --auto`. Human-reference only; downstream agents (researcher, planner, executor) read `08-CONTEXT.md`, not this file.

## Mode

`--auto`. Agent auto-selected all gray areas and picked recommended options without `AskUserQuestion`. No interactive turns.

## User invocation

> "Follow instructions in #prompt:SKILL.md with these arguments: 8 --auto (Also use the available MCP server called stitch. It's called stitch and not stitch-mcp.)"

## Notable runtime fact

The user requested use of the `stitch` MCP server. Workspace inspection found **no MCP configuration for stitch** (no `.vscode/mcp.json`, no `claude_desktop_config.json`, no prior stitch artifacts under `.planning/sketches/`). Agent surfaced this in `CONTEXT.md` D-08 and explicitly **blocked plans 08-01b..05 on stitch availability**, then proceeded with the rest of the discuss-phase workflow (which is documentation, not implementation).

## Areas auto-selected

All four. No areas skipped.

| # | Area | Auto-pick | Recommended-option rationale |
| - | ---- | --------- | ---------------------------- |
| 1 | Token namespace | `kColorPhlink*` | Grep-able, mechanical to audit, matches Brave's `kColorBrave*` precedent. |
| 2 | Mixer registration order | After `AddNativeChromeColorMixer`, before `key.custom_theme` | phlink brand identity overrides platform vibrancy but defers to user-installed community themes. Established by `phase-08-scoping.md` §2.1. |
| 3 | Pref shape | Single int `prefs::kPhlinkAppearanceMode {0,1,2}` | Robust to roaming, easy to migrate, matches Chromium `kBrowserColorScheme` shape. |
| 4 | WCAG-AA gate | Two-layer (gtest + lint-time Python mirror) | Belt-and-braces: chromium build CI not yet wired (per `docs/dev/ci.md`). Lint mirror keeps gate green on every PR. |

## Decisions captured (one-liner index → see CONTEXT.md §6 for full rationale)

- **D-01** Token namespace `kColorPhlink*`.
- **D-02** Mixer slots after Native, before custom_theme.
- **D-03** Reuse upstream `ColorProviderKey::ColorMode`.
- **D-04** Pref `kPhlinkAppearanceMode` int `{0=Light, 1=Dark, 2=Follow System}`.
- **D-05** Settings WebUI: dedicated phlink subsection in `appearance_page`.
- **D-06** Default = Follow System.
- **D-07** WCAG-AA enforced via gtest + `scripts/contrast-audit.py` in lint workflow.
- **D-08** Token hex values **NOT locked** — gated on stitch MCP wiring. 08-01b blocked.
- **D-09** Patch slot range `0110`–`0119`.
- **D-10** Centralized `PhlinkAppearanceModeObserver` in `chrome/browser/themes/`.
- **D-11** No hot-path theme code.
- **D-12** Test pyramid: gtests for color/mixer/observer, Playwright E2E for settings flow.

## Deferred ideas (captured to §7 of CONTEXT.md)

- Per-tab accent tint → v1.1.
- Custom user CSS → out forever.
- Time-of-day auto-dark → out forever.
- Theme marketplace → depends on Phase 14, deferred.
- Theme-switch animation → out (frame budget).
- macOS vibrancy override → defer to upstream.

## Risks logged

1. stitch MCP not wired up — blocks all real Phase 8 implementation.
2. Linux gtk-theme precedence — likely deferred to v1.0.
3. Translucent surface fallback on Windows without compositor blur.
4. WCAG large-text vs non-text classification needs a small DSL (08-05).

## Agent's discretion items (the things I picked without asking)

Per the standing user mandate "make small decisions yourself; report what + why":

| Item | Pick | Why |
| ---- | ---- | --- |
| Pref name spelling | `kPhlinkAppearanceMode` (not `kPhlinkTheme`, not `kPhlinkColorScheme`) | "Appearance" matches the macOS / Settings page naming users see; "Theme" overloaded with community-themes; "ColorScheme" collides with Chromium's `kBrowserColorScheme` and is confusing. |
| Default value = Follow System (2), not Light (0) | Modern OS-app default; user opt-out is one click. |
| Patches 0110+, not 0103+ | Reserve `0103`–`0109` for late additions in earlier phases (Phase 6/7). Cleaner ranges per phase. |
| Two-layer WCAG gate (lint + gtest) | Chromium build CI is not yet wired; lint must catch theme regressions on every PR. |
| Placeholder hex values in D-08 | Explicitly marked as "must be replaced by stitch output". Lets 08-01b plan reference *something* concrete; prevents silent acceptance of agent-picked brand colors. |
| Settings WebUI = single subsection in existing `appearance_page` | Smallest possible footprint; doesn't fight upstream. |
| Test layer for observer = unit gtest with fake NativeTheme + PrefService | Standard Chromium test pattern; avoids browser_test cost for a small observer. |
| Playwright (not browser_test) for the settings E2E | Per `docs/dev/mcp-workflow.md` §1, Playwright is the preferred tool for browser-level integration tests. |

## Outcome

`08-CONTEXT.md` written. Phase 8 implementation remains **gated on stitch MCP availability**. Until then, only `08-01a` (the scoping doc, already shipped at commit `16454f1`) is in tree.

## Next step

Per `--auto` chain rules, this would normally chain to `/gsd-plan-phase 8`. **Agent recommends NOT chaining**: planning hex-color-driven plans against placeholder hex values would be wasteful work. Recommended next user action:

1. Wire up the `stitch` MCP server (configure in `.vscode/mcp.json` or equivalent).
2. Run an interactive stitch session to author the Light + Dark palettes against the PRD §3.2 M1 names.
3. Save output to `.planning/sketches/phase-08/stitch-output.md`.
4. Re-run `/gsd-plan-phase 8` — it will now have concrete tokens and can produce executable plans.

If the user prefers the agent to proceed with placeholder hex anyway (and accept rework when stitch lands), say so explicitly and the agent will chain to plan-phase.
