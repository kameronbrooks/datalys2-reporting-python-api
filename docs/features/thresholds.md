# Thresholds

Color chart elements by whether values pass or fail a target. Supported on
[Line](../visuals/line.md), [Area](../visuals/area.md), and clustered
[Bar](../visuals/bar.md) charts via the `threshold=` prop.

## Quick start

```python
from dl2_reports import Line, Threshold

row.add(Line("performance", x_column="Week", y_columns=["Score"],
             threshold=Threshold(value=80, mode="above",
                                 blend_width=8, apply_to="both")))
```

## `Threshold` parameters

Plain dicts with the same keys are accepted; the shape validates `mode` and
`apply_to` at construction.

| Parameter | Type | Default (viewer) | Description |
|-----------|------|------------------|-------------|
| `value` | `float` | (required) | The threshold to compare against. |
| `pass_color` | `str` | `#22c55e` (green) | Color for passing values. |
| `fail_color` | `str` | `#ef4444` (red) | Color for failing values. |
| `mode` | `str` | `'above'` | `'above'`: values ≥ threshold pass. `'below'`: values ≤ threshold pass. `'equals'`: only exact matches pass. |
| `show_line` | `bool` | `True` | Draw a reference line at the threshold value. |
| `line_style` | `str` | `'dashed'` | Reference line style: `'solid'`, `'dashed'`, `'dotted'`. |
| `blend_width` | `float` | `5` | Width of the color blend zone at crossings, as % of chart width (0–50). Line/area only. |
| `apply_to` | `str` | `'both'` | `'both'`, `'markers'` (only markers get threshold colors), or `'lines'` (only lines/areas do). |

## Per-visual behavior

| Visual | Behavior |
|--------|----------|
| **Line** | Line segments colored with gradient blending at crossings; markers colored by value. |
| **Area** | Fill *and* stroke colored with gradient blending; markers by value. |
| **Clustered bar** | Each bar colored by its own value. (Not available on stacked bars.) |

## Gradient blending (line/area)

`blend_width` controls how gradually colors transition at a crossing:

- `0` — hard edge at the crossing point
- `5` — subtle blend (default)
- `10–15` — visible, gradual fade

## Multi-series tip

With several series, full threshold coloring makes lines indistinguishable.
Use `apply_to="markers"` to keep distinct series colors and show pass/fail on
the markers only:

```python
Line("sales", x_column="Quarter",
     y_columns=["Electronics", "Clothing", "Home"],
     threshold=Threshold(value=4000, mode="above", apply_to="markers"))
```

## Related

- [Annotations](annotations.md) — a `yAxis` line is a lighter-weight target
  marker with no recoloring.
- [Gauge ranges](../visuals/gauge.md#gaugerange) — banded targets for single
  values.
- [KPI](../visuals/kpi.md) `breach_value`/`warning_value` — status coloring
  for single values.
