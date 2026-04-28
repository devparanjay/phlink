"""Phase 4 Wave 3 — fresh-profile leak test.

Boots a fresh phlink profile through mitmproxy, lets it sit on
about:blank for IDLE_SECONDS, and asserts that the set of contacted
hostnames is a subset of `allowlist.txt`.

This is the network-layer enforcement of phlink's "no telemetry,
no phone-home" promise (PRD §3.5). The patch-layer enforcement lives
in patches/0003..0005 (UMA, crash uploader, variations seed) and the
build-layer enforcement lives in build/gn-args/common.gni
(enable_reporting=false, enable_feedback_service=false). All three
layers must independently fail any future attempt to add a leak.
"""

from __future__ import annotations

import os
import time

import pytest

from conftest import hosts_outside_allowlist  # type: ignore[import-not-found]


# 60s is the floor: it covers the typical Chromium "first 30s after
# startup" burst (component updater, OCSP, NTP background fetch, GCM
# registration, etc.). Override via $PHLINK_NETCAP_IDLE_SECONDS for
# longer soak runs in nightly CI.
IDLE_SECONDS = float(os.environ.get("PHLINK_NETCAP_IDLE_SECONDS", "60"))


def test_clean_profile_makes_no_outbound_requests(
    phlink_process,
    mitm_capture,
    allowlist,
):
    """A fresh phlink profile must not contact any host off the allow-list."""
    capture = mitm_capture.capture
    capture.reset()

    # Let the browser settle. Any outbound request the browser process
    # itself fires (component updater poll, OCSP, GCM registration,
    # variations seed, UMA upload, safebrowsing list refresh, …) will
    # land in capture.hosts during this window.
    deadline = time.monotonic() + IDLE_SECONDS
    while time.monotonic() < deadline:
        if phlink_process.proc.poll() is not None:
            pytest.fail(
                f"phlink exited prematurely with code {phlink_process.proc.returncode}; "
                f"see {phlink_process.profile / 'phlink.stderr.log'}"
            )
        time.sleep(0.5)

    leaks = hosts_outside_allowlist(capture.hosts, allowlist)
    assert not leaks, (
        "phlink contacted hosts that are not on the allow-list:\n  "
        + "\n  ".join(leaks)
        + "\n\nFull request log (host -> url):\n  "
        + "\n  ".join(f"{h} -> {u}" for h, u in capture.flows[:50])
        + ("\n  …(truncated)" if len(capture.flows) > 50 else "")
    )
