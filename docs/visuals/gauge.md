# Gauge (`type: "gauge"`)

A speedometer-style dial with an animated needle, optional colored range
bands, a center value readout, and a legend. The needle animates from 0 to the
target value on first render; hovering arc segments shows range tooltips.

> **Class:** `dl2_reports.Gauge` · **Legacy helper:** `row.add_gauge(...)` ·
> **Example:** [14_gauge.py](../../examples/all_visuals/14_gauge.py)

## Quick start

```python
from dl2_reports import Gauge, GaugeRange

page.add_row(
    Gauge("scoreData", value_column="Score",
          title="Performance Score", min_value=0, max_value=100, unit="pts"),

    Gauge("csatData", value_column="CSAT",
          title="Customer Satisfaction", min_value=0, max_value=100, unit="%",
          show_legend=True,
          ranges=[
              GaugeRange(0, 50, color="#e74c3c", label="Poor"),
              GaugeRange(50, 75, color="#f39c12", label="Average"),
              GaugeRange(75, 100, color="#27ae60", label="Good"),
          ]),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `value_column` | `str \| int` | Column containing the gauge value (default `0`, i.e. the first column). |
| `row_index` | `int` | Row to read the value from (viewer default 0). |
| `min_value` / `max_value` | `float` | Gauge scale bounds (viewer defaults 0 / 100). |
| `title` | `str` | Title displayed above the gauge. |
| `thickness` | `int` | Arc thickness in px (viewer default 24). |
| `start_angle` / `end_angle` | `float` | Arc angles in radians (viewer defaults −π/2 / π/2, i.e. a half circle). |
| `ranges` | `list[GaugeRange \| dict]` | Colored range bands (see below). |
| `track_color` | `str` | Background track color when no ranges are defined. |
| `value_color` | `str` | Value-arc color when no ranges are defined. |
| `needle_color` | `str` | Needle color (viewer default: the theme text color). |
| `show_needle` | `bool` | Show the needle (viewer default `True`). |
| `show_value` | `bool` | Show the center value (viewer default `True`). |
| `show_min_max` | `bool` | Show min/max labels (viewer default `True`). |
| `show_legend` | `bool` | Show a legend for the ranges (viewer default `False`). |
| `format` | `str` | Value format: `'number'`, `'currency'`, or `'percent'`. |
| `rounding_precision` | `int` | Decimal precision for the value (viewer default 1). |
| `currency_symbol` | `str` | Currency symbol when `format='currency'` (viewer default `'$'`). |
| `unit` | `str` | Unit text displayed below the value. |
| `colors` | `str \| list[str]` | Color palette for ranges (D3 scheme name or list) — used when ranges omit explicit colors. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## `GaugeRange`

```python
from dl2_reports import GaugeRange

GaugeRange(from_=75, to=100, color="#27ae60", label="Good", show_plus=False)
```

| Field | Type | Description |
|-------|------|-------------|
| `from_` | `float` | Start value (serializes as `from` — trailing underscore because `from` is a Python keyword). |
| `to` | `float` | End value. |
| `color` | `str` | Color for this segment (falls back to the gauge's `colors` palette). |
| `label` | `str` | Label shown in the legend and tooltip. |
| `show_plus` | `bool` | Display the range as `"{from}+"` instead of `"{from} – {to}"` in legend/tooltip. |

Plain dicts (`{"from": 0, "to": 50, ...}`) are accepted too.

## Notes

- Like a [KPI](kpi.md), a gauge reads **one** cell (`value_column` ×
  `row_index`).
- A subtle background appears behind the value text when the needle would
  overlap it.
- Full-circle or asymmetric arcs are possible via `start_angle`/`end_angle`
  (radians).

## Related

- [KPI](kpi.md) — the flat-card equivalent with comparisons.
- [Thresholds](../features/thresholds.md) — pass/fail coloring on charts
  (gauges use `ranges` instead).
