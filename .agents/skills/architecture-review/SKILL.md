---
name: architecture-review
description: Review architecture/boundaries: feature placement, layering, ownership, dependency flow, public contracts, refactors, integration risk.
---

# Architecture Review

Review affected ownership boundaries using the project's established architecture.

- Trace dependencies and state/data ownership; name the consequence of a misplaced responsibility.
- Check API/model/event/route changes update consumers and preserve compatibility or define migration.
- Assess persistence, platform, permission, and release effects where relevant.
- Keep refactors scoped. Add boundaries only for current complexity or demonstrated coupling.
- Direct UI/data access is not automatically a defect; assess project conventions and behavior.

## Findings

Use the shared [findings format](../production-code-review/references/findings.md) for short, plain-language issue bullets.
