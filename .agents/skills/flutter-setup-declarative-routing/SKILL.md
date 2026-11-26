---
name: flutter-setup-declarative-routing
stack: flutter
description: Add or extend declarative routing and deep links (for example `go_router` with `MaterialApp.router`). Use for URL-based navigation, deep linking, nested navigation, or browser history.
---

# Declarative Routing and Deep Links

Inspect the existing router, route definitions, guards, and navigation tests first. Extend the established router; adding `go_router` or another routing package is a new dependency and needs approval.

## Routes

With `go_router` (map these to the project's router otherwise):

- Keep one router configuration. Add routes as `GoRoute` paths with typed parameter parsing; reject or redirect invalid parameters instead of using `!` on `pathParameters`.
- Put auth and state redirects in the router's `redirect`, reading existing auth state; avoid redirect loops and handle loading state.
- Use `StatefulShellRoute.indexedStack` for persistent tabs whose branches keep state; `ShellRoute` when state need not persist.
- Use `context.go` to replace the stack and `context.push` to add to it, matching existing navigation semantics. Provide an `errorBuilder` or not-found route.
- On web, call `usePathUrlStrategy()` only when clean URLs are required and hosting rewrites to `index.html`.

## Deep links

Change native files only for the platforms in scope.

- Android: `AndroidManifest.xml` intent filter with `android:autoVerify="true"` for the verified host; `/.well-known/assetlinks.json` with the release signing SHA-256 fingerprint.
- iOS: `FlutterDeepLinkingEnabled` in `Info.plist` (set `NO` if a deep-link plugin owns handling), `applinks:<host>` in entitlements, and `/.well-known/apple-app-site-association` served without an extension.
- Treat every incoming link as untrusted input: validate parameters and enforce auth after routing. Hosted files and signing fingerprints are environment configuration; use placeholders and never read signing keys.

## Verify

Add route tests for new paths, redirects, and invalid parameters. Exercise links on a device or simulator (`adb shell am start -a android.intent.action.VIEW -d <url> <package>`, `xcrun simctl openurl booted <url>`) and report any platform not tested.
