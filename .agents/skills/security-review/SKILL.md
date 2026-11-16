---
name: security-review
description: Review security and privacy risks, including Flutter storage, auth, transport, native integrations, and release configuration.
---

# Security Review

Follow `SECURITY.md` before inspection. Trace untrusted inputs to sensitive operations in the affected code; inspect source and sanitized fixtures, never credentials.

- Verify authorization at the enforcement point, session expiry/refresh, least privilege, validation, and payment/replay protections. Client-side checks cannot prove server authorization.
- Trace sensitive data through storage, logs, URLs, analytics, crash reports, backups, and outbound requests; check retention and deletion.
- For Flutter/mobile changes, use [mobile checks](references/flutter.md), selecting only affected attack surfaces.
- Check dependency advisories against pinned versions and reachable code. Use current primary sources for uncertain platform/security claims; do not turn scanner output into findings without validation.
- Report the exploit/leak path, conditions, impact, and smallest mitigation. Separate unknown trust assumptions and untested controls from proven vulnerabilities.

Follow [shared review guidance](../production-code-review/references/findings.md) for CI reuse and concise `file:line` findings.
