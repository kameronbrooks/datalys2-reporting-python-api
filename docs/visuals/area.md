# Area Chart (`type: "area"`)

A line chart with the region below each line filled. Supports everything the
[line chart](line.md) does, plus fill opacity and line/marker toggles.

> **Class:** `dl2_reports.Area` · **Legacy helper:** `row.add_area(...)` ·
> **Example:** [09_area.py](../../examples/all_visuals/09_area.py)

## Quick start

```python
from dl2_reports import Area, Threshold

page.add_row(
    Area("temps", x_column="Date", y_columns=["Temperature"],
         smooth=True, fill_opacity=0.4, show_markers=True,
         threshold=Threshold(value=75, mode="below", apply_to="both")),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `x_column` | `str \| int` | Column for X values. |
| `y_columns` | `str \| list[str]` | Column(s) for Y series. |
| `smooth` | `bool` | Smooth curves instead of straight segments. |
| `show_line` | `bool` | Line stroke on top of the fill (viewer default `True`). |
| `show_markers` | `bool` | Interactive marker points (viewer default `True`). |
| `fill_opacity` | `float` | Fill opacity 0–1 (viewer default 0.3). |
| `show_legend` | `bool` | Show the legend. |
| `show_labels` | `bool` | Show value labels on points. |
| `min_y` / `max_y` | `float` | Y-axis bounds (otherwise auto). |
| `colors` | `list[str]` | Series colors. |
| `threshold` | `Threshold \| dict` | Pass/fail coloring of areas, lines, and markers — see [Thresholds](../features/thresholds.md). |
| `x_axis_label` / `y_axis_label` | `str` | Axis labels. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Notes

- Multiple series overlap (they are **not** stacked); keep `fill_opacity` low
  when charting more than one series.
- Threshold coloring applies to the fill *and* the stroke, with gradient
  blending at crossings (`blend_width`).

## Related

- [Line](line.md) — the same chart without fill.
- [Thresholds](../features/thresholds.md) · [Annotations](../features/annotations.md).
