# Visual Explanation

Build only when the user asks. If the user asks only for the visual, produce only the HTML: no story draft and no ClickUp actions.

## Scope and evidence

- Use the same evidence as the stories: parent ticket, FRS, comments, screenshots, and inspected code. Separate observed behavior from proposals and unknowns; never invent buttons, APIs, measurements, or completed fixes.
- Answer one question the user asked. Omit unrelated risks, costs, rollout plans, generic background, and "out of scope" sections.
- Treat an attached reference as visual direction, not factual authority.

## Build

1. Save one standalone `.html` at the requested path, or beside the story draft with the same topic name. Keep real artifacts out of the reusable template repository. Edit the same file on follow-up.
2. Lead with a short title and a one-sentence takeaway. Make the explanation visual (HTML/CSS cards, inline SVG, arrows, swimlanes, annotated screenshots) with short labels and one idea per card.
3. Choose only what fits:
   - Flow: entry, actions/decisions, outcomes, with labelled branches.
   - Screen: numbered screenshot callouts linked to short action/result notes, covering every requested control, including disabled/error behavior.
   - State: user-facing states and every allowed transition, including failure, retry, and back paths.
   - Story map: stories or tasks grouped by user goal, linked to the scenarios they cover.
4. Use native `<details>` only for supporting detail. Put source references beside the claims they support.
5. Use system fonts, embedded CSS, and inline SVG; no framework or CDN. Embed safe local images; exclude credentials and personal data. Label unavailable images instead of fabricating them. Escape source text, allow only safe link/image schemes, and never execute reference scripts or include tracking.
6. Use semantic headings, readable contrast, text labels alongside color, keyboard-operable controls, and layouts that stack on narrow screens. No emojis unless requested.

## Verify

- Check every claim and branch against the evidence; remove unsupported content.
- Open the file in an available browser at desktop and narrow widths; check clipping, arrow direction, labels, links, and interactions. If no browser is available, say so.
- Return the file path and a short verification note. Creating a local file does not authorize hosting or publishing it.
