"""
Probe: the orphaned-edit-state desync.

The user reports that on the (heavy) slions.net resources page, rapidly tapping
the URL field and then tapping back on the page (to drop focus) can leave the
field showing the FULL URL with the text NOT selected, NO cursor, and the
unfocused background — i.e. isEditing got left true (or the focus/selection got
torn) while the field is not actually focused.

This probe navigates to the real page, then hammers the tap-field / tap-page
loop many times, checking the field state after each cycle. When it hits a
suspect state it waits and re-checks (to confirm it is a stable stuck state,
not a transient), and dumps it. It prints a summary of how many orphans were
seen so it can be run repeatedly to measure the fix.

Usage: python scripts/tests/probe_tap_defocus_loop.py <serial> [cycles]
"""

import sys
import time

sys.path.insert(0, ".")
from scripts.tests.appdevice import FulgurisDevice

SERIAL = sys.argv[1]
CYCLES = int(sys.argv[2]) if len(sys.argv) > 2 else 40
URL = "https://slions.net/resources/fulguris.10/"


def is_url(t: str) -> bool:
    t = t.lower()
    return t.startswith("http") or "://" in t


def main():
    d = FulgurisDevice(SERIAL)
    d.navigate(URL, reset=False)
    d.settle(3.0)  # let the heavy page finish loading
    cx, cy = d.field_center()
    print(f"field center: ({cx}, {cy})  cycles: {CYCLES}")

    orphans = 0
    problems = 0
    for i in range(CYCLES):
        d.tap(cx, cy, wait=0.05)          # tap the URL field -> start editing (+ keyboard+popup)
        d.tap(360, 700, wait=0.05)        # tap visible page (above keyboard) -> drop field focus
        if i % 4 == 3 or i == CYCLES - 1:
            text = (d.field_text() or "").strip()
            focused = d.field_focused()
            state = "ORPHAN" if (is_url(text) and not focused) else "ok"
            if state == "ORPHAN":
                # confirm it is a stable stuck state, not a transient mid-tap frame
                time.sleep(0.4)
                text2 = (d.field_text() or "").strip()
                focused2 = d.field_focused()
                if is_url(text2) and not focused2:
                    orphans += 1
                    problems += 1
                    print(f"cycle {i}: STUCK-ORPHAN  text={text2!r} focused={focused2}")
                    d.settle(0.3)
                else:
                    print(f"cycle {i}: transient orphan, recovered  text={text2!r} focused={focused2}")
            else:
                if i % 16 == 15:
                    print(f"cycle {i}: ok  text={text!r} focused={focused}")

    print(f"\nSUMMARY: {orphans} orphan state(s) observed over {CYCLES} cycles")


if __name__ == "__main__":
    main()
