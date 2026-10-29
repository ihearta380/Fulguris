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
```

`SERIAL` is the device serial shown by the project's device tooling. Do not use `adb` or `gradlew` directly; the repository scripts configure package selection and build paths. The complete `all` test group is slow and is not needed for this focused verification.

## Network mode status

HOME uses ordinary Android system networking and follows the user's active Android VPN route. TARP is marked unavailable in the browser UI. This build does not route browser traffic through TARP and makes no anonymity or TARP protection claim.

Source review of the separate Timison TARP broker and relay found that the Android broker's current fetch API is limited to HTTPS GET, rejects redirects, and uses an explicitly configured loopback proxy; the relay adapter speaks authenticated HTTP CONNECT. This is not a complete WebView transport for POST/forms, JavaScript-created requests, WebSockets, WebRTC, service workers, DNS, downloads, or background services. Request interception or a WebView proxy setting alone cannot prove isolation. Before TARP can be enabled, the integration needs an OS-enforced per-app network boundary (for example, a dedicated Android UID/profile whose only permitted route is the authenticated TARP tunnel), fail-closed route establishment, and device tests for every listed traffic source. A missing route must stop browsing and must never fall back to HOME.

No WireGuard, firewall, NAT, or Ubuntu network configuration was changed.

## Evidence classification

Record results in `TIMISON_NEXT_STATUS.md` by category: compiled, automated host-tested, installed, device-tested, and security-verified. Successful compilation does not establish Pixel runtime behavior or TARP leak resistance. GitHub Actions workflow runs on the development branch, verifies the package identity/launcher label, and uploads `timison-browser-next-debug-apk` as a 30-day downloadable workflow artifact.
