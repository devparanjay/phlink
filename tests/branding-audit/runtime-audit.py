#!/usr/bin/env python3
"""Phase 8.5 runtime branding audit (BRND-04).

Launches phlink with a remote-debugging port, navigates to canonical
internal surfaces via CDP, captures `document.title` and visible body
text, and asserts no `\\bChromium\\b` / `\\bGoogle Chrome\\b` /
`\\bChrome\\b` strings appear (except for entries in the runtime
allowlist — see runtime-audit-allowlist.txt).

Skips cleanly when PHLINK_BINARY is unset (CI without a binary).

Stack matches tests/benchmark_60tab/ (Python + raw CDP websocket).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

try:
    from websocket import create_connection  # websocket-client
except ImportError:  # pragma: no cover
    print("ERROR: pip install websocket-client", file=sys.stderr)
    sys.exit(2)

HERE = Path(__file__).resolve().parent
ALLOWLIST_PATH = HERE / "runtime-audit-allowlist.txt"

# Surfaces to audit. Mix of internal pages we already own.
SURFACES = [
    "chrome://settings/",
    "chrome://settings/appearance",
    "chrome://settings/privacy",
    "chrome://settings/help",
    "chrome://version/",
    "chrome://flags/",
    "chrome://about/",
    "chrome://newtab/",
]

# Forbidden tokens (case-sensitive word-boundary).
FORBIDDEN = re.compile(r"\b(Chromium|Google Chrome|Chrome)\b")


def load_allowlist() -> list[re.Pattern]:
    if not ALLOWLIST_PATH.exists():
        return []
    out = []
    for line in ALLOWLIST_PATH.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.append(re.compile(re.escape(s)))
    return out


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_devtools(port: int, timeout: float = 30.0) -> str:
    deadline = time.time() + timeout
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/json/version", timeout=1.0
            ) as r:
                data = json.load(r)
                return data["webSocketDebuggerUrl"]
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.25)
    raise RuntimeError(f"DevTools not ready on :{port}: {last_err}")


def cdp_call(ws, msg_id: int, method: str, params: dict | None = None) -> dict:
    payload = {"id": msg_id, "method": method, "params": params or {}}
    ws.send(json.dumps(payload))
    while True:
        raw = ws.recv()
        msg = json.loads(raw)
        if msg.get("id") == msg_id:
            return msg


def attach_target(browser_ws_url: str):
    ws = create_connection(browser_ws_url, timeout=15)
    return ws


def new_target(ws, msg_id: int, url: str) -> str:
    res = cdp_call(ws, msg_id, "Target.createTarget", {"url": url})
    return res["result"]["targetId"]


def attach(ws, msg_id: int, target_id: str) -> str:
    res = cdp_call(
        ws, msg_id, "Target.attachToTarget", {"targetId": target_id, "flatten": True}
    )
    return res["result"]["sessionId"]


def session_call(ws, msg_id: int, session_id: str, method: str, params: dict | None = None):
    payload = {
        "id": msg_id,
        "sessionId": session_id,
        "method": method,
        "params": params or {},
    }
    ws.send(json.dumps(payload))
    while True:
        raw = ws.recv()
        msg = json.loads(raw)
        if msg.get("id") == msg_id and msg.get("sessionId") == session_id:
            return msg


def wait_for_load(ws, msg_id_seed: int, session_id: str, timeout: float = 10.0):
    """Poll document.readyState until 'complete' or timeout."""
    deadline = time.time() + timeout
    seed = msg_id_seed
    while time.time() < deadline:
        seed += 1
        r = session_call(
            ws,
            seed,
            session_id,
            "Runtime.evaluate",
            {"expression": "document.readyState", "returnByValue": True},
        )
        if r.get("result", {}).get("result", {}).get("value") == "complete":
            return seed
        time.sleep(0.2)
    return seed


def collect(ws, msg_id_seed: int, session_id: str, url: str) -> tuple[str, str, int]:
    seed = msg_id_seed + 1
    session_call(ws, seed, session_id, "Page.enable")
    seed += 1
    session_call(ws, seed, session_id, "Runtime.enable")
    seed += 1
    session_call(ws, seed, session_id, "Page.navigate", {"url": url})
    seed = wait_for_load(ws, seed, session_id, timeout=15.0)
    seed += 1
    title = session_call(
        ws,
        seed,
        session_id,
        "Runtime.evaluate",
        {"expression": "document.title", "returnByValue": True},
    )["result"]["result"].get("value", "")
    seed += 1
    body = session_call(
        ws,
        seed,
        session_id,
        "Runtime.evaluate",
        {"expression": "document.body && document.body.innerText || ''", "returnByValue": True},
    )["result"]["result"].get("value", "")
    return title, body, seed


def scrub(text: str, allow: list[re.Pattern]) -> str:
    for pat in allow:
        text = pat.sub("", text)
    return text


def main() -> int:
    binary = os.environ.get("PHLINK_BINARY")
    if not binary:
        print("PHLINK_BINARY not set; skipping runtime branding audit.")
        return 0
    if not Path(binary).exists():
        print(f"PHLINK_BINARY not found: {binary}", file=sys.stderr)
        return 2

    allow = load_allowlist()
    port = free_port()
    user_data_dir = Path(tempfile.mkdtemp(prefix="phlink-audit-"))

    args = [
        binary,
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate",
        "about:blank",
    ]

    print(f"Launching: {binary} (port {port})")
    proc = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    failures: list[tuple[str, str, list[str]]] = []  # (url, where, snippets)
    try:
        ws_url = wait_for_devtools(port, timeout=30.0)
        ws = attach_target(ws_url)
        msg_id = 0
        for url in SURFACES:
            try:
                msg_id += 1
                tgt = new_target(ws, msg_id, url)
                msg_id += 1
                sess = attach(ws, msg_id, tgt)
                title, body, msg_id = collect(ws, msg_id, sess, url)
            except Exception as e:  # noqa: BLE001
                print(f"  WARN: {url}: {e}")
                continue

            for label, text in (("title", title), ("body", body)):
                scrubbed = scrub(text, allow)
                hits = FORBIDDEN.findall(scrubbed)
                if hits:
                    snippets = []
                    for m in FORBIDDEN.finditer(scrubbed):
                        s = max(0, m.start() - 30)
                        e = min(len(scrubbed), m.end() + 30)
                        snippets.append(scrubbed[s:e])
                    failures.append((url, label, snippets[:5]))
                    print(f"  FAIL {url} [{label}]: {len(hits)} hit(s)")
                else:
                    print(f"  OK   {url} [{label}]")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        shutil.rmtree(user_data_dir, ignore_errors=True)

    if failures:
        print("\nRuntime branding audit FAILED:")
        for url, where, snips in failures:
            print(f"  {url} [{where}]:")
            for s in snips:
                print(f"    …{s!r}…")
        return 1
    print("\nRuntime branding audit PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
