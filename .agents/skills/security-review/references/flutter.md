# Flutter Security Checks

Review the affected Dart and native paths together, including flavor-specific release configuration. Select checks by threat and data sensitivity; this is not a mandatory full-app audit.

- **Storage/privacy:** tokens and sensitive records should use suitable Keychain/Keystore-backed protection, not plain preferences, logs, caches, or unprotected databases. Check backup/export rules, screenshots/app-switcher previews, clipboard, analytics, crash breadcrumbs, and cleanup on logout/account switch where sensitive data flows.
- **Auth/payments:** verify refresh concurrency, stale sessions, logout invalidation, account boundaries, sensitive-action reauthentication, and biometric fallback. Trace payment amounts, recipient identity, replay/idempotency, and confirmation to server enforcement; hiding a button is insufficient.
- **Transport:** inspect HTTP/Dio clients, redirects, WebSockets, release ATS/network-security exceptions, cleartext traffic, and permissive certificate callbacks. Check pinning where policy requires it, including rotation/recovery; do not prescribe it blindly.
- **Platform input:** validate deep/app links, OAuth redirects/state/PKCE where applicable, push payloads, exported Android components, iOS URL handlers, and method-channel arguments. Trace authentication and authorization after routing.
- **WebViews/files:** restrict navigation, JavaScript bridges, local-file access, downloads, and external URL schemes to intended origins/actions. Validate parsed types, paths, file sizes, and upload metadata at trust boundaries.
- **Build/crypto:** bundled assets, `--dart-define`, and obfuscation cannot keep server secrets private. Inspect only safe source/config references to signing and service accounts. Check release debug flags, WebView debugging, custom crypto, randomness, key lifecycle, and affected native plugins/FFI.
- **Dependencies:** assess the actual locked SDK/plugin versions and platform exposure. Distinguish public client identifiers from privileged keys; do not label every Firebase configuration value a secret. Validate scanner claims against Flutter's documented false positives.
- **Verification:** use synthetic data and isolated test services. State which platforms/flavors were checked and which server/native controls remain unverified. No production logins, credential retrieval, or unapproved live exploitation.

Reference baseline: [OWASP MASVS](https://mas.owasp.org/MASVS/). Check [Flutter obfuscation limits](https://docs.flutter.dev/deployment/obfuscate) and [scanner false positives](https://docs.flutter.dev/reference/security-false-positives) when relevant.
