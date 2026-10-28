"""Timing/interaction-race probe for the address field edit state machine.

Targets the intermittent selection + label-reset bugs with the sequences most
likely to race the 400ms edit-start guard:
  T  touch (tap) edit cycles
  RE re-enter edit after a defocus (selection must re-establish)
  FP focus->edit->immediate-defocus->refocus (guard fires mid-transition)
  FF many rapid nav focus/unfocus cycles, then verify label stability
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import keys  # noqa: E402
from tests import appdevice  # noqa: E402

URL = "example.com"
PROBE = "zzz"


def enter_edit(dev):
    dev.enter_edit()


def defocus(dev):
    dev.key(keys.DPAD_DOWN, wait=0.6)


def wait_defocused(dev, timeout=6.0):
    deadline = time.time() + timeout
    while dev.field_focused() and time.time() < deadline:
        time.sleep(0.3)


def nav_focus(dev):
    dev.key(keys.SEARCH, wait=0.6)


def check_selection(dev, tag: str) -> bool:
    """True if the URL is currently selected (typing replaces the whole field)."""
    dev.type_text(PROBE, wait=0.5)
    got = dev.field_text()
    ok = got.strip().lower() == PROBE
    print("  [%s] selection: typed -> %r %s" % (tag, got, "OK" if ok else "NOT-SELECTED"))
    return ok


def main() -> int:
    serial = sys.argv[1] if len(sys.argv) > 1 else "R58R91GBTZK"
    dev = appdevice.FulgurisDevice(serial)
    dev.navigate(URL)
    label = dev.field_text()
    print("label: %r" % label)
    fails = 0

    # --- T: touch (tap) edit cycles -----------------------------------------
    print("== T: touch edit cycles ==")
    for i in range(4):
        c = dev.field_center()
        dev.tap(c[0], c[1], wait=0.9)
        if not check_selection(dev, "T%d" % i):
            fails += 1
        defocus(dev); wait_defocused(dev)

    # --- RE: re-enter edit after defocus ------------------------------------
    print("== RE: re-enter edit selection ==")
    for i in range(4):
        enter_edit(dev)
        dev.type_text("abc", wait=0.4)      # dirty the field
        defocus(dev); wait_defocused(dev)
        enter_edit(dev)                      # must re-select the URL
        if not check_selection(dev, "RE%d" % i):
            fails += 1
        defocus(dev); wait_defocused(dev)

    # --- FP: focus->edit->immediate defocus->refocus ------------------------
    print("== FP: rapid edit/defocus (guard mid-transition) ==")
    for i in range(6):
        enter_edit(dev)
        time.sleep(0.12)                     # defocus well before the 400ms guard
        dev.key(keys.DPAD_DOWN, wait=0.3)
        wait_defocused(dev)
        text = dev.field_text()
        if PROBE in text.lower() or text.strip().lower().startswith("http"):
            # label should be showing, not a URL
            print("  [FP%d] after rapid defocus field=%r (expected label %r)" % (i, text, label))
            fails += 1
        else:
            print("  [FP%d] after rapid defocus field=%r OK" % (i, text))

    # --- FF: many rapid nav focus/unfocus cycles ----------------------------
    print("== FF: rapid nav focus/unfocus x12 ==")
    for i in range(12):
        nav_focus(dev)
        time.sleep(0.15)
        dev.key(keys.DPAD_DOWN, wait=0.3)
    wait_defocused(dev)
    text = dev.field_text()
    print("  [FF] final field=%r expected label=%r %s" %
          (text, label, "OK" if text == label else "MISMATCH"))
    if text != label:
        fails += 1

    print("\nSUMMARY: %d problem(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
