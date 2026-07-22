# Annotations (Visual Elements)

Overlay trend lines, reference axes, markers, and text labels on charts. In
the report JSON these live in the visual's `otherElements` array; in Python
you attach them with `.add_trend()` and `.add_element()` — both return the
visual, so calls chain.

```python
chart = row.add(Line("sales", x_column="Month", y_columns=["Revenue"]))
chart.add_element("yAxis", value=100, label="Target", color="green")
```

## Trend lines — `.add_trend(coefficients=None, **props)`

Renders a polynomial trend from coefficients. Supported on `line`, `area`,
`scatter`, `clusteredBar`, `stackedBar`, and `histogram` visuals (before
dl2 0.4.1 the viewer only rendered trends on scatter); other types raise
`ValueError`.

```python
chart = page.add_row().add_scatter("my_data", "A", "B")

chart.add_trend(color="red")                            # auto linear fit
chart.add_trend(coefficients=2, color="blue",
                line_style="dashed")                    # auto quadratic fit
chart.add_trend(coefficients=[0, 1.5], color="green")   # manual [intercept, slope, ...]
```

| `coefficients` value | Behavior |
|----------------------|----------|
| `None` | Auto-calculate a linear (degree 1) regression from the backing DataFrame. |
| `int` | Auto-calculate a polynomial fit of that degree. |
| `list[float]` | Use as-is: `[intercept, slope, quad, ...]`. |

**Auto-calculation requirements:** the visual must be in the report tree, its
dataset must have the original DataFrame, and its props must include
`x_column` and `y_column` (singular). That means histograms (binned counts)
and multi-series charts (`y_columns`) need explicit coefficients.

**Units:** on categorical X axes (line, area, bars) the viewer evaluates
coefficients against the **0-based category index**; numeric axes (scatter,
histogram) use real axis units.

## Other elements — `.add_element(type, **props)`

| Element type | Description | Key props |
|--------------|-------------|-----------|
| `xAxis` | Vertical reference line at an X value. | `value`, `color`, `label`, `line_style` |
| `yAxis` | Horizontal reference line at a Y value. | `value`, `color`, `label`, `line_style` |
| `marker` | Point marker at a value. | `value`, `size`, `shape` (`'circle'`, `'square'`, `'triangle'`), `color` |
| `label` | Text label at a value. | `value`, `label`, `font_size`, `font_weight` |

Common styling props on all elements: `color`, `line_style`
(`'solid'` / `'dashed'` / `'dotted'`), `line_width`, `label`.

```python
chart.add_element("xAxis", value="2026-01-01", label="Launch", line_style="dotted")
chart.add_element("marker", value=42, shape="triangle", size=8, color="#f59e0b")
```

`value` may be a number, date, or string, matching the axis type.

## Notes

- Elements serialize with `visualElementType` set from the first argument;
  any extra kwargs pass through to the viewer.
- `on_condition(False).add_line(...).add_trend()` chains are safe — the
  [NullComponent](conditional-layout.md) absorbs the call.
- A `yAxis` reference line just draws a line; to *recolor* the series by a
  target, use a [threshold](thresholds.md).

## Related

- [Thresholds](thresholds.md) · [Scatter](../visuals/scatter.md) (built-in
  `show_trendline`/`show_correlation`)
