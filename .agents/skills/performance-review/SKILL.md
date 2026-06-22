---
name: performance-review
description: Review performance risks: rendering, async, data processing, caching, memory, startup, network calls, expensive loops.
---

# Performance Review

Focus on user-visible slowness, unnecessary work, and scaling risks.

## Check

| Area | Reject when |
|---|---|
| Rendering/UI | Expensive work happens in render path, or unnecessary re-renders occur |
| Lists/data | Large collections use eager/synchronous loading where lazy/paginated is needed |
| Async/IO | Network, disk, parsing, or heavy compute blocks UI or lacks timeout/cancel/error path |
| State churn | State updates are too broad, repeated, or triggered unnecessarily |
| Memory | Controllers, streams, subscriptions, caches, or listeners can leak or grow unbounded |
| Data processing | Repeated mapping/filtering/sorting/parsing should be cached, paged, streamed, or offloaded |
| Startup | Feature adds synchronous startup work or blocks first usable screen |

## Output

| Severity | Performance risk | Required action |
|---|---|---|
| P1/P2/P3 | Concrete slow path | Smallest measurable fix or verification |

Do not optimize prematurely; reject only plausible production risks.

## Examples

| Signal | Required action |
|---|---|
| Sorting/filtering large collection in render path | Precompute, memoize, move to state layer, or lazy page |
| Network call starts on every state update | Start once in lifecycle/state owner |
| Stream/subscription not disposed | Dispose or bind lifecycle to existing owner |
