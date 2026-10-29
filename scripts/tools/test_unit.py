#!/usr/bin/env python3
"""Run app-module local JVM regression tests.

    python scripts/tools/test_unit.py --build-type agentDebug
    python scripts/tools/test_unit.py --build-type timisonDebug
"""
from __future__ import annotations

import argparse

import adb


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--build-type", choices=sorted(adb.UNIT_TEST_VARIANTS), required=True)
    parser.add_argument("--test-class", action="append", default=[],
                        help="Fully qualified JUnit class to run (repeatable)")
    args = parser.parse_args()
    code = adb.gradle_unit_test(args.build_type, args.test_class)
    print("Unit tests PASSED." if code == 0 else "Unit tests FAILED.")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
