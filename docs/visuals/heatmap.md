# Heatmap (`type: "heatmap"`)

A matrix of X × Y categories where each cell's color encodes a value.

> **Class:** `dl2_reports.Heatmap` · **Legacy helper:** `row.add_heatmap(...)` ·
> **Example:** [12_heatmap.py](../../examples/all_visuals/12_heatmap.py)

## Quick start

```python
from dl2_reports import Heatmap

page.add_row(
    Heatmap("salesMatrix",
            x_column="Month", y_column="Region", value_column="Sales",
            color="Viridis", show_cell_labels=True),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `x_column` | `str \| int` | Column for X-axis categories. |
| `y_column` | `str \| int` | Column for Y-axis categories. |
| `value_column` | `str \| int` | Column for the heat value. |
| `show_cell_labels` | `bool` | Show the value text inside cells. |
| `min_value` / `max_value` | `float` | Color-scale bounds (otherwise derived from the data). |
| `color` | `str \| list[str]` | D3 interpolator name (`"Viridis"`, `"Magma"`, `"YlOrRd"`, …) or a list of colors for custom interpolation. |
| `x_axis_label` / `y_axis_label` | `str` | Axis labels. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Notes

- The dataset should be **long-form**: one row per (x, y) cell with its value —
  the same shape `df.melt()` produces — not a pivoted matrix.
- Pin `min_value`/`max_value` when comparing several heatmaps so their color
  scales match.
- A custom color list interpolates between your colors, e.g.
  `color=["#ffffff", "#ff0000"]` for white→red.

## Related

- [Table](table.md) with [conditional formatting](../features/conditional-formatting.md)
  — when exact values matter more than the overview.
- [Aggregation](../features/aggregation.md) — build the (x, y, value) rows
  client-side from raw data.
