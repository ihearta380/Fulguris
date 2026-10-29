#!/usr/bin/env python3
"""Install a deployable APK on a device or on all connected devices.

The agentDebug variant (slionsFullAgentDebug) is a debug build of the "agent"
PUBLISHER flavor — a robot launcher icon, dedicated to automated testing; see
docs/features/agent-variant.md.

    python scripts/tools/install.py                 # single device, or all if only one
    python scripts/tools/install.py --all
    python scripts/tools/install.py --device SERIAL
    python scripts/tools/install.py --build         # build first, then install
    python scripts/tools/install.py --build-type agentRelease
    python scripts/tools/install.py --build --build-type downloadDebug
"""
from __future__ import annotations

import argparse
import os
import sys

import adb
from verify_timison_apk import _tool, verify


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", help="Target a specific adb device serial")
    parser.add_argument("--all", action="store_true", help="Install on all connected devices")
    parser.add_argument("--build", action="store_true", help="Build before installing")
    parser.add_argument("--build-type", choices=sorted(adb.AGENT_VARIANTS),
                        default=adb.DEFAULT_BUILD_TYPE,
                        help="Which variant to install (default: agentDebug)")
    parser.add_argument("--certificate-sha256", default=os.environ.get("TIMISON_SIGNING_CERT_SHA256"),
                        help="required pinned certificate SHA-256 when installing timisonDebug")
    args = parser.parse_args()

    if args.build:
        code = adb.gradle_build(args.build_type)
        if code != 0:
            print("Build FAILED, not installing.")
            return code

    apk = adb.apk_path(args.build_type)
    if not apk:
        print("No APK found; run build first.")
        return 2

    if args.build_type == "timisonDebug":
        if not args.certificate_sha256:
            print("Install rejected: set TIMISON_SIGNING_CERT_SHA256 or --certificate-sha256.", file=sys.stderr)
            return 2
        try:
            fingerprint = verify(apk, args.certificate_sha256, _tool("aapt", None), _tool("apksigner", None))
        except Exception as error:  # noqa: BLE001 - reject before reaching the device installer
            print(f"Install rejected: Timison APK verification failed: {error}", file=sys.stderr)
            return 2
        print(f"Timison APK verified: package=com.timison.browser.next.full.agent.debug certificate_sha256={fingerprint}")

    ok = True
    for serial in adb.resolve_devices(args.device, args.all):
        success = adb.install_apk(serial, apk)
        print(f"{'OK  ' if success else 'FAIL'} {adb.device_label(serial)}")
        ok = ok and success
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
