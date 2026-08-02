# Printing & PDF *(dl2 0.5+)*

Printing a report (Ctrl+P, or headless `page.pdf()`) renders the **entire**
report onto paper — no configuration needed, from the Python side or the JSON
config. It is a viewer feature; nothing in this package changes what you emit.

What the viewer does in print mode:

- Every page renders in sequence, and every tab of a `tabs` visual is
  flattened into titled sections.
- Tables and checklists are unpaginated with groups expanded; table headers
  repeat across sheets.
- Calendars release their `max_events_per_day` "+N more" clamps.
- Scroll containers (`max_height`) and clipping are released; interactive
  chrome is hidden; page breaks avoid splitting visuals.
- The light palette is pinned (dark text on white paper) and status colors
  survive via `print-color-adjust`.

Existing props simply behave differently on paper — e.g. `page_size` and
`max_height` stop limiting what is visible. If a report is destined for PDF,
prefer content that reads well linearly (titles on visuals, modest table
widths).

## Related

- [Chart image export](chart-export.md) — exporting a single chart as PNG/SVG.
- [Calendar](../visuals/calendar.md) — clamp behavior when printed.
