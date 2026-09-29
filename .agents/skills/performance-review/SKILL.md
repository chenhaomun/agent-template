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

Use the shared [findings format](../production-code-review/references/findings.md) for short, plain-language issue bullets.
