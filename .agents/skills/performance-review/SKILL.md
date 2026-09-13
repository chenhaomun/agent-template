---
name: performance-review
description: Review performance risks: rendering, async, data processing, caching, memory, startup, network calls, expensive loops.
---

# Performance Review

Identify user-visible latency, frame work, memory growth, and scaling risks. Name the trigger, data scale, or measurement; distinguish suspected bottlenecks from measured regressions.

- Rendering: IO, repeated sorting/parsing in build, broad rebuild/listener scope, eager large lists, and unnecessary intrinsic layout.
- Images/lists: oversized image decoding, missing pagination, unstable item identity, or nested scrolling that defeats lazy construction.
- Async: repeated requests, stale results, unbounded concurrency, and startup blocking the first usable screen. Async IO alone does not require an isolate.
- Ownership: leaked controllers/subscriptions/listeners, unbounded caches, and retained large objects. Address invalidation and ownership in cache fixes.
- Compute: use isolates only when CPU cost justifies startup/copy overhead; check target support, especially web.
- Validate speedup claims with a repeatable profile-mode scenario on a representative target. Compare relevant frame time, latency, allocation, or request count; debug timing is not production evidence.

Prefer the smallest measurable fix. Do not add caching, isolates, or repaint boundaries without a plausible bottleneck and tradeoff assessment.

## Findings

Inspect actual code and affected callers. Report actionable issues supported by a concrete trigger and impact; do not turn style preferences or missing measurements into defects.

- `[P1] path/to/file.dart:42 — Trigger and impact; smallest fix.`

Use one short bullet per issue, ordered by severity (P0 critical, P1 high, P2 medium, P3 low). Use clickable file links with verified line numbers when supported; anchor to changed lines for diff reviews. Merge duplicate causes. No tables or generic praise.
If none, say “No actionable findings.” Mention material verification gaps separately; do not imply unrun checks passed.
