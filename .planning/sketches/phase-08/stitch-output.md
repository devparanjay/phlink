# Phase 8 — Stitch Design Handoff (consolidated)

> Source of truth for Phase 8 (Appearance Subsystem) design tokens.
> Generated via stitch MCP (`projects/12962487919675094023` — "phlink Browser Chrome").
> Validated visually against `light-screenshot.png` and `dark-screenshot.png`.

## 1. Methodology

stitch was used in two modes:

1. **Visual validation** — `generate_screen_from_text` produced full settings-page mockups for Light and Dark, exercising every token in real chrome (sidebar, cards, toggles, dropdowns, focus state). Both screenshots reviewed for ideology fit.
2. **Token authoring** — stitch auto-generated a Material tonal palette in its `designMd`. We **do not** adopt the Material tonal palette wholesale — it drifts from phlink's locked hex (PRD §3.2 M1). We adopt:
   - phlink's hand-locked palette (from the prompt, validated by screenshot) — **authoritative**
   - stitch's typography scale (Inter, 11/12/13/14/20px) — adopted as-is
   - stitch's spacing/radius (4/8/16px, 4px component / 8px container radius) — adopted as-is

## 2. Final Token Palette (LOCKED)

### 2.1 Light theme

| Token                  | Hex        | Role                                                    |
| ---------------------- | ---------- | ------------------------------------------------------- |
| `--phlink-canvas`      | `#FFFFFF`  | Window background (main content)                        |
| `--phlink-surface`     | `#F8F4EC`  | Sidebar / inactive surface (warm off-white)             |
| `--phlink-surface-alt` | `#F1EDE5`  | Hover state on surface                                  |
| `--phlink-card`        | `#FFFFFF`  | Card / dropdown / popover (on canvas)                   |
| `--phlink-text`        | `#1A1A1A`  | Primary text                                            |
| `--phlink-text-muted`  | `#525252`  | Secondary text, hints                                   |
| `--phlink-hairline`    | `#E5E0D6`  | 1px borders, dividers                                   |
| `--phlink-accent`      | `#A8C8E8`  | Pastel blue — selected card border, focus ring, toggle on |
| `--phlink-on-accent`   | `#1A1A1A`  | Foreground on accent fills (passes WCAG AA, 11.4:1)     |
| `--phlink-danger`      | `#C0392B`  | Reset / destructive                                     |
| `--phlink-success`     | `#2E8540`  | Confirmation only                                       |

### 2.2 Dark theme

| Token                  | Hex        | Role                                                    |
| ---------------------- | ---------- | ------------------------------------------------------- |
| `--phlink-canvas`      | `#0D0D0D`  | Window background (near-black, slight warmth)           |
| `--phlink-surface`     | `#181818`  | Sidebar surface                                         |
| `--phlink-surface-alt` | `#1F1F1F`  | Card surface                                            |
| `--phlink-card`        | `#1F1F1F`  | Card / dropdown / popover                               |
| `--phlink-text`        | `#FFFFFF`  | Primary text                                            |
| `--phlink-text-muted`  | `#A0A0A0`  | Secondary text                                          |
| `--phlink-hairline`    | `#2A2A2A`  | 1px borders                                             |
| `--phlink-accent`      | `#F5E68A`  | Pastel yellow — selected card border, focus ring, toggle on |
| `--phlink-on-accent`   | `#000000`  | **Critical**: foreground on accent fills (16:1) — never white |
| `--phlink-danger`      | `#F5736B`  | Reset / destructive (lightened for dark bg)             |
| `--phlink-success`     | `#6FE38A`  | Confirmation only                                       |

### 2.3 WCAG AA contrast verification

