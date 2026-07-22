# Card (`type: "card"`)

A text card. Supports plain text, Markdown, or HTML content, plus a `{{ ... }}`
template syntax evaluated in the viewer — so card text can compute values from
your datasets at view time.

> **Class:** `dl2_reports.Card` · **Legacy helper:** `row.add_card(...)` ·
> **Example:** [03_card.py](../../examples/all_visuals/03_card.py)

## Quick start

```python
from dl2_reports import Card

page.add_row(
    Card(title="Info", text="Revenue is up 5% this week."),
    Card(title="Dataset Summary",
         text="Rows in tasksData: {{ count('tasksData') }}"),
    Card(title="Notes",
         text="**Bold** and _italic_ via markdown.",
         content_type="md"),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | `str` | Card title (supports template syntax). |
| `text` | `str` | Main content (supports template syntax). |
| `content_type` | `str` | `'text'` (viewer default), `'md'` (Markdown), or `'html'`. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

Cards do not require a dataset.

## Template syntax

`title` and `text` may contain `{{ ... }}` placeholders. Each placeholder is
evaluated **in the browser** as a JavaScript expression with these variables in
scope:

- `datasets` — the report's datasets object
- `helpers` — helper functions (also destructured for direct use, below)
- `row` *(dl2 0.4+)* — when the card is inside a modal opened via a table's
  `row_modal_id`, the clicked row's values: `{{ row.Region }}`,
  `{{ formatCurrency(row.Amount) }}`. See
  [Modals](../features/modals.md#row-detail-modals).

Helpers available directly:

| Helper | Description |
|--------|-------------|
| `count(datasetId)` | Row count. |
| `sum(datasetId, column)` / `avg` / `min` / `max` | Column aggregates (operate on `table`-format datasets). |
| `formatNumber(value, digits?)` | Number formatting. |
| `formatPercent(value, digits?)` | Percent formatting. |
| `formatCurrency(value, symbol?, digits?)` | Currency formatting. |

Whole-value expression form — use when the entire title/text is one expression:

```python
Card(title={"expr": "'Rows: ' + count('tasksData')"},
     text={"expr": "formatCurrency(sum('kpiData', 'Value'), '$', 0)"})
```

> ⚠️ **Security note:** template expressions execute arbitrary JavaScript in
> the viewer's browser. Only embed expressions in reports whose HTML/JSON you
> trust end to end.

## Notes

- Prefer Python f-strings when the value is known at build time; use
  `{{ ... }}` templates when the value must react to the viewer-side data
  (e.g. inside row modals, or over derived datasets that only exist in the
  browser).
- `content_type="md"` is the usual choice for multi-line formatted content.

## Related

- [Modals](../features/modals.md) — cards with `{{ row.* }}` templates power
  custom row detail modals.
- [KPI](kpi.md) — structured single-value display with status coloring.
