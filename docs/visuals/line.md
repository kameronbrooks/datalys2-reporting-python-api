# Line Chart (`type: "line"`)

Data points connected by straight or smoothed lines — the default choice for
values over time or any ordered X axis. Supports multiple series, Y-axis
bounds, threshold coloring, and annotations.

> **Class:** `dl2_reports.Line` · **Legacy helper:** `row.add_line(...)` ·
> **Example:** [08_line.py](../../examples/all_visuals/08_line.py)

## Quick start

```python
from dl2_reports import Line, Threshold

page.add_row(
    Line("sales", x_column="Month", y_columns=["Revenue", "Costs"],
         smooth=True, show_legend=True),
    Line("sales", x_column="Month", y_columns=["Revenue"],
         threshold=Threshold(value=5000, mode="above", blend_width=8)),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `x_column` | `str \| int` | Column for X values (time or category). |
| `y_columns` | `str \| list[str]` | Column(s) for Y series. |
| `smooth` | `bool` | Smooth curves instead of straight segments. |
| `show_legend` | `bool` | Show the legend. |
| `show_labels` | `bool` | Show value labels on points. |
| `min_y` / `max_y` | `float` | Y-axis bounds (otherwise auto). |
| `colors` | `list[str]` | Series colors. |
| `threshold` | `Threshold \| dict` | Pass/fail coloring with gradient blending — see [Thresholds](../features/thresholds.md). |
| `x_axis_label` / `y_axis_label` | `str` | Axis labels. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Notes

- Date columns added via `add_df` are serialized with a `date` dtype, so the
  X axis and tooltips are date-aware — see
  [Datasets](../features/datasets.md#dates).
- With a threshold on a multi-series chart, `apply_to="markers"` keeps
  distinct line colors and shows pass/fail only on the markers.
- `.add_trend()` auto-computes a regression from the backing DataFrame for
  single-series charts using `x_column`/`y_column` props — multi-series
  (`y_columns`) charts need explicit coefficients. See
  [Annotations](../features/annotations.md).

## Related

- [Area](area.md) — same features plus fill.
- [Scatter](scatter.md) — unordered numeric X/Y with regression stats.
- [Thresholds](../features/thresholds.md) · [Annotations](../features/annotations.md).
