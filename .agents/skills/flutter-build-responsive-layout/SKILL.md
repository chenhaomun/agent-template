---
name: flutter-build-responsive-layout
stack: flutter
description: Adapt layouts across screen sizes with `LayoutBuilder`, `MediaQuery`, `Expanded`/`Flexible`.
metadata:
  model: models/gemini-3.1-pro-preview
  last_modified: Tue, 21 Apr 2026 20:17:40 GMT
---

# Responsive Flutter Layouts

Preserve product behavior, existing components, breakpoints, and supported targets.

- Use LayoutBuilder for local parent constraints; focused MediaQuery accessors for window size, text scaling, padding, and insets as needed.
- Choose layout by available space rather than device labels or orientation alone.
- Use Expanded/Flexible only with compatible Flex parents and bounded constraints. Give scrollables a deliberate scroll owner; do not use shrinkWrap to mask an unbounded layout on large data.
- Keep large collections lazy. Constrain readable form/text widths on wide windows; change list/grid or navigation patterns only when product intent supports it.
- Preserve state and focus across resizing. Account for safe areas, keyboard, long localized labels, text scaling, and keyboard/pointer interaction where supported.
- Verify narrow/wide constraints and relevant boundary widths; inspect overflow, clipped content, and unreachable controls with existing widget tests or a runtime comparison proportionate to risk.
