# Phase 11: Documentation & License Audit - Context

**Gathered:** 2026-04-30
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 11 delivers the documentation set and license-compatibility gate that make phlink releasable as an open-source project.
Three of the five plans are already complete (11-03 `third-party-licenses.md`, 11-04 CI license-check, 11-05 `mcp-workflow.md`).
The two remaining plans are:

- **11-01** — `docs/user/` authoring: install, features, settings, troubleshooting, and privacy pages targeted at end users.
- **11-02** — `docs/dev/` gap-fill: `release-process.md` (ceremony + CI flow, references `scripts/release/`) and `extension-model.md` (stub explaining phlink's no-bundled-extension posture); plus index READMEs for both `docs/user/` and `docs/dev/`; plus a lightweight broken-link CI check.

Phase boundary: documentation and CI quality gates only. No code changes to the browser binary, no new patches to the Chromium patch series.

</domain>

<decisions>
## Implementation Decisions

### User Docs Strategy
- **Practical skeleton** approach: real content for features that exist in the current `dev-0.1` build; explicit `> **Note (alpha):** …` callouts where a feature is deferred or not yet available.
- Cover **all 3 platforms equally** (macOS, Linux, Windows) — consistent with `build.md` / `architecture.md` patterns already established.
- **User-friendly / approachable tone** — these are end-user pages, not developer pages. Short sentences, practical steps, avoid Chromium internals jargon.
- Privacy page: **high-level "what defaults are set"** with links to `docs/dev/PRD.md` for technical depth. No need to reproduce the mechanism explanation.

### Remaining Dev Docs
- `release-process.md`: **Summary + script references** — explain the ceremony and CI flow, reference `scripts/release/keygen.sh` and `scripts/release/sign-release.sh`; do not inline every step.
- `extension-model.md`: **Stub** — document that phlink has no bundled WebExtensions; adblock is a built-in component (not a WebExtension), Chrome Web Store URLs work unchanged; user-installed extensions are supported; phlink-curated discovery list is deferred to Phase 13/14.
- Both `docs/user/` and `docs/dev/` get an **index README.md** — navigable without a docs site, consistent with Chromium convention.
- **Lightweight broken-link CI check** added (non-blocking / warning) using `lychee` or `markdown-link-check`; failure is advisory, not a release blocker at alpha.

### the agent's Discretion
- File naming within `docs/user/` (e.g., `install.md`, `features.md`, `settings.md`, `troubleshooting.md`, `privacy.md`).
- Exact lychee/markdown-link-check invocation in the lint workflow.
- How deeply to cross-link user docs to `docs/dev/` (light cross-links are fine; do not turn user docs into dev docs).

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/dev/architecture.md`, `build.md`, `upstream-tracking.md`, `ci.md`, `installers.md`, `release-keys.md` — full examples of the established doc format.
- `scripts/release/keygen.sh`, `scripts/release/sign-release.sh` — referenced by `release-process.md`.
- `docs/dev/third-party-licenses.md`, `docs/dev/mcp-workflow.md` — already written to the success criteria; no changes needed.
- `scripts/license-audit.py` + `.github/workflows/lint.yml` — CI license check already wired (11-04 done).

### Established Patterns
- Doc header format: `# Title\n\n> blockquote intro\n\n## 1. Section` — used by all existing docs.
- Relative links from `docs/dev/` reference `../../patches/`, `../../scripts/`, `../../.planning/ROADMAP.md`.
- One sentence per line in longer prose blocks (Chromium convention, per copilot-instructions §7).
- 80-col soft wrap.
- Tables for comparative/tabular content; code blocks for commands.

### Integration Points
- `docs/user/README.md` and `docs/dev/README.md` — new index files.
- `.github/workflows/lint.yml` — extend with broken-link check step.
- `docs/dev/` — add `release-process.md` and `extension-model.md`.
- `docs/user/` — create directory and add 5 pages + README.

</code_context>

<specifics>
## Specific Ideas

- User install page should call out the `codesign --force --deep --sign -` workaround needed on macOS for dev builds from `out/Default/` (mentioned in multiple phase verifications).
- User features page should briefly cover: adblock (Shield), appearance (Light/Dark themes), privacy defaults, profile export/import, and the update mechanism.
- User troubleshooting page: cover the most likely alpha pain points (build from source, codesign, missing filter lists after clean profile).
- Privacy page: list the specific defaults: DoH Cloudflare 1.1.1.1, third-party cookies blocked, network state isolation, referrer hardening, telemetry-free. Link to `docs/dev/PRD.md §2` for the threat model.

</specifics>

<deferred>
## Deferred Ideas

- Full docs site (Docusaurus, MkDocs, etc.) — deferred post-alpha. Markdown files in-repo are sufficient for alpha.
- `extension-model.md` full content — deferred until Phase 13/14 when the curated extension list and WebStore URL install path are implemented.
- Automated screenshot generation for user docs — deferred until stable UI.

</deferred>
