---
name: flutter-use-http-package
stack: flutter
description: Implement HTTP requests with the existing `http` package integration. Use only when `http` is already used or the user specifically requests it.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 21:36:42 GMT
---

# Use the HTTP Package

Inspect the project's API client, configuration, auth, error model, and tests before adding a request. Reuse its client lifecycle, URL construction, serialization, logging, and dependency-injection patterns.

## Request Rules

- Build endpoints with `Uri` and encode structured request bodies deliberately. Keep credentials and environment configuration out of source and logs.
- Set only headers required by the API and attach authorization through the existing auth path. Do not invent a global client or bypass shared interceptors.
- Apply an explicit timeout when the project has no central timeout policy. Translate transport failures, timeouts, malformed payloads, and non-success responses into the project's typed error/result contract.
- Accept the endpoint's documented success statuses; do not assume a single status code or return a fabricated empty model for an empty response.
- Retry only when the existing policy permits an idempotent operation and has bounded backoff. Never silently retry mutations.
- Parse large payloads off the UI isolate only when measurement or payload size justifies the overhead.

## UI Integration

Keep requests outside `build`; ensure cancellation, stale results, and disposal follow existing state-management conventions. Present loading, data, empty, error, and permission states where the feature can reach them.

Verify request construction, success mapping, and at least one meaningful failure path using the project's existing test approach.
