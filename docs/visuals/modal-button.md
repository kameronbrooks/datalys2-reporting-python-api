# Modal Button (`type: "modal"`)

A dedicated button that opens a global [modal](../features/modals.md). Use it
when you want an explicit call-to-action rather than the hover "expand" icon
that `modal_id=` adds to other visuals.

> **Class:** `dl2_reports.ModalButton` · **Legacy helper:** `row.add_modal_button(...)` ·
> **Example:** [15_links_and_modals.py](../../examples/all_visuals/15_links_and_modals.py)

## Quick start

```python
from dl2_reports import ModalButton

modal = report.add_modal("revenue-details", "Revenue Breakdown")
modal.add_row().add_table("regionalRevenue", title="Regional Data")

page.add_row(
    ModalButton("revenue-details", "View Detailed Breakdown"),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `modal_id` | `str` | **Required.** Id of the global modal to open (serializes as the visual's `id`). |
| `button_label` | `str` | Button text. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## The three ways to open a modal

| Trigger | How |
|---------|-----|
| Hover expand icon | `modal_id="..."` on any visual/layout ([common prop](../features/common-props.md)). |
| Dedicated button | `ModalButton("...", "Label")` — this visual. |
| Table row double-click *(dl2 0.4+)* | `row_modal_id="..."` on a [table](table.md)/[checklist](checklist.md). |

See [Modals](../features/modals.md) for defining modal content.

## Related

- [Modals](../features/modals.md) · [Link](link.md) · [Table](table.md)
