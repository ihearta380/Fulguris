#!/usr/bin/env python3
"""Tap-based selection stress: tap the field to enter edit, type immediately, check
whether the URL was fully selected (replaced) or not (appended). Loops to expose the
intermittent 'sometimes not selected' bug on the TOUCH path."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import keys
from tests import appdevice

SER = sys.argv[1] if len(sys.argv) > 1 else None
CYCLES = int(sys.argv[2]) if len(sys.argv) > 2 else 20

device = appdevice.FulgurisDevice(SER)
device.restart()
device.navigate("example.com", reset=False)
time.sleep(1.5)
label = device.field_text()
print("label:", repr(label))
# Make sure we actually landed on a real page (label differs from the URL).
if not label or "example" in label.lower() or label.lower().startswith("http"):
    # retry once from a clean restart
    device.restart()
    device.navigate("example.com", reset=False)
    time.sleep(1.5)
    label = device.field_text()
    print("label (retry):", repr(label))


def webview():
    return (360, 800)


bad = 0
for i in range(CYCLES):
    # leave edit / defocus field: tap webview
    wx, wy = webview()
    device.tap(wx, wy, wait=0.5)
    time.sleep(0.25)
    # tap the field to (re)enter edit (fallback to top-of-screen if node lookup fails)
    c = device.field_center() or (360, 60)
    device.tap(c[0], c[1], wait=0.2)      # small wait: keyboard may be showing
    device.type_text("X", wait=0.2)       # type immediately after the tap
    time.sleep(0.2)
    # hide keyboard so the field text is readable
    device.key(keys.BACK, wait=0.5)
    text = device.field_text().strip().lower()
    ok = (text == "x")
    if not ok:
        bad += 1
    verdict = "SELECTED(replaced)" if ok else "NOT SELECTED(appended/other)"
    print("  [T%02d] after=%r  %s" % (i, text, verdict))
    # cancel edit fully so the next cycle starts from the label
    device.key(keys.BACK, wait=0.4)
    time.sleep(0.2)

print("\nSUMMARY: %d/%d tap cycles selected the URL" % (CYCLES - bad, CYCLES))
