# Contributing to phlink

Thanks for your interest in phlink — an open-source, privacy-first, performance-first Chromium-based browser. This document covers how to set up a dev environment, the contribution workflow, and what reviewers will look for.

## TL;DR

1. Read [docs/dev/PRD.md](docs/dev/PRD.md) §10.1 — the **locked product decisions**. PRs that conflict with these will be closed unless they include a justification for re-litigating the decision.
2. Read [docs/dev/build.md](docs/dev/build.md) to set up a working build.
3. Read [docs/dev/upstream-tracking.md](docs/dev/upstream-tracking.md) before authoring a Chromium patch.
4. Open an issue first for anything bigger than a typo / one-file fix.
5. Follow the PR template; CI must pass.

## Getting set up

```bash
git clone https://github.com/devparanjay/phlink.git
cd phlink
bash scripts/bootstrap.sh   # macOS / Linux
# or:
pwsh scripts/bootstrap.ps1  # Windows
```

Building Chromium is a long process — see [docs/dev/build.md](docs/dev/build.md). For most contributions (docs, scripts, build config, CI), you don't need to actually compile.

## Linting (run before opening a PR)

CI runs lint on macOS, Linux, and Windows. To run the same checks locally:

```bash
# Python
pip install ruff
ruff check scripts

# Shell (macOS/Linux)
brew install shellcheck   # or: apt install shellcheck
shellcheck scripts/*.sh

# PowerShell (Windows)
Install-Module PSScriptAnalyzer -Scope CurrentUser
Invoke-ScriptAnalyzer -Path scripts -Recurse

# Markdown
npm install -g markdownlint-cli2
markdownlint-cli2 "**/*.md"
```

## Branching & commits

- Feature branches: `feature/<short-slug>` or `fix/<short-slug>`.
- Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages: `feat(adblock): integrate adblock-rust at network layer`.
- Reference issues in the body: `Refs #N` or `Fixes #N`.
- Keep commits focused. A reviewer-friendly PR has 1–10 commits, each independently reviewable.

## What reviewers check

Every PR is reviewed against this list (it mirrors `.github/PULL_REQUEST_TEMPLATE.md`):

- [ ] Lint passes locally and in CI.
- [ ] No new outbound telemetry, analytics, or "phone home" code.
- [ ] No new Google services / Sync / Cast / Widevine code paths enabled by default.
- [ ] No proprietary blob added.
- [ ] No third-party cookie or storage default loosened.
- [ ] Documentation updated (`docs/dev/` for contributor changes; `docs/user/` for user-visible changes).
- [ ] If adding a Chromium patch, it's also exported via `scripts/refresh-patches.py` and committed under `patches/`.
- [ ] Conventional Commit subject + body explains *why* the change is needed.

## What we will NOT accept

- Feature additions that conflict with `docs/dev/PRD.md` §10.1 locked decisions, without an accompanying ADR-style proposal.
- Code that introduces telemetry, even opt-in (we'll revisit this in v2 only).
- Changes that weaken site isolation, sandboxing, or the renderer/browser process boundary in the name of performance.

## Reporting security issues

Please don't open a public issue for security vulnerabilities. Email the maintainer (see profile). We'll triage within 72 hours.

## License

By contributing, you agree your work is licensed under the same terms as the rest of phlink (see [LICENSE](LICENSE)).
