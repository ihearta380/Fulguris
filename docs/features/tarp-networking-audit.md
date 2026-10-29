# TARP integration audit: current gate

This is a source-review architecture note. It does not certify the TARP protocol, relay deployment, or network isolation.

The separate Timison broker exposes distinct HOME/TARP services, but its current `fetch(url, method)` surface is a restricted HTTPS GET client. The TARP path requires a configured capability, explicitly configures the local proxy, rejects redirects, and returns bounded responses. The separate relay's HTTP adapter supports authenticated HTTP CONNECT and forwards credentials into the relay protocol. The broker fetch API therefore cannot serve as a general WebView networking backend.

Fulguris is a full WebView browser with multiple traffic origins: WebView navigation/subresources, DNS, JavaScript fetch/XHR, WebSockets, WebRTC, service workers, downloads/uploads, redirects, and app/background components. A `shouldInterceptRequest` implementation does not cover every origin and cannot establish a no-leak guarantee. An ordinary proxy preference also cannot prove that all processes and traffic are captured or that failure closes the route.

TARP remains unavailable in Timison Browser Next. Do not activate it or describe browsing as anonymous. A future implementation must use a dedicated Android UID/profile or equivalent OS-enforced boundary that permits only the authenticated TARP route, fails closed when credentials/route are unavailable, and prevents direct-network fallback. Validate DNS, WebRTC, WebSockets, downloads, uploads, service workers, redirects, background traffic, IPv4/IPv6, and route loss on device. Preserve HOME as normal Android networking and never silently switch between modes.

## Candidate integration boundary (design only; not implemented)

Keep the full browser renderer in the Timison Browser Next package and place
the TARP transport/VPN service in a separate signed package with a separate
Android UID. Bind the browser only to an authenticated transport control
interface; the browser must not own TARP credentials or a direct relay socket.
The transport service should expose readiness, route generation, and a narrow
health/status API. Do not expose a general URL-fetch API as a substitute for a
WebView network stack.

The transport package can own an Android `VpnService` and a userspace packet
forwarder for the browser UID. Configure the browser as the only allowed app in
the VPN, route both IPv4 and IPv6 default routes plus DNS through the TUN, and
require Android always-on VPN lockdown before declaring TARP ready. The
transport's authenticated relay connection is the explicit egress exception;
all other browser packets must be carried in the TUN. If the platform cannot
confirm the app allowlist, lockdown state, DNS route, or authenticated relay,
the browser must stay blocked. Switching to HOME requires an explicit user
action after a visible disconnect; transport loss while TARP is selected must
not switch modes.

This boundary still needs a feasibility spike: Android's VPN app has special
routing treatment for its own sockets, so keeping browser and VPN in one UID
would leave an ambiguous direct-egress surface. The candidate separate-UID
layout is intended to isolate that exception, but it is not yet proven. Verify
the actual Android 17 routing/lockdown semantics on Pixel 10 before adopting it.
Also audit WebView renderers, isolated processes, WebRTC UDP, QUIC, WebSockets,
DNS, service workers, file/content providers, uploads/downloads, app updates,
crash/analytics components, and browser intents against the UID route.

Acceptance requires an external packet capture at the device uplink and relay,
test-controlled DNS/HTTPS/WebSocket/WebRTC endpoints, route loss and bad
credential injection, and proof that only the authorized authenticated relay
connection appears outside the TUN. Tests must cover IPv4 and IPv6, redirects,
background/resumed tabs, downloads/uploads and service workers. Browser-side
logs are insufficient evidence. No such isolation test has run in this project
phase.

No source or network configuration in the separate TARP repository was changed in this browser work. No firewall, WireGuard, NAT, or public exposure changes were made.
