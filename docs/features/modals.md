# Modals

Modals are overlay dialogs with their own rows of layouts and visuals —
drill-down detail without leaving the page. They are defined globally on the
report and triggered from visuals.

## Defining a modal

`report.add_modal(id, title, description=None)` returns a `Modal`; build its
content with `add_row()` exactly like a page:

```python
modal = report.add_modal("revenue-details", "Revenue Breakdown",
                         description="Detailed view of revenue by region.")
modal.add_row().add_table("regionalRevenue", title="Regional Data")
```

## Triggering a modal

### 1. Expand icon — `modal_id=` on any element

Any visual or layout accepts `modal_id` (a [common prop](common-props.md)).
Hovering the element shows an expand icon in the top-right corner; clicking
it opens the modal:

```python
page.add_row().add_kpi("kpiData", "Revenue", title="Total Revenue",
                       modal_id="revenue-details")
```

### 2. Dedicated button — [`ModalButton`](../visuals/modal-button.md)

```python
from dl2_reports import ModalButton
page.add_row(ModalButton("revenue-details", "View Detailed Breakdown"))
```

### 3. Table rows *(dl2 0.4+)* — `row_modal` / `row_modal_id`

Double-clicking a [table](../visuals/table.md) or
[checklist](../visuals/checklist.md) row (or right-click → *Open details*)
opens a detail modal. [Calendar](../visuals/calendar.md) events *(dl2 0.5+)*
use the same API — double-click an event.

## Row detail modals

Two flavors:

**Built-in** — `row_modal=True` renders a simple field list; customize with
`row_modal_columns` and `row_modal_title`:

```python
row.add_table("orders", row_modal=True,
              row_modal_columns=["Region", "Rep", "Amount"],
              row_modal_title="Order")
```

**Custom** — `row_modal_id="..."` opens one of your global modals instead.
[Cards](../visuals/card.md) inside it can reference the clicked row through
`{{ row.ColumnName }}` templates:

```python
row.add_table("orders", row_modal_id="order-detail")

modal = report.add_modal("order-detail", "Order Details")
modal.add_row().add_card(
    title="Order — {{ row.Region }}",
    text="**Rep:** {{ row.Rep }}\n**Amount:** {{ formatCurrency(row.Amount) }}",
    content_type="md",
)
```

[Column formats](column-formatting.md) apply inside row detail modals too.

## Notes

- Modal `id`s must be unique; the [viewer validator](linting.md) warns about
  unknown `modalId` / `rowModalId` references.
- Modals are global — several visuals can trigger the same modal.
- A modal's rows support everything a page's rows do: layouts, tabs, charts,
  tables.

## Related

- [Modal button](../visuals/modal-button.md) · [Card templates](../visuals/card.md#template-syntax) ·
  [Table](../visuals/table.md) · [Link](../visuals/link.md) (navigation instead of overlay)
