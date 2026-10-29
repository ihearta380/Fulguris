# TARP integration audit: current gate

This is a source-review and platform-architecture note. It does not certify the TARP protocol, relay deployment, Android 17 route behavior, or network isolation.

## Browser transport requirements

The separate Timison broker exposes distinct HOME/TARP services, but its current `fetch(url, method)` surface is a restricted HTTPS GET client. The TARP path requires a configured capability, explicitly configures the local proxy, rejects redirects, and returns bounded responses. The separate relay's HTTP adapter supports authenticated HTTP CONNECT and forwards credentials into the relay protocol. The broker fetch API therefore cannot serve as a general WebView networking backend.

Fulguris uses Chromium WebView networking plus app and platform components. Relevant traffic includes navigation/subresources, DNS, JavaScript fetch/XHR, WebSockets, WebRTC, service workers, downloads/uploads, redirects, background activity, and IPv4/IPv6. `shouldInterceptRequest` does not cover every origin, and a WebView proxy setting does not establish a fail-closed route. A local proxy fetch API is not sufficient to preserve the browser's full networking behavior securely.

## Android VPN and existing WireGuard constraint

Android permits one active `VpnService` per Android user/profile. Starting another VPN in the same profile replaces the active service, so a TARP `VpnService` in the same Pixel profile cannot be assumed to coexist with the user's active WireGuard VPN. Android provides per-profile VPN support for managed work profiles, which is a possible isolation boundary, but the effects of profile routing, always-on lockdown, and the TARP service's own authenticated relay socket when the personal profile uses WireGuard have **not** been verified on this Pixel 10 / Android 17 setup.

Official platform references:

- [Android VPN developer guide](https://developer.android.com/develop/connectivity/vpn) — one active VPN service per user/profile, always-on VPN and lockdown, and per-profile VPN concepts.
- [Android `VpnService` API](https://developer.android.com/reference/android/net/VpnService) — VPN preparation/ownership and service behavior.
- [Android `VpnService.Builder` API](https://developer.android.com/reference/android/net/VpnService.Builder) — routes, allowed/disallowed applications, DNS, and proxy caveats.
- [WireGuard Android VPN service declaration](https://github.com/WireGuard/wireguard-android/blob/master/tunnel/src/main/AndroidManifest.xml) — confirms WireGuard Android uses a `VpnService`; it does not establish coexistence with TARP.

## Candidate architecture, not implemented

**Candidate: isolated managed work profile.** Keep WireGuard unchanged and active in the personal profile. Enroll a separately managed Android work profile, install Timison Browser Next and a dedicated TARP transport there, and configure Android's work-profile always-on VPN/lockdown to the TARP service. The TARP transport owns relay credentials and the tunnel; the browser binds to a narrow status/control interface and has no direct relay socket. Constrain the tunnel to the browser UID where platform behavior permits, and route IPv4, IPv6, and DNS through the authenticated TARP route. The app must show TARP as unavailable until the OS confirms the route, profile policy, authentication, and fail-closed state. Switching to HOME requires an explicit user action; loss of TARP must block navigation and must never fall back silently.

This is a feasibility candidate only. Work-profile VPN separation does not, by itself, prove that the TARP relay socket is carried inside the personal WireGuard tunnel, nor prove the intended outer-network path. Do not implement packet routing or enable a TARP selection until the following compatibility experiment is completed without changing WireGuard or network infrastructure:

1. On the target Pixel 10 / Android 17, record the current personal-profile WireGuard state and confirm the existing browser remains installed and operational.
2. Using Android's supported managed work-profile setup, install a test build and TARP transport only in that profile. Do not disable, replace, reconfigure, or revoke WireGuard.
3. Verify Android allows the work-profile TARP VPN while the personal-profile WireGuard VPN remains active. Establish the exact path of the authenticated relay socket (including whether it is nested through WireGuard or egresses another interface) using independent device/uplink and relay-side captures.
4. Verify work-profile always-on lockdown behavior on route loss, denied authentication, TARP service crash, DNS failure, and IPv4/IPv6. Show that browser-origin packets cannot appear directly at the uplink.
5. Exercise controlled DNS, HTTPS redirects, WebSockets, WebRTC UDP, uploads/downloads, service workers, background/resumed tabs, and app updates. Confirm the only permitted external flow is the authenticated TARP transport and that ordinary browser functionality is preserved.

If Android cannot establish the required route while preserving the personal WireGuard connection, stop. A single-profile combined VPN would require owning/rehosting the WireGuard tunnel inside a new VPN service and replacing the current WireGuard app's VPN role; that is outside the authorized scope and must not be attempted. An app-level proxy or WebView interception fallback is not acceptable.

## Current state and acceptance gate

TARP remains **unavailable** in the browser. No routing code, VPN service, relay credentials, or transport was added. There is no anonymity or leak-prevention claim. Status is **architecture documented; compatibility untested; routing unimplemented; security unverified**.

Security acceptance requires target-device fault injection plus independent packet capture at the device uplink and relay. Browser logs or compilation cannot establish isolation. Keep HOME on ordinary Android system networking, honoring the user's current Android VPN configuration.

No WireGuard, firewall, NAT, router, Ubuntu, or public-network-exposure configuration was changed.
