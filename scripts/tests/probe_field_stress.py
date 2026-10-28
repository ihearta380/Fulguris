"""Comprehensive stress probe for the address field focus/edit state machine.

Cycles focus/unfocus/edit/type many times with mixed action patterns and checks
two invariants after every cycle:

  * INV-SELECT  — entering edit mode selects the whole URL (typing replaces it).
  * INV-LABEL   — after the field loses focus it shows the label, not stale text.

Exit code 0 = all cycles held both invariants; 1 = at least one failure. Prints
a per-cycle table plus a summary.
"""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import keys  # noqa: E402
from tests import appdevice  # noqa: E402

URL = "example.com"
PROBE = "zzz"          # typed characters (distinct from the label)
CYCLES = int(sys.argv[2]) if len(sys.argv) > 2 else 6


def enter_edit(dev):
    dev.enter_edit()  # SEARCH (nav focus) + DPAD_CENTER (edit; guard selects all)


def defocus(dev):
    """Move focus off the field to the web view."""
    dev.key(keys.DPAD_DOWN, wait=0.6)


def wait_defocused(dev, timeout=6.0):
    deadline = time.time() + timeout
    while dev.field_focused() and time.time() < deadline:
        time.sleep(0.3)


def cycle(dev, label: str) -> None:
    enter_edit(dev)
    dev.type_text(PROBE, wait=0.5)
    after_type = dev.field_text()
    replaced = after_type.strip().lower() == PROBE
    defocus(dev)
    wait_defocused(dev)
    after_defo = dev.field_text()
    stale = PROBE in after_defo.lower()
    print("  [%s] type=%s replace=%s | defocus=%r label=%s stale=%s" % (
        label, repr(after_type), "OK" if replaced else "BAD",
        after_defo, "OK" if not stale else "BAD", "STALE" if stale else "ok"))
    return replaced, stale


def main() -> int:
    serial = sys.argv[1] if len(sys.argv) > 1 else "R58R91GBTZK"
    dev = appdevice.FulgurisDevice(serial)
    print("package:", dev._package)

    dev.navigate(URL)
    label = dev.field_text()
    print("label after navigate: %r" % label)

    failures = 0
    for i in range(CYCLES):
        replaced, stale = cycle(dev, "cycle %d" % i)
        if not replaced:
            failures += 1
            print("    -> INV-SELECT FAILED: URL not selected (typing appended)")
        if stale:
            failures += 1
            print("    -> INV-LABEL FAILED: typed text still present after defocus")

    print("\nSUMMARY: %d/%d cycles clean" % (CYCLES - failures, CYCLES))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
