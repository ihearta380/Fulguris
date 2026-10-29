"""Unit tests for fail-closed Timison APK package and signer validation."""
from __future__ import annotations

from pathlib import Path
import contextlib
import io
import sys
import tempfile
import unittest
from unittest.mock import patch

import install_timison_apk
from verify_timison_apk import verify


CERT = "0123456789abcdef" * 4
BADGING = "package: name='com.timison.browser.next.full.agent.debug' versionCode='1'\n"
SIGNING = f"Verifies\nSigner #1 certificate SHA-256 digest: {CERT}\n"


class VerifyTimisonApkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.apk = Path(self.temp.name) / "browser.apk"
        self.apk.write_bytes(b"apk-test")

    def tearDown(self) -> None:
        self.temp.cleanup()

    @patch("verify_timison_apk._run", side_effect=[BADGING, SIGNING])
    def test_accepts_expected_package_and_certificate(self, _run) -> None:
        result = verify(str(self.apk), CERT.upper(), "aapt", "apksigner")
        self.assertEqual(result, CERT)

    @patch("verify_timison_apk._run", side_effect=[BADGING, RuntimeError("unsigned APK")])
    def test_rejects_unsigned_apk(self, _run) -> None:
        with self.assertRaisesRegex(RuntimeError, "unsigned APK"):
            verify(self.apk, CERT, "aapt", "apksigner")

    @patch("verify_timison_apk._run", return_value="package: name='wrong.package'\n")
    def test_rejects_wrong_package_before_signature_check(self, _run) -> None:
        with self.assertRaisesRegex(ValueError, "wrong APK package"):
            verify(self.apk, CERT, "aapt", "apksigner")
        _run.assert_called_once()

    @patch("verify_timison_apk._run", side_effect=[BADGING, SIGNING])
    def test_rejects_unexpected_certificate(self, _run) -> None:
        with self.assertRaisesRegex(ValueError, "signing certificate mismatch"):
            verify(self.apk, "f" * 64, "aapt", "apksigner")

    @patch("verify_timison_apk._run", side_effect=[BADGING, "Signer #1 certificate SHA-256 digest: a\nSigner #2 certificate SHA-256 digest: b\n"])
    def test_rejects_multiple_signers(self, _run) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one APK signer"):
            verify(self.apk, CERT, "aapt", "apksigner")

    @patch("install_timison_apk.adb.install_apk")
    @patch("install_timison_apk.adb.resolve_devices")
    @patch("install_timison_apk.verify", side_effect=ValueError("certificate mismatch"))
    def test_installer_rejects_before_device_or_install(self, _verify, resolve, install) -> None:
        argv = ["install_timison_apk.py", "--apk", str(self.apk), "--certificate-sha256", CERT]
        with patch.object(sys, "argv", argv), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(install_timison_apk.main(), 2)
        resolve.assert_not_called()
        install.assert_not_called()

    def test_verified_install_uses_update_install_only(self) -> None:
        argv = ["install_timison_apk.py", "--apk", str(self.apk), "--certificate-sha256", CERT, "--confirm"]
        with (patch.object(sys, "argv", argv),
              patch("install_timison_apk._tool", return_value="android-sdk-tool"),
              patch("install_timison_apk.verify", return_value=CERT),
              patch("install_timison_apk.adb.resolve_devices", return_value=["pixel-serial"]),
              patch("install_timison_apk.adb.device_label", return_value="Pixel 10"),
              patch("install_timison_apk.adb.install_apk", return_value=True) as install,
              contextlib.redirect_stdout(io.StringIO())):
            self.assertEqual(install_timison_apk.main(), 0)
        install.assert_called_once_with("pixel-serial", str(self.apk))


if __name__ == "__main__":
    unittest.main()
