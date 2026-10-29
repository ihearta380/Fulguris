# Timison Browser Next

Timison Browser Next is a separately installable Fulguris-derived product flavor. The upstream `slions` flavor and its package identity remain available. Timison branding, launcher colors, seed bookmarks, and locale overlays are flavor-scoped; upstream Fulguris copyright/license material remains in the repository and applicable icon assets retain their attribution headers.

## Build and install

Build with the repository Python tool (Python 3.12, PyYAML, JDK 17, Android SDK 36, recursive submodules):

```sh
python scripts/tools/build.py --build-type timisonDebug
```

The APK is `app/build/outputs/apk/timisonFullAgent/debug/app-timison-full-agent-debug.apk`. It uses application ID `com.timison.browser.next.full.agent.debug`, so installation does not replace the regular Fulguris package or the existing Timison Browser package.

On a Pixel 10 connected through ADB, install/launch and run a focused regression set with the repository tools:

```sh
python scripts/tools/install.py --device SERIAL --build-type timisonDebug
python scripts/tools/launch.py --device SERIAL --restart --package com.timison.browser.next.full.agent.debug
python scripts/tests/run.py --device SERIAL --package com.timison.browser.next.full.agent.debug --group smoke
python scripts/tests/run.py --device SERIAL --package com.timison.browser.next.full.agent.debug --group bookmarks
python scripts/tests/run.py --device SERIAL --package com.timison.browser.next.full.agent.debug --group downloads
python scripts/tests/run.py --device SERIAL --package com.timison.browser.next.full.agent.debug --group history
python scripts/tests/run.py --device SERIAL --package com.timison.browser.next.full.agent.debug --group web-runtime
python scripts/tests/run.py --device SERIAL --package com.timison.browser.next.full.agent.debug --test https
```

`SERIAL` is the device serial shown by the project's device tooling. Do not use `adb` or `gradlew` directly; the repository scripts configure package selection and build paths. The complete `all` test group is slow and is not needed for this focused verification.

The `web-runtime` group serves a controlled page over `adb reverse` and checks
JavaScript execution, first-party cookies, localStorage across tabs, and active
tab restoration after an app restart. The `history` group covers Back and
Forward within a tab. HTTPS status tests in the `url-field` suite exercise a
valid certificate and an expired certificate warning. The suite covers
bookmarks and downloads in focused groups. File-upload picker flows and
app-settings/privacy controls still need explicit device validation. These
device tests must be run through the repository scripts; listing or compiling
the tests is not execution evidence.

## Network mode status

HOME uses ordinary Android system networking and follows the user's active Android VPN route. TARP is marked unavailable in the browser UI. This build does not route browser traffic through TARP and makes no anonymity or TARP protection claim.

Source review of the separate Timison TARP broker and relay found that the Android broker's current fetch API is limited to HTTPS GET, rejects redirects, and uses an explicitly configured loopback proxy; the relay adapter speaks authenticated HTTP CONNECT. This is not a complete WebView transport for ordinary browsing. Android allows one active `VpnService` per user/profile, so a second TARP VPN in the same profile would replace WireGuard. A managed work-profile VPN is a possible candidate, but its coexistence and route nesting through the user's personal-profile WireGuard have not been tested on the target Pixel. See the [TARP networking audit](tarp-networking-audit.md). TARP remains unavailable pending that compatibility experiment, authenticated routing, fail-closed behavior, and independent leak tests across all browser traffic sources.

No WireGuard, firewall, NAT, or Ubuntu network configuration was changed.

## Evidence classification

Record results in `TIMISON_NEXT_STATUS.md` by category: compiled, automated host-tested, installed, device-tested, and security-verified. Successful compilation does not establish Pixel runtime behavior or TARP leak resistance. GitHub Actions workflow runs on the development branch, verifies the package identity/launcher label, and uploads `timison-browser-next-debug-apk` as a 30-day downloadable workflow artifact.
