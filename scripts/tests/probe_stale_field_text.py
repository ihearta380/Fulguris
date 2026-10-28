"""Repro probe: after typing in the address field, moving focus to another
element should reset the field to the tab label, but it may keep the typed text."""
from __future__ import annotations

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import keys  # noqa: E402
from tests import appdevice  # noqa: E402

def main() -> None:
    serial = sys.argv[1] if len(sys.argv) > 1 else "R58R91GBTZK"
    dev = appdevice.FulgurisDevice(serial)
    print("package:", dev._package)

    dev.navigate("example.com")
    label = dev.field_text()
    print("1) after navigate  focused=%s ime=%s text=%r" %
          (dev.field_focused(), dev.ime_shown(), label))

    # Enter edit mode (focus for navigation then center -> edit + select all).
    dev.enter_edit()
    time.sleep(0.4)
    print("2) in edit         focused=%s ime=%s text=%r" %
          (dev.field_focused(), dev.ime_shown(), dev.field_text()))

    # Type some characters (replaces the selected URL).
    dev.type_text("qqq", wait=0.6)
    typed = dev.field_text()
    print("3) typed 'qqq'     focused=%s ime=%s text=%r" %
          (dev.field_focused(), dev.ime_shown(), typed))

    # Hide the keyboard so field_text reads the field (not the IME).
    dev.key(keys.BACK, wait=0.8)
    print("4) after 1st BACK  focused=%s ime=%s text=%r" %
          (dev.field_focused(), dev.ime_shown(), dev.field_text()))

    # Move focus to another element: D-pad DOWN leaves the field for the web view.
    dev.key(keys.DPAD_DOWN, wait=0.9)
    print("5) after DPAD_DOWN focused=%s webview=%s ime=%s text=%r" %
          (dev.field_focused(), dev.webview_focused(), dev.ime_shown(), dev.field_text()))

    time.sleep(0.5)
    print("6) settle          focused=%s webview=%s ime=%s text=%r" %
          (dev.field_focused(), dev.webview_focused(), dev.ime_shown(), dev.field_text()))

    final = dev.field_text()
    if "qqq" in final.lower():
        print("RESULT: BUG REPRODUCED - typed text still in field after focus left: %r" % final)
    else:
        print("RESULT: OK - field reset to label after focus left: %r" % final)


if __name__ == "__main__":
    main()
