# Timison Browser Next — status and evidence

Updated: 2026-10-28 (Phase F4)

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
- Revalidated with the committed upstream `app/build.gradle` restored
  temporarily; the project build tool reported **BUILD SUCCESSFUL** for the
  upstream variant, with its compile/package tasks already up-to-date from the
  initial successful baseline build.
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
- The Timison flavor owns its needed metadata and seed bookmark resources; the
  build uses Android's main/flavor overlay model rather than duplicate-importing
  the whole `src/slions/res` resource tree.
- Timison APK:
  `app/build/outputs/apk/timisonFullAgent/debug/app-timison-full-agent-debug.apk`;
  SHA256 `fdf7436eb537945ef7779187ecd678e0ad52ffb5f1b87252529793b3c1bdec41`;
  package `com.timison.browser.next.full.agent.debug`; label `Timison Browser
  Next`; launch activity `fulguris.activity.SplashActivity`; compile/target SDK
  36. `aapt dump badging` confirms metadata and `unzip -t` reports no archive
  errors.
- `.venv/bin/python scripts/tests/run.py --all --group smoke --package
  com.timison.browser.next.full.agent.debug --no-save` → **NOT RUN**: project
  tooling reported `No devices connected over adb`. Pixel 10 installation,
  package coexistence, screenshots and all requested browser feature tests
  remain **NOT VERIFIED**.
- `.venv/bin/python scripts/tests/run.py --list` → **PASS**, test suite imports
  and enumerates. This is test discovery only, not execution of browser tests.
- `.venv/bin/python scripts/tools/install.py --all --build-type timisonDebug`
  → **NOT RUN**, `No devices connected over adb`; no APK installation was
  attempted.
- No install, uninstall, clear-data, or external app package operation ran.

## Branch and review

- Development branch: `timison-browser-next-development`, pushed to `origin`
  (`ihearta380/Fulguris`).
