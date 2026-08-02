# Bar (`type: "clusteredBar"` / `"stackedBar"`)

A bar chart of one or more series per category. One Python class covers both
variants — `stacked=` picks the compiled type: `False` → `clusteredBar`
(side-by-side), `True` → `stackedBar`.

> **Class:** `dl2_reports.Bar` · **Legacy helper:** `row.add_bar(...)` ·
> **Example:** [07_bar.py](../../examples/all_visuals/07_bar.py)

## Quick start

```python
from dl2_reports import Bar, Threshold

page.add_row(
    Bar("sales", x_column="Quarter", y_columns=["Electronics", "Clothing"],
        show_legend=True),
    Bar("sales", x_column="Quarter", y_columns=["Electronics", "Clothing"],
        stacked=True, show_legend=True),
    Bar("sales", x_column="Quarter", y_columns=["Revenue"],
        threshold=Threshold(value=5000, mode="above")),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `x_column` | `str \| int` | Column for X-axis categories. |
| `y_columns` | `list[str]` | Series columns for Y values. |
| `stacked` | `bool` | `True` → stacked bars, `False` (default) → clustered. |
| `x_axis_label` / `y_axis_label` | `str` | Axis labels. |
| `show_legend` | `bool` | Show the legend. |
| `show_labels` | `bool` | Show value labels on bars. |
| `horizontal` | `bool` | Render bars horizontally (viewer-dependent). |
| `threshold` | `Threshold \| dict` | Pass/fail bar coloring — **clustered bars only**. See [Thresholds](../features/thresholds.md). |
| `enable_export` | `bool` | *(dl2 0.5+)* Right-click **Export PNG** / **Export SVG** image export (viewer default `True`). |
| `export_file_name` | `str` | *(dl2 0.5+)* Base file name for exported images, no extension (viewer falls back to title → dataset id → chart type). |
| `context_menu` | `bool` | *(dl2 0.5+)* Right-click context menu (viewer default `True`). |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Notes

- `threshold=` colors each bar by whether its value passes; the viewer applies
  it to `clusteredBar` only (a stacked bar has no single per-bar value).
- Trend lines and other [annotations](../features/annotations.md) render on
  both variants *(dl2 0.4.1+)*; on the categorical X axis, trend coefficients
  are evaluated against the 0-based category index.
- Combine with [`aggregate=`](../features/aggregation.md) to chart grouped
  totals straight from a raw dataset (reference the aggregate's output column
  in `y_columns`, e.g. `y_columns=["sum_Amount"]`).

## Related

- [Histogram](histogram.md) — distribution of one numeric column.
- [Line](line.md) / [Area](area.md) — trends over ordered X values.
- [Chart image export](../features/chart-export.md) — PNG/SVG export details *(dl2 0.5+)*.
