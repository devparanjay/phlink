# MCP Workflow

> Source of truth for which Model Context Protocol (MCP) servers are authorized for phlink development, what each is used for, and the rules for adding new ones. This doc satisfies success criterion §11.4 of [.planning/ROADMAP.md](../../.planning/ROADMAP.md) ("`docs/dev/mcp-workflow.md` documents the authorized MCPs"). It is the canonical reference cited from [.github/copilot-instructions.md §10](../../.github/copilot-instructions.md) and [PRD.md §6.3](PRD.md).

## 1. Authorized MCP servers

| Server | Purpose | Used during | Notes |
| --- | --- | --- | --- |
| `playwright` | Browser-level integration testing of phlink builds (UI flows, content blocking observable behavior, settings pages). | Tests authoring (Phase 5+, full coverage Phase 12). | Preferred over hand-rolled DevTools Protocol clients **except** when the test must observe browser-process traffic — the 60-tab benchmark harness ([tests/benchmark_60tab/](../../tests/benchmark_60tab/)) deliberately uses pytest + raw CDP for that reason. |
| `stitch-mcp` | UI/UX design, design-system tokens, logo and brand asset generation. | Phase 8 (Appearance Subsystem) token authoring, Phase 11 doc illustrations, ad-hoc settings-page work. | **Hard rule:** design tokens (color, typography, spacing) for shipped UI surfaces are authored via `stitch-mcp`, not hand-rolled. See [phase-08-scoping.md](phase-08-scoping.md) §1. |
| `git` | Non-trivial git operations (interactive rebase plans, complex conflict resolution explanations, commit-message synthesis from staged diffs). | Any phase. | Plain `git` CLI is fine for routine `add`/`commit`/`push`. Reach for the MCP only when the operation is awkward to express in shell. |

## 2. Posture

- **MCP outputs are reviewed, not rubber-stamped.** Anything an MCP produces that lands in the tree (tokens, generated tests, doc snippets, brand assets) must be reviewed in the PR like any other contribution.
- **No MCP may exfiltrate source.** MCPs that ship code or context to third-party LLM endpoints are subject to the same telemetry posture as the browser itself ([copilot-instructions.md §3](../../.github/copilot-instructions.md) — no telemetry, no phone-home). If an MCP requires uploading proprietary user data to a vendor service, it is **not** authorized for use against this repository.
- **MCPs do not bypass safety checks.** They run inside the same operational-safety envelope as a human contributor: no `--no-verify`, no force-pushes to shared branches, no destructive shortcuts.

## 3. Adding a new MCP

A new MCP becomes "authorized" only after **all** of the following:

1. A short proposal lands in this file (new row in §1) explaining: name, what it does, why existing tools are insufficient, where its outputs end up, and license / privacy posture of the server itself.
2. The MCP is wired into the developer's local environment (e.g., `~/.config/Claude/claude_desktop_config.json` or the equivalent for the editor in use). **Per-developer**; this repo intentionally does not ship MCP credentials or server URLs.
3. The first PR using the new MCP labels itself with the MCP's row in §1 in the PR description, so reviewers know to check its outputs.

If a hypothetical MCP fails any of these, fall back to manual work or a different authorized MCP.

## 4. What MCPs are explicitly **not** for

- **Generating production C++ that touches `//chrome/` or `//content/` core paths** — those changes go through ordinary review against the patch set in [patches/](../../patches/) and Chromium style. MCPs may suggest skeletons; humans land them.
- **Authoring filter lists, DoH provider URLs, or signing keys** — these are locked decisions ([PRD.md §10.1](PRD.md)) and live in tracked source files. No MCP may rewrite them in a PR.
- **Fabricating Chromium APIs.** If an MCP suggests a `base::` type, `mojom` interface, or GN target that an agent cannot find in [.refs/chromium/chromium@main/](../../.refs/chromium/chromium@main/) or the live Chromium tree, treat the suggestion as wrong and verify before using.

## 5. References

- [.github/copilot-instructions.md §10](../../.github/copilot-instructions.md) — short-form rules embedded in the agent prompt.
- [PRD.md §6.3](PRD.md) — product requirement that MCPs be documented before use.
- [phase-08-scoping.md](phase-08-scoping.md) — concrete example of stitch-mcp gating a phase.
