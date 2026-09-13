---
name: security-review
description: Review security/privacy risks: auth, permissions, secrets, storage, networking, input validation, payments, user data, logs, dependencies.
---

# Security Review

Review threat-relevant changes and trace untrusted data to sensitive operations.

- Check authorization, session expiry/refresh, and permissions at the enforcement point.
- Check secrets and personal data in storage, logs, URLs, reports, and outbound requests.
- Check input validation appropriate to parsers, queries, routes, files, and shell execution.
- Assess transport security, denied-permission behavior, retention, and dependency exposure where affected.
- Describe the exploit/leak path and smallest mitigation. Separate unknown trust assumptions from proven vulnerabilities.

## Findings

Inspect actual code and affected callers. Report actionable issues supported by a concrete trigger and impact; do not turn style preferences or missing measurements into defects.

- `[P1] path/to/file.dart:42 — Trigger and impact; smallest fix.`

Use one short bullet per issue, ordered by severity (P0 critical, P1 high, P2 medium, P3 low). Use clickable file links with verified line numbers when supported; anchor to changed lines for diff reviews. Merge duplicate causes. No tables or generic praise.
If none, say “No actionable findings.” Mention material verification gaps separately; do not imply unrun checks passed.
