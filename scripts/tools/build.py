#!/usr/bin/env python3
"""Build a deployable APK (default: the slionsFullAgentDebug variant).

"agent" is a PUBLISHER-dimension flavor with a robot launcher icon, dedicated to
automated testing; see docs/features/agent-variant.md.

    python scripts/tools/build.py                    # agentDebug (default)
    python scripts/tools/build.py --build-type agentRelease
"""
from __future__ import annotations

import argparse
import os
import sys

import adb
from verify_timison_apk import _tool, verify


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--build-type", choices=sorted(adb.AGENT_VARIANTS),
                        default=adb.DEFAULT_BUILD_TYPE,
                        help="Which variant to build (default: agentDebug)")
    args = parser.parse_args()

    code = adb.gradle_build(args.build_type)
    if code != 0:
        print("Build FAILED.")
        return code
    out = adb.build_output_path(args.build_type)
    if args.build_type == "timisonDebug":
        certificate = os.environ.get("TIMISON_SIGNING_CERT_SHA256")
        if not certificate:
            print("Build rejected: set TIMISON_SIGNING_CERT_SHA256 to the pinned Timison signing certificate fingerprint.", file=sys.stderr)
            return 2
        try:
            fingerprint = verify(out, certificate, _tool("aapt", None), _tool("apksigner", None))
        except Exception as error:  # noqa: BLE001 - deployment tool must fail closed
            print(f"Timison APK verification FAILED: {error}", file=sys.stderr)
            return 2
        print(f"Timison APK verified: package=com.timison.browser.next.full.agent.debug certificate_sha256={fingerprint}")
    print(f"Build OK: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