- Draft pull request: [#1 Add Timison Browser Next build
  variant](https://github.com/ihearta380/Fulguris/pull/1), targeting `main`.

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

## Phase F4 — branding, browser QA, and artifact publication

**Status: BOTH FLAVORS COMPILED; PACKAGE/METADATA CHECKS PASSED; DEVICE QA BLOCKED.**

- Built the original Fulguris `agentDebug` and Timison `timisonDebug` variants
  through `scripts/tools/build.py`. Both `assemble` tasks completed successfully
  after removing a duplicate flavor resource definition. APK ZIP integrity
  checks passed. The original package remains
  `net.slions.fulguris.full.agent.debug`; Timison is
  `com.timison.browser.next.full.agent.debug`.
- Timison APK at `artifacts/timison-browser-next-debug.apk` (same as the Gradle
  output) has SHA256
  `89a99cba3a3c4d6e46bd72cda8208af39b9bf07226cf0c3c4034e61a10a9bc13` and is
  approximately 23 MiB. `aapt dump badging` confirmed the package, version
  `2.1.2-timison`, and launcher label `Timison Browser Next`.
- Branding work is Timison-flavor scoped: updated app-facing brand strings in
  available locales, Timison default bookmarks (the app only seeds defaults for
  a fresh bookmark database), a T monogram and palette, and recolored secondary
  incognito/settings app icons. Homepage/bookmarks headers show HOME active and
  TARP unavailable. Fulguris attribution/license files and icon headers remain.
  Original `slions` source resources and branding remain unchanged.
- Added `docs/features/timison-browser-next.md` with build, Pixel install/test
  commands and mode claims. Added a TARP audit describing the source-reviewed
  broker/relay limitations and the OS-enforced, fail-closed architecture gate.
  TARP is not activated, no anonymity claim is made, and no host/network
  configuration was changed.
- Historical host unit run: Robolectric 4.4 rejected Java 17 class files; after
  upgrading test-only Robolectric to 4.14.1, two broadcast assertions and an
  empty/commented `CloseableExtensionsTest` remained. Follow-up fixes and the
  fully green reruns are recorded below.
- `scripts/tools/ui.py state` → **BLOCKED**: `No devices connected over adb`.
  Pixel 10 install, modern HTTPS/TLS behavior and JavaScript, cookies/storage,
  tabs/session restore, bookmarks/history, download/upload, navigation controls,
  settings/privacy, and any network-leak tests are therefore not device-tested.
  Do not treat build/unit tests as device or security verification.
- Added `.github/workflows/timison-browser-next.yml` to build on development
  branch pushes and upload the APK as a 30-day Actions artifact named
  `timison-browser-next-debug-apk`. The first hosted run status is recorded
  below.
- Exact Pixel commands: see
  [`docs/features/timison-browser-next.md`](docs/features/timison-browser-next.md).

## Follow-up — unit tests, Pixel report, and hosted artifact workflow

- Repaired the Robolectric broadcast tests to drain the main looper between
  broadcast and assertion. Restored active `safeUse` tests for result/close and
  absorbed exception/close cases. Added `--test-class` filtering to
  `scripts/tools/test_unit.py` for deterministic reproduction.
- Targeted Timison run:
  `python scripts/tools/test_unit.py --build-type timisonDebug --test-class
  fulguris.rx.BroadcastReceiverObservableTest --test-class
  fulguris.extensions.CloseableExtensionsTest` → **PASS**.
- Full original and Timison unit runs:
  `python scripts/tools/test_unit.py --build-type agentDebug` and
  `python scripts/tools/test_unit.py --build-type timisonDebug` → **PASS**.
  Each completed all 83 test cases with zero failures/errors. The two branding
  tests are included in both variants.
- User-reported Pixel 10 check: Timison APK installed successfully; Google
  Search rendered images and modern layouts; multiple tabs worked; yellow/orange
  theme visible. This is user-reported manual evidence, not a locally captured
  test record. Rechecking `python scripts/tools/ui.py state` still reports
  `No devices connected over adb`, so the automated Pixel suite and remaining
  browser features (TLS failure handling, JS/cookie/storage, tab restore,
  bookmarks/history, downloads/uploads, navigation/settings/privacy) remain
  device-unverified here.
- Added a deterministic `web-runtime` device test with a host-served test page
  for JavaScript execution, first-party cookies, localStorage across tabs, and
  active tab restoration after app restart. The test is registered and listed;
  it has **not run on a device** because ADB reports no devices.
- GitHub push succeeded using a fixed-size HTTP request after normal chunked
  sends failed. Commit `0d7f0a49` is on the fork branch. Timison workflow run
  [40798390886](https://github.com/ihearta380/Fulguris/actions/runs/40798390886)
  **PASSED** on that commit: checkout, JDK, Python, Android SDK setup, PyYAML,
  APK build, package/label check, and artifact upload all completed
  successfully. Artifact `12864464347`, named
  `timison-browser-next-debug-apk`, is 17,739,601 bytes and expires
  2026-11-28. It is downloadable from the Actions run page. This is the
  workflow-produced APK; local package metadata checks also passed.
- TARP remains disabled. The audit now includes a design-only separate-UID
  `VpnService`/always-on lockdown candidate, its unresolved Android 17 routing
  feasibility question, and explicit external packet-capture acceptance
  requirements. This is architecture design, not implemented or security
  verified.

## Follow-up — browser coverage and WireGuard/TARP compatibility gate

**Status: FORWARD TEST ADDED; ANDROID DEVICE TESTING BLOCKED; TARP COMPATIBILITY UNTESTED.**

- Added `test_in_tab_forward_navigates_history` to the focused `history` group.
  It serves the existing controlled local pages, verifies Back returns from B
  to A, then activates the accessible Forward toolbar action and checks that B
  returns. It uses the UI automation node API and avoids hard-coded screen
  coordinates. This test has not yet run on Pixel because the available ADB
  tooling reports no connected device.
- Existing coverage includes valid/expired HTTPS status, refresh/Stop,
  JavaScript, cookies, localStorage across tabs, session restore, bookmarks,
  downloads and Back. Upload chooser and settings/privacy flows remain explicit
  device-validation gaps; no passing claim is made for those paths. See the
  exact focused commands in `docs/features/timison-browser-next.md`.
- Source-reviewed Android's VPN guide/API and upstream WireGuard Android service
  declaration. Android allows one active `VpnService` per user/profile; a
  second VPN in the same profile would replace the current one. A separate
  managed work-profile TARP VPN is only a candidate. Whether its authenticated
  relay route nests through the personal-profile WireGuard and whether lockdown
  prevents all bypasses on Pixel 10 / Android 17 are untested. Updated
  `docs/features/tarp-networking-audit.md` with a no-infrastructure-change
  feasibility experiment and explicit security acceptance gates.
- TARP remains unavailable and no transport/routing code was implemented. No
  WireGuard, firewall, NAT, router, Ubuntu, or public exposure settings changed.
- Validation for this follow-up: test discovery and Python syntax checks are
  recorded after execution below. Pixel regression tests remain blocked by
  `No devices connected over adb`; this is not device or security verification.
