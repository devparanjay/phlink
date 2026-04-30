# Phase 11: Documentation & License Audit — Plan Index

**Status:** 11-03, 11-04, 11-05 complete. Two remaining plans below.

| Plan | File | Goal | Tasks | Effort |
|------|------|------|-------|--------|
| 11-01 | [11-01-PLAN.md](11-01-PLAN.md) | Author `docs/user/` — install, features, settings, troubleshooting, privacy, index | 6 | medium |
| 11-02 | [11-02-PLAN.md](11-02-PLAN.md) | Fill `docs/dev/` gaps + broken-link CI check | 4 | low |

---

## Already complete (do not re-plan)

| Plan | Deliverable | Status |
|------|-------------|--------|
| 11-03 | `docs/dev/third-party-licenses.md` | ✅ Done |
| 11-04 | `.github/workflows/lint.yml` license-audit.py step | ✅ Done |
| 11-05 | `docs/dev/mcp-workflow.md` | ✅ Done |

---

## Execution order

Plans 11-01 and 11-02 are independent — they touch different files and can be executed in either order or in parallel.

Suggested order: **11-02 first** (shorter, establishes `docs/dev/README.md` that 11-01 cross-links to), then **11-01**.
