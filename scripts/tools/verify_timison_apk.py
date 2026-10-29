#!/usr/bin/env python3
"""Fail-closed package and signer check for Timison Browser Next APKs.

    python scripts/tools/verify_timison_apk.py --apk path/to/app.apk \
        --certificate-sha256 <pinned-certificate-fingerprint>

The fingerprint is public certificate data. Do not pass private key material to
this verifier or store signing credentials in the repository.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

EXPECTED_PACKAGE = "com.timison.browser.next.full.agent.debug"


def _tool(name: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    candidates: list[Path] = []
    if sdk:
        build_tools = Path(sdk) / "build-tools"
        if build_tools.is_dir():
            versions = sorted(p for p in build_tools.iterdir() if p.is_dir())
            candidates.extend(p / name for p in reversed(versions))
    from shutil import which
    found = which(name)
    if found:
        candidates.append(Path(found))
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise FileNotFoundError(f"Android SDK tool '{name}' not found; install Build Tools or pass --{name}")


def _run(command: list[str]) -> str:
    result = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=30, check=False)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{result.stdout}")
    return result.stdout


def verify(apk: Path | str, expected_cert: str, aapt: str, apksigner: str) -> str:
    apk = Path(apk)
    if not apk.is_file() or apk.stat().st_size == 0:
        raise ValueError(f"APK is missing or empty: {apk}")
    badging = _run([aapt, "dump", "badging", str(apk)])
    package_match = re.search(r"^package: name='([^']+)'", badging, re.MULTILINE)
    if not package_match:
        raise ValueError("APK package name is missing or unreadable")
    package = package_match.group(1)
    if package != EXPECTED_PACKAGE:
        raise ValueError(f"wrong APK package: expected {EXPECTED_PACKAGE}, got {package}")

    signing = _run([apksigner, "verify", "--verbose", "--print-certs", str(apk)])
    digests = re.findall(r"Signer #\d+ certificate SHA-256 digest:\s*([0-9a-fA-F:]+)", signing)
    if len(digests) != 1:
        raise ValueError(f"expected exactly one APK signer, found {len(digests)}")
    normalize = lambda value: re.sub(r"[^0-9a-f]", "", value.lower())
    actual = normalize(digests[0])
    expected = normalize(expected_cert)
    if len(expected) != 64 or actual != expected:
        raise ValueError(f"signing certificate mismatch: expected SHA-256 {expected_cert}, got {digests[0]}")
    return digests[0].replace(":", "").lower()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", required=True, type=Path)
    parser.add_argument("--certificate-sha256", default=os.environ.get("TIMISON_SIGNING_CERT_SHA256"),
                        help="pinned SHA-256 digest (required; can use TIMISON_SIGNING_CERT_SHA256)")
    parser.add_argument("--aapt", help="path to Android SDK aapt")
    parser.add_argument("--apksigner", help="path to Android SDK apksigner")
    args = parser.parse_args()
    if not args.certificate_sha256:
        parser.error("certificate fingerprint is required; refusing to accept any signer")
    try:
        aapt = _tool("aapt", args.aapt)
        apksigner = _tool("apksigner", args.apksigner)
        fingerprint = verify(args.apk, args.certificate_sha256, aapt, apksigner)
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"REJECTED: {error}", file=sys.stderr)
        return 1
    print(f"VERIFIED package={EXPECTED_PACKAGE} certificate_sha256={fingerprint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
