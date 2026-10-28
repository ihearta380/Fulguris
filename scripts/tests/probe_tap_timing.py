#!/usr/bin/env python3
"""Tap + type at VARIABLE delays after the tap to expose any remaining unselected
window on the touch path. Types 'X' at each delay and checks the URL was replaced.
If selection is established at the frame after the tap, EVERY delay should replace."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import keys
from tests import appdevice

SER = sys.argv[1] if len(sys.argv) > 1 else None
device = appdevice.FulgurisDevice(SER)
device.restart()
device.navigate("example.com", reset=False)
time.sleep(1.5)
label = device.field_text()
print("label:", repr(label))

# delays (ms) after the tap before typing, covering the old 0..400ms guard window
delays = [0, 20, 40, 60, 80, 100, 120, 150, 200, 250, 300, 350, 400]

def webview():
    return (360, 800)

bad = 0
total = 0
for d in delays:
    # defocus: tap webview
    device.tap(*webview(), wait=0.45)
    time.sleep(0.2)
    c = device.field_center() or (360, 60)
    device.tap(c[0], c[1], wait=0.15)   # small wait after the tap
    time.sleep(d / 1000.0)              # the variable delay under test
    device.type_text("X", wait=0.1)
    time.sleep(0.2)
    device.key(keys.BACK, wait=0.4)     # hide keyboard
    text = device.field_text().strip().lower()
    device.key(keys.BACK, wait=0.3)     # cancel
    time.sleep(0.15)
    total += 1
    ok = (text == "x")
    if not ok:
        bad += 1
    print("  delay=%4dms  after=%-22r  %s" % (d, text, "SELECTED" if ok else "NOT SELECTED"))

print("\nSUMMARY: %d/%d delays replaced the URL" % (total - bad, total))
