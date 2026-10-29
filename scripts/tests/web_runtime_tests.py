"""WebView JavaScript, first-party cookie and origin storage regression checks."""
from __future__ import annotations

import atexit
import os
import re
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
PORT = 8906
_server: ThreadingHTTPServer | None = None
_reverse_devices = {}


class _NoCacheHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ASSETS_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, *args):
        pass


def _ensure_server(device) -> None:
    global _server
    if _server is None:
        _server = ThreadingHTTPServer(("127.0.0.1", PORT), _NoCacheHandler)
        threading.Thread(target=_server.serve_forever, daemon=True).start()
        atexit.register(_server.shutdown)
    if device.id not in _reverse_devices:
        device.reverse(PORT)
        _reverse_devices[device.id] = device
        atexit.register(lambda d=device: d.reverse_remove(PORT))


def _wait_for_field(device, expected: str, timeout: float = 25.0) -> str:
    deadline = time.time() + timeout
    value = device.field_text()
    while time.time() < deadline:
        if expected in value:
            return value
        time.sleep(0.5)
        value = device.field_text()
    return value


def test_javascript_cookie_and_storage_across_tabs(device, ctx: dict) -> None:
    """JS executes and same-origin cookie/localStorage survive a new browser tab."""
    _ensure_server(device)
    device.navigate(f"http://localhost:{PORT}/web_runtime.html?reset={time.time_ns()}")
    first = _wait_for_field(device, "runtime-js-cookie-storage-1")
    assert "runtime-js-cookie-storage-1" in first, (
        "inline JavaScript, cookie access or initial localStorage write failed "
        f"(toolbar field: {first!r})"
    )

    device.navigate(f"http://localhost:{PORT}/web_runtime.html?second={time.time_ns()}")
    second = _wait_for_field(device, "runtime-js-cookie-storage-2")
    assert "runtime-js-cookie-storage-2" in second, (
        "same-origin cookie/localStorage did not persist into the second tab "
        f"(toolbar field: {second!r})"
    )

    device.restart()
    restored = _wait_for_field(device, "runtime-js-cookie-storage-", timeout=20.0)
    match = re.search(r"runtime-js-cookie-storage-(\d+)", restored)
    assert match and int(match.group(1)) >= 2, (
        "the active WebView page was not restored after a cold app restart "
        f"(toolbar field: {restored!r})"
    )


FEATURE_GROUPS = {"web-runtime": [test_javascript_cookie_and_storage_across_tabs]}
ALL_TESTS = FEATURE_GROUPS["web-runtime"]
TEST_DESCRIPTIONS = {
    "test_javascript_cookie_and_storage_across_tabs":
        "JavaScript, first-party cookies and localStorage persist across tabs"
}
