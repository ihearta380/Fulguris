"""Precise timing probe: type at various delays AFTER entering edit mode.

The bug: the URL is only selectAll()'d inside a 400ms delayed guard. Until then
the cursor sits at the END with NO selection, so a real keystroke INSERTS into
the URL instead of replacing it. This probe sends the edit key with wait=0 and
sleeps a controlled delay before typing, so it actually tests the pre-400ms window.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import keys  # noqa: E402
from tests import appdevice  # noqa: E402
from autotest.android import adb  # noqa: E402

URL = "example.com"


def nav_focus(dev):
    adb.key(dev.serial, keys.SEARCH, wait=0.7)


def start_edit_now(dev):
    """Enter edit mode and return immediately (no settle wait)."""
    adb.key(dev.serial, keys.DPAD_CENTER, wait=0.0)


def defocus(dev):
    adb.key(dev.serial, keys.DPAD_DOWN, wait=0.4)
    deadline = time.time() + 6
    while dev.field_focused() and time.time() < deadline:
        time.sleep(0.3)


def probe(dev, delay_ms: int) -> bool:
    nav_focus(dev)
    start_edit_now(dev)
    time.sleep(delay_ms / 1000.0)
    adb.type_text(dev.serial, "X", wait=0.0)
    after = dev.field_text()
    replaced = after.strip().lower() == "x"
    print("  delay=%4dms  after=%r  %s" % (delay_ms, after[:40],
          "SELECTED(replaced)" if replaced else "NOT SELECTED(appended)"))
    defocus(dev)
    return replaced


def main() -> None:
    serial = sys.argv[1] if len(sys.argv) > 1 else "R58R91GBTZK"
    dev = appdevice.FulgurisDevice(serial)
    dev.navigate(URL)
    print("label: %r" % dev.field_text())
    for d in (0, 100, 200, 300, 350, 400, 450, 600):
        probe(dev, d)


if __name__ == "__main__":
    main()
