# TARP networking audit (source review)

Status: **TARP unavailable / not configured**. The Timison Browser Next variant
is an ordinary, internet-capable Fulguris WebView browser. This review does not
establish isolation and no TARP controls are exposed in the application.

## Observed paths

- `app/src/main/AndroidManifest.xml` requests `android.permission.INTERNET`,
  enables cleartext traffic, and declares `network_security_config`.
- Page loads, redirects, JavaScript `fetch`/XHR, WebSockets, service workers,
  DNS resolution, WebRTC, and WebView prefetch are handled by Chromium/WebView's
  networking implementation. Application request callbacks do not constitute a
  complete boundary for these paths.
- Fulguris has WebView interception/ad blocking and proxy-related preferences,
  but these are application features, not OS-enforced network isolation. They
  cannot prove that Chromium's full traffic surface or proxy-bypassing paths
  are contained.
- App-owned networking is also present: `app/src/main/java/fulguris/network/`
  defines WebView, `HttpURLConnection`, and OkHttp network engines; suggestion
  providers and the ad-blocking implementation use OkHttp. Any TARP boundary
  would have to account for these clients in addition to Chromium.
- Downloads are handed to Android's download facilities and external intents
  can pass links to other applications. Those paths leave the browser process
  and would need separate policy enforcement in a TARP design.
- Cookies and browser storage are WebView-managed. They are not a network path
  themselves, but cookies/service-worker state must be considered when defining
  a TARP session boundary.

## Feasibility and gate

The present architecture cannot demonstrate fail-closed TARP behavior. A
WebView proxy setting or `shouldInterceptRequest` alone is insufficient.
TARP therefore remains unavailable until there is a separately enforced
network boundary, authenticated installed-key CONNECT verification, controlled
failure injection, and independent device-side traffic capture. This work did
not contact or modify the Ubuntu host, WireGuard, firewall, NAT, router, or
network exposure.

## Required verification before any TARP UI action

1. Inventory every browser and external-app traffic path on-device.
2. Verify the installed-key authenticated CONNECT path against the intended
   service without weakening TLS or authentication.
3. Capture device traffic independently while exercising redirects,
   JavaScript fetch/XHR, WebSockets, WebRTC, DNS, downloads, service workers,
   prefetch and external intents.
4. Disable/fault the tunnel and prove all TARP-originated traffic fails closed,
   with no direct Home-network packet path. Repeat after process restart and
   Android network changes.

Until these gates pass, no TARP mode may be enabled.
