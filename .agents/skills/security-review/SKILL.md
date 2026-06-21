---
name: security-review
description: Review code for security and privacy risks. Use for auth, permissions, secrets, storage, networking, input validation, payments, user data, logs, analytics, file access, and dependency risk.
---

# Security Review

Review threat-relevant changes only. Keep findings concrete and actionable.

## Check

| Area | Reject when |
|---|---|
| Secrets | Tokens, keys, credentials, or sensitive env values enter source, logs, reports, or UI |
| Auth/session | Missing auth check, weak expiry handling, unsafe refresh, or privilege confusion |
| Input/output | Untrusted input reaches parser, query, file, route, or shell without validation |
| Storage | Sensitive data is stored without project-approved secure storage or retention rules |
| Network | Insecure URL, weak TLS assumption, missing timeout/error handling, or token leak |
| Permissions | Platform permission added without feature need and fallback UX |
| Privacy | PII is over-collected, logged, cached, tracked, or sent to third party unnecessarily |
| Dependencies | New package/tool has unclear need, risky permissions, or unreviewed supply-chain risk |

## Output

| Severity | Risk | Required action |
|---|---|---|
| P1/P2/P3 | Concrete exploit or leak path | Smallest mitigation |

If no issue, state remaining security assumption.

## Examples

| Signal | Required action |
|---|---|
| Bearer token printed or included in report | Remove leak, rotate if real, add safe logging |
| New permission added without fallback UX | Justify feature need and add denied/restricted state |
| User input reaches file path/API query directly | Validate, encode, constrain, or reject input |
