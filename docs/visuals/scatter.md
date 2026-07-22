# Scatter Plot (`type: "scatter"`)

Individual points at numeric X/Y coordinates, with optional category coloring,
a linear regression trendline, and correlation statistics.

> **Class:** `dl2_reports.Scatter` · **Legacy helper:** `row.add_scatter(...)` ·
> **Example:** [10_scatter.py](../../examples/all_visuals/10_scatter.py)

## Quick start

```python
from dl2_reports import Scatter

page.add_row(
    Scatter("measurements",
            x_column="Height", y_column="Weight",
            category_column="Species",
            show_trendline=True, show_correlation=True),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `x_column` | `str \| int` | Column for numeric X values. |
| `y_column` | `str \| int` | Column for numeric Y values (singular — one series of points). |
| `category_column` | `str \| int` | Optional column for coloring points by category. |
| `show_trendline` | `bool` | Show a linear regression trendline. |
| `show_correlation` | `bool` | Show correlation stats (r, r², equation). |
| `point_size` | `int` | Point size (viewer default 5). |
| `x_axis_label` / `y_axis_label` | `str` | Axis labels. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Notes

- Unlike line/area/bar, scatter takes a singular `y_column`; use
  `category_column` to distinguish groups rather than multiple Y columns.
- `show_trendline=True` is the built-in viewer-side regression. For custom
  trend styling or polynomial fits, use `.add_trend()` instead — scatter's
  numeric axes evaluate coefficients in **real axis units**, and
  auto-calculation works here because the visual has both `x_column` and
  `y_column`:

  ```python
  chart = row.add(Scatter("data", x_column="A", y_column="B"))
  chart.add_trend(color="red")                          # auto linear fit
  chart.add_trend(coefficients=2, line_style="dashed")  # auto quadratic fit
  ```

  See [Annotations](../features/annotations.md).

## Related

- [Line](line.md) — ordered X values / time series.
- [Heatmap](heatmap.md) — density over two categorical axes.
