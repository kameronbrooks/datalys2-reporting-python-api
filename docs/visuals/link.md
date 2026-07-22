# Link (`type: "link"`) *(dl2 0.4+)*

A navigation element: jump to any visual in the report (across pages and
tabs), or open an external URL. Renders as an inline link or a button.

> **Class:** `dl2_reports.Link` · **Legacy helper:** `row.add_link(...)` ·
> **Example:** [15_links_and_modals.py](../../examples/all_visuals/15_links_and_modals.py)

## Quick start

```python
from dl2_reports import Link

page.add_row(
    Link(target_id="sales-table", label="Jump to data", link_style="button"),
    Link(href="https://example.com/docs", label="External docs"),
)
```

## Parameters

Exactly **one** of `target_id` / `href` is required — the constructor raises
`ValueError` otherwise.

| Parameter | Type | Description |
|-----------|------|-------------|
| `target_id` | `str` | Id of a visual to navigate to. The viewer switches to the containing page, activates containing tabs (nested included), scrolls to the visual, and flashes it. |
| `href` | `str` | External URL — opens in a new tab. |
| `label` | `str` | Link text (viewer falls back to the target/href). |
| `link_style` | `str` | `'link'` (viewer default) or `'button'`. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Anchors and deep links

Every visual with an `id` is also a DOM anchor. Plain `#visual-id` hash links
navigate the same way a `Link` does — from markdown [cards](card.md), or as a
deep link in the report URL on page load:

```
report.html#sales-table
```

## Notes

- Give link targets **stable, unique ids** — duplicate ids break navigation
  (and [persistence](../features/persistent-view-state.md)); the viewer's
  validator warns about them.
- The [compile lint / viewer validation](../features/linting.md) warns when a
  `target_id` doesn't resolve to any visual.

## Related

- [Tabs](tabs.md) — links activate containing tabs automatically.
- [Modal button](modal-button.md) — open an overlay instead of navigating.
