"""Pytest fixtures for the network-capture test suite.

The suite intercepts every outbound HTTP/HTTPS request from a phlink
browser process by routing it through a local mitmproxy instance, then
asserts the captured set of contacted hostnames is a subset of
`tests/network-capture/allowlist.txt`.

Architecture
------------
1. `mitm_capture` (session scope): boots an in-process mitmproxy on
   127.0.0.1:<random-port>, installs its CA cert into a throwaway
   directory, and exposes a `Capture` object that streams every request
   it sees into a list.
2. `phlink_browser` (function scope): launches the binary at
   $PHLINK_BINARY (or skips the test if unset) with --proxy-server
   pointing at the mitmproxy port and --user-data-dir pointing at a
   temp profile. The CA cert is whitelisted via
   --ignore-certificate-errors-spki-list so HTTPS interception works
   without modifying the OS trust store.
3. The test sleeps for IDLE_SECONDS (default 60), reads
   `mitm_capture.hosts`, and diffs against the allow-list.

Why mitmproxy and not Playwright's request interceptor?
The Playwright interceptor only sees requests originating from a
Page; it cannot see browser-process traffic (component updater, OCSP,
metrics uploader, A/B-test seed fetch, safe-browsing list pings, OS
keychain pings, etc.). Those are exactly the requests this suite
exists to catch.

Why a transparent system proxy and not a TUN device?
Routing only HTTP(S) through mitmproxy keeps the test runnable on
Linux CI without root privileges. DNS-level leaks are covered by the
DoH-default patch (Phase 4 Wave 2): if Cloudflare DoH is the only DNS
endpoint in use, every plain-DNS query becomes itself a leak signal
caught by the OS resolver path, which we check separately via
mitmproxy's UDP listener (future work — see issue tracker).
"""

from __future__ import annotations

import asyncio
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import closing
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = Path(__file__).resolve().parent / "allowlist.txt"


def _free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _read_allowlist(path: Path) -> set[str]:
    hosts: set[str] = set()
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            hosts.add(line.lower())
    return hosts


@dataclass
class Capture:
    """Live record of every host contacted during a test."""

    hosts: set[str] = field(default_factory=set)
    flows: list[tuple[str, str]] = field(default_factory=list)  # (host, url)

    def reset(self) -> None:
        self.hosts.clear()
        self.flows.clear()


class _RecordAddon:
    """mitmproxy addon that records every request flow into a Capture."""

    def __init__(self, capture: Capture):
        self._capture = capture

    def request(self, flow):  # mitmproxy calls this per request
        try:
            host = flow.request.pretty_host.lower()
        except Exception:
            host = flow.request.host.lower() if flow.request.host else "<unknown>"
        self._capture.hosts.add(host)
        self._capture.flows.append((host, flow.request.pretty_url))


@dataclass
class MitmHandle:
    capture: Capture
    proxy_port: int
    ca_cert: Path


def _start_mitmproxy(capture: Capture, port: int, confdir: Path) -> threading.Thread:
    """Run mitmproxy in a dedicated thread + asyncio loop."""
    from mitmproxy import options as mitm_options
    from mitmproxy.tools.dump import DumpMaster

    ready = threading.Event()
    state: dict[str, object] = {}

    def _run() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        opts = mitm_options.Options(
            listen_host="127.0.0.1",
            listen_port=port,
            confdir=str(confdir),
            ssl_insecure=True,
        )
        master = DumpMaster(opts, with_termlog=False, with_dumper=False)
        master.addons.add(_RecordAddon(capture))
        state["master"] = master
        ready.set()
        try:
            loop.run_until_complete(master.run())
        finally:
            loop.close()

    t = threading.Thread(target=_run, name="mitmproxy", daemon=True)
    t.start()
    if not ready.wait(timeout=10):
        raise RuntimeError("mitmproxy failed to start within 10s")

    # Wait for mitmproxy's CA cert to be materialized on disk.
    ca = confdir / "mitmproxy-ca-cert.pem"
    deadline = time.monotonic() + 10
    while not ca.exists() and time.monotonic() < deadline:
        time.sleep(0.1)
    if not ca.exists():
        raise RuntimeError(f"mitmproxy CA cert not generated at {ca}")

    return t