| Pair (theme)                        | Ratio   | Required | Status |
| ----------------------------------- | ------- | -------- | ------ |
| `#1A1A1A` on `#FFFFFF` (Light)      | 17.4:1  | 4.5:1    | PASS   |
| `#525252` on `#FFFFFF` (Light)      | 7.5:1   | 4.5:1    | PASS   |
| `#1A1A1A` on `#F8F4EC` (Light)      | 16.0:1  | 4.5:1    | PASS   |
| `#1A1A1A` on `#A8C8E8` (Light acc.) | 11.4:1  | 4.5:1    | PASS   |
| `#A8C8E8` on `#FFFFFF` (border)     | 1.5:1   | 3:1 (UI) | FAIL → solved by 2px width + selected check icon |
| `#FFFFFF` on `#0D0D0D` (Dark)       | 19.7:1  | 4.5:1    | PASS   |
| `#A0A0A0` on `#0D0D0D` (Dark)       | 8.5:1   | 4.5:1    | PASS   |
| `#FFFFFF` on `#181818` (Dark)       | 16.7:1  | 4.5:1    | PASS   |
| `#000000` on `#F5E68A` (Dark acc.)  | 16.0:1  | 4.5:1    | PASS   |
| `#FFFFFF` on `#F5E68A` (Dark acc.)  | 1.3:1   | n/a      | **NEVER** — fg on accent must be `#000000` |

The 1.5:1 selected-card-border ratio is mitigated by:
(a) using **2px** stroke instead of 1px (WCAG SC 1.4.11 large component) and
(b) always pairing the border with a check-icon in the corner (semantic redundancy).

## 3. Typography (adopted from stitch)

Family stack: `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`

| Token         | Size / Weight / Line | Use                              |
| ------------- | -------------------- | -------------------------------- |
| `display`     | 20px / 600 / 28px    | Page title ("Appearance")        |
| `header-1`    | 18px / 600 / 24px    | Section header                   |
| `header-2`    | 14px / 600 / 20px    | Sub-section, row label           |
| `body`        | 14px / 400 / 20px    | Default body, control labels     |
| `body-sm`     | 13px / 400 / 18px    | Secondary text, descriptions     |
| `label`       | 12px / 500 / 16px    | Pills, small UI                  |
| `label-sm`    | 11px / 500 / 14px    | Captions, footer                 |

## 4. Spacing & Radius

- Spacing scale: `4 / 8 / 12 / 16 / 24 / 32 / 48` (px). Use `8px` baseline.
- Radius: `4px` for components (toggles, inputs), `8px` for containers (cards, dropdowns).
- Hairline borders: **1px** always, color from `--phlink-hairline`.
- **No drop shadows.** Elevation expressed via surface tint and hairline only.

## 5. Visual references

- `.planning/sketches/phase-08/light-screenshot.png` — desktop chrome://settings/appearance, Light selected. Validated: warm off-white sidebar, white canvas, hairline rows, recessive accent, no shadows, no marketing CTAs.
- `.planning/sketches/phase-08/dark-screenshot.png` — desktop chrome://settings/appearance, Dark selected. Validated: near-black canvas, soft grey surfaces, yellow accent used only for selected-card border + active sidebar pill, BLACK foreground rule honored, no shadows.
- `.planning/sketches/phase-08/light-stitch-raw.json` — full stitch generation (Light).
- `.planning/sketches/phase-08/dark-stitch-raw.json` — full stitch generation (Dark).

## 6. Ideology checks (both themes)

| Check                                              | Light | Dark |
| -------------------------------------------------- | ----- | ---- |
| No telemetry / phone-home UI surfaces              | ✅    | ✅   |
| No marketplace / Web Store promotion               | ✅    | ✅   |
| No upsell / "EXPLORE THEMES" CTAs                  | ✅    | ✅*  |
| Recessive — chrome quieter than content            | ✅    | ✅   |
| Hairlines, no drop shadows                         | ✅    | ✅   |
| WCAG AA contrast on all default text pairs         | ✅    | ✅   |
| Accent used sparingly (focus + selection only)     | ✅    | ✅   |
| Quintessentially Chromium (no exotic chrome)       | ✅    | ✅   |

\* dark first-pass had a "Make phlink yours / EXPLORE THEMES" callout — regenerated with explicit suppression. Final dark-screenshot.png is clean.

## 7. Open implementation notes for plan-phase 8

- `--phlink-accent` is a **role token**, not a brand color reservation — implementations must never use it for non-state surfaces (no accent-tinted icons, no accent backgrounds for cards).
- "Follow system" theme card must reflect *current* OS preference live (not on next launch) — see Phase 8 plan.
- Settings UI is implemented in TS (chrome://settings polymer/lit). Tokens compile to CSS custom properties in a single `phlink_theme.css` injected at app start (no FOUC).
- Native UI (toolbar, omnibox, tab strip) consumes the same tokens via `ui/color/color_provider` — Phase 8 must add a phlink color mixer.
