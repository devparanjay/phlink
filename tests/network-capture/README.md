# Network-capture suite

This suite is the **third defense layer** in phlink's no-phone-home
posture (Phase 4, Wave 3). It launches a built phlink binary against a
fresh profile, routes every HTTP/HTTPS request through a local
mitmproxy, and fails the test if any contacted hostname is not on
`allowlist.txt`.

The other two layers:

| Layer  | Where                                            | What it kills                                      |
| ------ | ------------------------------------------------ | -------------------------------------------------- |
| Build  | `build/gn-args/common.gni`                       | Compiles out the metrics / feedback / SB pipelines |
| Source | `patches/0003`-`patches/0006`                    | Hard-disables consent, crash upload, seed fetch    |
| **Network** | **`tests/network-capture/`** (this suite) | **Fails CI if anything still escapes**            |

## Running locally

```sh
# 1. Create a venv and install deps.
cd tests/network-capture
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# cryptography is pulled in by mitmproxy already; if not:
pip install cryptography

# 2. Point at a built phlink binary (any chromium-derivative will work
#    for smoke-testing the harness itself).
export PHLINK_BINARY=/path/to/your/phlink

# 3. Run.
pytest -v
```

If `$PHLINK_BINARY` is unset, the suite skips cleanly. This is the
expected state in the repo until Phase 5/6 produces the first build
artifact.

## Adding to the allow-list

Don't, unless you can't help it. If you must:

1. Add the bare hostname to `allowlist.txt`, one per line.
2. Add a comment block above it justifying why it can't be eliminated.
3. File a follow-up issue tagged `phlink-leak` to track removal.
4. Never use wildcards.

## CI

The GitHub workflow `.github/workflows/network-capture.yml` runs this
suite on every PR. Until a phlink build is wired up, the workflow runs
the harness against itself (i.e. proves the fixture starts and stops
cleanly) but skips the actual launch step.
