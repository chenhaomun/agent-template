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

Use the shared [findings format](../production-code-review/references/findings.md) for short, plain-language issue bullets.
