# TARP integration audit: current gate

This is a source-review architecture note. It does not certify the TARP protocol, relay deployment, or network isolation.

The separate Timison broker exposes distinct HOME/TARP services, but its current `fetch(url, method)` surface is a restricted HTTPS GET client. The TARP path requires a configured capability, explicitly configures the local proxy, rejects redirects, and returns bounded responses. The separate relay's HTTP adapter supports authenticated HTTP CONNECT and forwards credentials into the relay protocol. The broker fetch API therefore cannot serve as a general WebView networking backend.

Fulguris is a full WebView browser with multiple traffic origins: WebView navigation/subresources, DNS, JavaScript fetch/XHR, WebSockets, WebRTC, service workers, downloads/uploads, redirects, and app/background components. A `shouldInterceptRequest` implementation does not cover every origin and cannot establish a no-leak guarantee. An ordinary proxy preference also cannot prove that all processes and traffic are captured or that failure closes the route.

TARP remains unavailable in Timison Browser Next. Do not activate it or describe browsing as anonymous. A future implementation must use a dedicated Android UID/profile or equivalent OS-enforced boundary that permits only the authenticated TARP route, fails closed when credentials/route are unavailable, and prevents direct-network fallback. Validate DNS, WebRTC, WebSockets, downloads, uploads, service workers, redirects, background traffic, IPv4/IPv6, and route loss on device. Preserve HOME as normal Android networking and never silently switch between modes.

No source or network configuration in the separate TARP repository was changed in this browser work. No firewall, WireGuard, NAT, or public exposure changes were made.
