# KPI (`type: "kpi"`)

A KPI card: one headline value read from a dataset row, with optional
comparison value, formatting, and breach/warning status coloring.

> **Class:** `dl2_reports.KPI` · **Legacy helper:** `row.add_kpi(...)` ·
> **Example:** [02_kpi.py](../../examples/all_visuals/02_kpi.py)

## Quick start

```python
from dl2_reports import KPI

page.add_row(
    KPI("kpiData",
        value_column="Revenue",
        title="Total Revenue",
        format="currency",
        comparison_column="Revenue",
        comparison_row_index=-2,
        comparison_text="vs. last month"),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `value_column` | `str \| int` | Column for the main KPI value. |
| `title` | `str` | Card title. |
| `comparison_column` | `str \| int` | Column for the comparison value. |
| `comparison_row_index` | `int` | Row index for the comparison (negative indices count from the end). Defaults to the same row as `row_index`. |
| `comparison_text` | `str` | Text shown beside the comparison value, e.g. `"Last Month"`, `"Yesterday"`. |
| `row_index` | `int` | Row index to display (viewer default 0; negative indices ok). |
| `format` | `str` | `'number'`, `'currency'`, `'percent'`, `'date'`, or `'hms'`. |
| `rounding_precision` | `int` | Rounding precision for numeric values. |
| `currency_symbol` | `str` | Currency symbol (viewer default `'$'`). |
| `good_direction` | `str` | Which direction is "good": `'higher'` or `'lower'`. Controls comparison arrow coloring. |
| `breach_value` | `float` | Value that triggers a breach indicator. |
| `warning_value` | `float` | Value that triggers a warning indicator. |
| `description` | `str` | Description text displayed at the bottom of the card. |
| `width` / `height` | `int` | Optional fixed card size in px. |
| `extra` | `dict` | [Passthrough props](generic-visual.md) not modeled by this class. |
| `**common` | | [Common visual properties](../features/common-props.md) (`id`, `border`, `modal_id`, `filter`, …). |

## Notes

- `row_index` defaults to the first row; use `-1` to always show the latest
  row of a time-ordered dataset.
- `breach_value` / `warning_value` combine with `good_direction` to color the
  card status — e.g. `good_direction="higher", warning_value=90,
  breach_value=80` flags values dipping below those levels.
- A KPI shows **one** row's value. To display an aggregate (e.g. a grand
  total), either compute it in pandas before `add_df`, or attach an
  [`aggregate=`](../features/aggregation.md) /
  [derived dataset](../features/derived-datasets.md) that produces a
  single-row dataset.
- `kpi.get_value()` reads the value back into Python at build time — see
  [Reading values](../features/reading-values.md).

## Related

- [Gauge](gauge.md) — the same "single value" idea as a dial with ranges.
- [Card](card.md) — free-form text with computed `{{ ... }}` templates.
- [Modals](../features/modals.md) — `modal_id=` adds an expand icon that opens
  a drill-down overlay.