@pytest.fixture(scope="session")
def mitm_capture():
    """Session-wide mitmproxy + capture object."""
    confdir = Path(tempfile.mkdtemp(prefix="phlink-mitm-"))
    capture = Capture()
    port = _free_port()
    _start_mitmproxy(capture, port, confdir)
    yield MitmHandle(
        capture=capture,
        proxy_port=port,
        ca_cert=confdir / "mitmproxy-ca-cert.pem",
    )
    # confdir intentionally left for post-mortem in CI artifacts.


@pytest.fixture()
def allowlist() -> set[str]:
    return _read_allowlist(ALLOWLIST_PATH)


@pytest.fixture()
def phlink_binary() -> Path:
    """Resolve the phlink binary or skip the test cleanly.

    The binary path is taken from $PHLINK_BINARY. If unset, every test
    that needs it is skipped — this lets the suite live in the repo
    before a build artifact exists, and lets contributors run only the
    parts that don't require a build.
    """
    raw = os.environ.get("PHLINK_BINARY", "").strip()
    if not raw:
        pytest.skip("PHLINK_BINARY not set; skipping browser-launch tests")
    p = Path(raw).expanduser()
    if not p.exists() or not os.access(p, os.X_OK):
        pytest.skip(f"PHLINK_BINARY={raw!r} is not an executable file")
    return p


@pytest.fixture()
def phlink_profile(tmp_path: Path) -> Path:
    profile = tmp_path / "profile"
    profile.mkdir()
    return profile


@dataclass
class PhlinkProcess:
    proc: subprocess.Popen
    profile: Path


@pytest.fixture()
def phlink_process(
    phlink_binary: Path,
    phlink_profile: Path,
    mitm_capture: MitmHandle,
):
    """Launch phlink wired through mitmproxy and yield the process handle."""
    args = [
        str(phlink_binary),
        f"--user-data-dir={phlink_profile}",
        f"--proxy-server=http://127.0.0.1:{mitm_capture.proxy_port}",
        # Avoid a one-time first-run dialog that would block the headless
        # idle window.
        "--no-first-run",
        "--no-default-browser-check",
        # Phlink is built with --ignore-certificate-errors disabled in
        # production; for the capture test we accept mitmproxy's CA via
        # SPKI pinning instead of disabling cert checks wholesale.
        # mitmproxy ships the SPKI of its generated CA in
        # mitmproxy-ca-cert.cer's SPKI; we extract it at runtime.
        f"--ignore-certificate-errors-spki-list={_spki_b64(mitm_capture.ca_cert)}",
        "about:blank",
    ]
    # Capture stderr; on Linux Chromium-derivatives spam noisy GPU lines
    # we don't care about, so route to a file we can attach in CI.
    log_path = phlink_profile / "phlink.stderr.log"
    with log_path.open("wb") as logf:
        proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=logf,
        )
        try:
            yield PhlinkProcess(proc=proc, profile=phlink_profile)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)


def _spki_b64(ca_pem: Path) -> str:
    """Compute the base64 SPKI hash Chromium expects for cert-error bypass."""
    import base64
    import hashlib
    from cryptography import x509
    from cryptography.hazmat.primitives import serialization

    cert = x509.load_pem_x509_certificate(ca_pem.read_bytes())
    spki = cert.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return base64.b64encode(hashlib.sha256(spki).digest()).decode("ascii")


# Helper exposed to tests so they can import without importing pytest.
def hosts_outside_allowlist(seen: Iterable[str], allowed: set[str]) -> list[str]:
    return sorted(h for h in seen if h not in allowed)
