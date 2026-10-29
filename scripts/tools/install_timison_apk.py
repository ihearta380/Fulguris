#!/usr/bin/env python3
"""Verify a Timison APK before offering a non-destructive ADB update install."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys

import adb
from verify_timison_apk import _tool, verify


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--device", help="ADB serial; omitted only when exactly one device is connected")
    parser.add_argument("--certificate-sha256", default=os.environ.get("TIMISON_SIGNING_CERT_SHA256"))
    parser.add_argument("--confirm", action="store_true", help="skip confirmation (use only from an already-confirmed deployment wrapper)")
    args = parser.parse_args()
    if not args.certificate_sha256:
        parser.error("certificate fingerprint is required; refusing to install an unpinned APK")

    try:
        fingerprint = verify(args.apk, args.certificate_sha256, _tool("aapt", None), _tool("apksigner", None))
    except Exception as error:  # noqa: BLE001 - fail closed before the install path
        print(f"REJECTED: {error}", file=sys.stderr)
        return 2

    serials = adb.resolve_devices(args.device, False)
    if len(serials) != 1:
        print(f"REJECTED: expected exactly one selected device, got {len(serials)}", file=sys.stderr)
        return 2
    serial = serials[0]
    apk_sha = hashlib.sha256(args.apk.read_bytes()).hexdigest()
    print(f"VERIFIED package=com.timison.browser.next.full.agent.debug certificate_sha256={fingerprint}")
    print(f"APK SHA256: {apk_sha}\nADB device: {adb.device_label(serial)} ({serial})")
    print("Install uses adb install -r only. This tool never uninstalls or clears app data.")
    if not args.confirm:
        confirmation = input("Install this APK? Type INSTALL: ")
        if confirmation != "INSTALL":
            print("Cancelled")
            return 0
    if not adb.install_apk(serial, str(args.apk)):
        print("Install FAILED. The installed package was not uninstalled or cleared.", file=sys.stderr)
        return 1
    print("Installed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
