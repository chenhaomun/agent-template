---
name: figma-design-to-code
description: Implement UI from Figma with high visual fidelity via the Figma MCP/connector. Use whenever a Figma URL, node ID, frame, or design handoff is the source of truth for UI work. Enforces exact-value extraction per node (design context + variables), token mapping, asset export, and a render-vs-design screenshot compare loop.
---

# Figma Design-to-Code (High Fidelity)

One-shot design dumps plus eyeballing screenshots yields ~70% fidelity. The gap comes from guessed values, truncated context, hardcoded near-miss colors, redrawn icons, and no closing verification. This workflow removes guessing: exact values only, chunked extraction, and a mandatory compare-and-fix loop before done.

Figma MCP tool names vary by server version: design context may be `get_design_context` or `get_code`; screenshot may be `get_screenshot` or `get_image`. Use whichever this session exposes — the workflow is identical.

## Contents
- [Hard Rules](#hard-rules)
- [Workflow](#workflow)
- [Flutter Mapping](#flutter-mapping)
- [Fidelity Loss Diagnostics](#fidelity-loss-diagnostics)
- [Acceptance](#acceptance)

## Hard Rules

1. **Screenshots are for verification, never measurement.** Every number, color, and font value in code must trace to a `get_design_context`/`get_variable_defs` response for a specific node. If a value was estimated from an image, it is wrong.
2. **Never fetch one design-context dump for a whole screen.** Fetch per logical section (app bar, card, list item, footer...). Whole-screen dumps exceed output limits, get truncated, and force guessing.
3. **Map design variables to project theme tokens before coding.** Fetch variable definitions; reuse the project's theme/design-system token when one matches. Hardcode a raw value only when no token exists, and flag it in the report.
4. **Export assets; never redraw.** Icons, logos, illustrations, and images come out of Figma via asset export/download into the project's asset conventions. Hand-approximated vectors are a top fidelity killer.
5. **Reuse existing components first.** Check Code Connect mappings (`get_code_connect_map`) and the project's widget/component library before writing new UI. Design-system consistency beats freshly coded lookalikes; if the design conflicts with an existing component, flag it instead of forking silently.
6. **Not done until verified.** The rendered UI must be screenshot-compared against the Figma reference, and a full pass must find zero deviations — or each remaining deviation is explicitly reported with a reason.

## Workflow

### Task Progress
- [ ] **Scope.** Confirm target frame/node IDs, the frame's dimensions, which screens/components are in scope, and where the code lives. Locate the project's theme, tokens, and reusable components.
- [ ] **Reference screenshot.** `get_screenshot` for each target frame. This is the ground truth for the final compare, not a data source.
- [ ] **Structure.** `get_metadata` for the node tree. Enumerate logical sections and their node IDs. Plan one extraction pass per section.
- [ ] **Extract per section.** For each section node, `get_design_context` and record exact values: layout mode/direction, padding (top/right/bottom/left), item gap, per-child sizing (fixed/hug/fill), width/height, fills, strokes (color + weight), per-corner radius, effects (shadow color/blur/spread/offset), typography (family, weight, size, line-height, letter-spacing, case, color), opacity, z-order.
- [ ] **Tokens.** `get_variable_defs` for the frame. Build a mapping table: Figma variable → project theme token → raw fallback. Resolve every color/spacing/text style through this table.
- [ ] **Assets.** Export every icon/image/illustration the sections need into project asset conventions. Record the mapping.
- [ ] **Spec before code.** Assemble the recorded values into a per-section fidelity spec. Any value still missing: re-fetch that specific node — do not guess, do not proceed without it.
- [ ] **Implement** from the spec, smallest components first. Use theme tokens and existing components per the mapping tables. Respect the design's constraints/responsive rules; don't bake in absolute frame offsets outside genuine Stack/overlay cases.
- [ ] **Compare loop.** Run the app at the design frame's dimensions and screenshot it. Compare side-by-side against the Figma reference in this order: structure → spacing → sizing → typography → color → radius/borders/shadows → assets. Fix every deviation, re-render, repeat. A pass with fixes is never the last pass; finish with one clean pass.
- [ ] **States.** After visual parity: cover loading, empty, error, disabled, and permission states per `AGENTS.md` (the design usually shows only the success state).

## Flutter Mapping

Translate extracted Figma values structurally — not by visual approximation:

| Figma | Flutter |
|---|---|
| Auto layout vertical / horizontal | `Column` / `Row` (`spacing:` for item gap, or `SizedBox` gaps) |
| Padding | `Padding` with exact `EdgeInsets.fromLTRB(...)` |
| Hug contents | `MainAxisSize.min` |
| Fill container | `Expanded` / `CrossAxisAlignment.stretch` |
| Fixed size | `SizedBox` with exact dimensions |
| Absolute position | `Stack` + `Positioned` |
| Corner radius (per corner) | `BorderRadius.only(...)` |
| Stroke | `Border.all(color, width)` / `BorderSide` |
| Drop shadow | `BoxShadow(color, blurRadius, spreadRadius, offset)` |
| Text style | `TextStyle` — set `height: lineHeight / fontSize` and `letterSpacing` explicitly; both default wrong if omitted |
| Fill color / gradient | Theme token first; `LinearGradient` with exact stops |
| Opacity | `Opacity` / color alpha per extracted value |
| Image fill mode | Exported asset + `BoxFit` matching the fill mode |

For other stacks the same table applies conceptually (auto layout → flex, gap → gap, hug → fit-content, fill → flex-grow).

## Fidelity Loss Diagnostics

| Symptom | Usual cause | Fix |
|---|---|---|
| Spacing slightly off everywhere | Values estimated from screenshot | Re-fetch design context per node; use exact padding/gap |
| Colors close but wrong | Variables not fetched; hex eyeballed | `get_variable_defs`; map to theme tokens |
| Text feels different despite same font | Line-height/letter-spacing left default | Set `height` and `letterSpacing` from extracted values |
| Icons/illustrations look redrawn | They were | Export the real assets |
| Section layout collapses at other sizes | Hug/fill/fixed mis-mapped | Re-check sizing mode per child in design context |
| Whole screen "roughly right, nothing exact" | One whole-screen dump, truncated | Redo extraction per section |
| Duplicated near-identical component | Existing component not reused | Check Code Connect map and component library first |

## Acceptance

- Every fidelity-spec value traces to an extracted design-context/variable value.
- Final compare pass at design dimensions is clean.
- Remaining deviations (e.g. platform font metrics) are listed with reasons — never silently shipped.
- Report: sections implemented, token mappings used, assets exported, compare passes run, flagged conflicts with the existing design system.
