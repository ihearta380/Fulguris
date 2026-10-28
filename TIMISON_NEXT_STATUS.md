# Timison Browser Next — status and evidence

Updated: 2026-10-28

## Milestone A — upstream baseline

**Status: BUILD PASSED; DEVICE SMOKE TEST NOT RUN.**

- Repository remotes: `origin https://github.com/ihearta380/Fulguris.git`;
  `upstream https://github.com/Slion/Fulguris.git`.
- Checked-out upstream commit: `51d211ac838a7d251af71024e5bffe74e450ab61`.
- Submodules (checked out SHAs): AppIntro
  `ade32f63f0edc871920ca8a7a59d269f136c1dd0`; AutoTest
  `cdf207c6a5cb5a3d1a3f5eddb2dbc62f311bdf24`; Preference
  `92540b03cbb049a74890055472d94cd1f2630b4b`; l10n
  `70cfc8d2a71493cfdde5d7408204a9e1ed647f72`; wiki
  `0e05ccc0d87effe00962c1630e73d3b7fda9749e`.
- Root `LICENSE` states post-`53528d0` sole-author files are CPAL-1.0 and other
  files default to MPL-2.0 unless otherwise specified. Both root license texts
  are retained; `LICENSE-CPAL-1.0`, `LICENSE-MPL-2.0`, and submodule `LICENSE`
  files remain in the repository. Kotlin/resource headers identify Fulguris and
  original developer attribution. No license/notice files were removed.
- Build environment used: `.venv/bin/python` 3.12.16 with PyYAML 6.0.3;
  temporary Temurin JDK 17.0.21+9 under ignored `.temp/`; Android SDK API 36
  and Build Tools 36.0.0. Gradle wrapper 8.14.3 downloaded into `.temp`.
- Baseline command: `.venv/bin/python scripts/tools/build.py` with `GRADLE_USER_HOME`,
  `JAVA_HOME`, `ANDROID_HOME`, and `ANDROID_SDK_ROOT` set as documented →
  **BUILD SUCCESSFUL**, `:app:assembleSlionsFullAgentDebug` (93 tasks).
- Baseline APK: `app/build/outputs/apk/slionsFullAgent/debug/Fulguris-v2.1.2-slions-full-agent-debug.apk`; 20,896,724 bytes; SHA256
  `ac430f6102caf988a641af26e2daa3eef0e63f7457fed829cf0e42e5934615d7`;
  package `net.slions.fulguris.full.agent.debug`; launch activity
  `fulguris.activity.SplashActivity`.
- Initial host validation attempts failed because the default Python is 3.8.5,
  Gradle's default cache is not writable, and Java 16 is too old. Using the
  user's `.venv`, repo-local Gradle cache and temporary JDK 17 resolved these
  host-side blockers. A Gradle 8 deprecation warning and upstream Kotlin/API
  deprecation warnings remain; no source changes were needed for baseline.

## Milestone B — Timison variant

**Status: BUILD PASSED; DEVICE TESTS NOT VERIFIED.**

- Added `timison` brand flavor and `timisonDebug` project build-tool option.
- Package verified from the built manifest:
  `com.timison.browser.next.full.agent.debug`; launcher label:
  `Timison Browser Next`.
- The existing TARP project's UI resources contain no launcher artwork. Its
  source theme specifies `#11161F` and `#5FE0C5`; Timison Next now uses those
  colors and a new vector T monogram instead of the upstream Fulguris mark.
  Existing source attribution and component headers remain.
  Existing Fulguris tab, JavaScript, cookie,
  bookmark, history and download code is shared unchanged.
- Build command: `python scripts/tools/build.py --build-type timisonDebug` →
  **BUILD SUCCESSFUL**, `:app:assembleTimisonFullAgentDebug` (93 tasks).
- The first Timison build failed at resource linking because `src/slions/res`
  was not included; the flavor source set now consumes those upstream resources
  (including default bookmarks and contact metadata). The subsequent build
  passed.
- Timison APK:
  `app/build/outputs/apk/timisonFullAgent/debug/app-timison-full-agent-debug.apk`;
  24,398,602 bytes; SHA256
  `07ad6b609c1f67e17aa960cfd7aa6039259b18caceeae1d1e65e4bce3d5941b9`;
  package `com.timison.browser.next.full.agent.debug`; label `Timison Browser
  Next`; launch activity `fulguris.activity.SplashActivity`; compile/target SDK
  36. `aapt dump badging` confirms metadata and `unzip -t` reports no archive
  errors.
- `.venv/bin/python scripts/tests/run.py --all --group smoke --package
  com.timison.browser.next.full.agent.debug --no-save` → **NOT RUN**: project
  tooling reported `No devices connected over adb`. ADB daemon access is also
  restricted in the environment. Pixel 10 installation, package coexistence,
  screenshots and all requested browser feature tests remain **NOT VERIFIED**.
- `.venv/bin/python scripts/tests/run.py --list` → **PASS**, test suite imports
  and enumerates. This is test discovery only, not execution of browser tests.
- `.venv/bin/python scripts/tools/install.py --all --build-type timisonDebug`
  → **NOT RUN**, `No devices connected over adb`; no APK installation was
  attempted.
- No install, uninstall, clear-data, or external app package operation ran.

## Milestone C — networking architecture

**Status: SOURCE AUDIT DOCUMENTED; NO ISOLATION CLAIM.** See
[`docs/features/tarp-networking-audit.md`](docs/features/tarp-networking-audit.md).
Fulguris requests INTERNET, allows cleartext, and relies on Chromium WebView
network paths plus external download/intent paths. A proxy preference or
`shouldInterceptRequest` cannot enforce complete fail-closed routing. TARP is
unavailable pending authenticated installed-key testing, independent traffic
capture, and fault-injection proof that direct fallback is impossible.

No Ubuntu host, WireGuard, firewall, NAT, router, or network exposure settings
were changed. No Tor or AWS dependency was introduced.

## Remaining release gates

1. Make the authorized Pixel 10 visible to project ADB tooling.
2. Verify original Timison package IDs remain installed and untouched, then
   install and exercise navigation, JavaScript, cookies, tabs, bookmarks,
   history, downloads and common sites on Pixel 10.
3. Keep TARP unavailable until the documented isolation gates pass.
