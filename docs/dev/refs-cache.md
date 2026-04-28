# `.refs/` — Upstream Documentation Cache

> Per [PRD §8.4](PRD.md), phlink keeps a structured, queryable cache of upstream documentation for every adopted technology, language, and OSS library. This file documents that cache.

## Why this exists

- **Offline reference** — phlink developers can grep upstream docs without network access.
- **Deterministic AI context** — agents (`playwright`, `stitch-mcp`, future custom MCPs) can read a known snapshot rather than re-fetching arbitrary web pages.
- **Provenance** — every snapshot records its source URL, fetch date, version, and license.

## Layout

```
.refs/
  <ecosystem>/
    <name>@<version>/
      source.<ext>            # the actual fetched docs / archive
      MANIFEST.json           # required, schema-validated metadata
      [extracted/]            # optional — extracted contents if archive
```

Examples:

```
.refs/chromium/chromium@128.0.6613.84/
.refs/rust/adblock-rust@0.8.0/
.refs/python/jsonschema@4.21.0/
```

## `MANIFEST.json`

Each entry has a `MANIFEST.json` validated against [`../../scripts/refs/MANIFEST.schema.json`](../../scripts/refs/MANIFEST.schema.json).

Required fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Project name |
| `version` | string | Version or git ref |
| `ecosystem` | string | `chromium`, `rust`, `python`, `js`, `docs`, … |
| `source_url` | URI | Where it was fetched from |
| `fetch_date` | ISO 8601 UTC | When it was fetched |
| `license` | string | SPDX identifier preferred |

Optional: `sha256_of_archive`, `notes`, `files`, `size_bytes`.

## Adding a snapshot

Use the helper:

```bash
bash scripts/refs-fetch.sh \
  --name adblock-rust \
  --version 0.8.0 \
  --ecosystem rust \
  --url https://github.com/brave/adblock-rust/archive/refs/tags/v0.8.0.tar.gz \
  --license MPL-2.0 \
  --notes "Brave's Rust adblock engine — phlink's primary blocking engine (Phase 5)."
```

Run `bash scripts/refs-fetch.sh --help` for full usage.

## Git status

`.refs/` is **gitignored**. These are *upstream* docs, not phlink's own source. They describe phlink's dependencies; tracking them would balloon the repo without value (and would likely create license/redistribution headaches). Treat the cache as a local development convenience.

The schema and fetch helper, on the other hand, are tracked.
