---
name: flutter-fix-layout-issues
stack: flutter
description: Diagnose Flutter overflow, unbounded constraints, and ParentData errors; verify the affected layout.
---

# Fix Flutter Layout Errors

Capture the first layout exception and relevant widget/constraint tree using available runtime tools or supplied screenshots/logs. Trace constraints down and sizes up; fix the cause before cascading “RenderBox was not laid out” errors.

- **Unbounded viewport:** give the scrollable finite space or use the existing sliver/scroll owner. `Expanded` works only inside a bounded Flex axis; do not blindly add `shrinkWrap`.
- **Unbounded input width:** constrain the field within its Row, using compatible Flex or explicit bounds.
- **Flex overflow:** check available space, text wrapping, flex allocation, keyboard insets, and scrolling. Do not clip or hide required content to suppress the warning.
- **ParentData misuse:** place `Expanded/Flexible` under compatible Flex ancestry and `Positioned` under Stack ancestry, without an intervening incompatible render-object widget.

Preserve project layout intent. Verify the original screen, narrow constraints, large text, and relevant keyboard/localization states; use focused widget coverage for regressions. Hot reload where applicable and inspect the result. Report runtime checks unavailable rather than claiming visual success from analysis alone.
