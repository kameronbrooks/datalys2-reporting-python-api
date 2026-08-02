# Box Plot (`type: "boxplot"`)

Distribution through quartiles — median, box (Q1–Q3), whiskers, and optional
outliers/mean. Two input modes: **data mode** (raw values, stats computed in
the browser) and **pre-calculated mode** (you supply the five-number summary).

> **Class:** `dl2_reports.Boxplot` · **Legacy helper:** `row.add_boxplot(...)` ·
> **Example:** [13_boxplot.py](../../examples/all_visuals/13_boxplot.py)

## Quick start

```python
from dl2_reports import Boxplot

# Data mode: raw values, grouped by department
page.add_row(
    Boxplot("surveyResults",
            data_column="Score",
            category_column="Department",
            color="Tableau10",
            direction="horizontal"),
)

# Pre-calculated mode: one row per box
page.add_row(
    Boxplot("stats",
            category_column="Team",
            min_column="Min", q1_column="Q1", median_column="Median",
            q3_column="Q3", max_column="Max", mean_column="Mean"),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `data_column` | `str \| int` | **Data mode.** Column of raw numeric values. |
| `category_column` | `str \| int` | Groups the data (data mode) or labels each row's box (pre-calc mode). |
| `min_column` | `str \| int` | **Pre-calc mode.** Minimum value column. |
| `q1_column` | `str \| int` | **Pre-calc mode.** First quartile column. |
| `median_column` | `str \| int` | **Pre-calc mode.** Median column. |
| `q3_column` | `str \| int` | **Pre-calc mode.** Third quartile column. |
| `max_column` | `str \| int` | **Pre-calc mode.** Maximum value column. |
| `mean_column` | `str \| int` | Optional mean value column (either mode). |
| `direction` | `str` | `'vertical'` (viewer default) or `'horizontal'`. |
| `show_outliers` | `bool` | Show outliers as rhombus shapes (data mode only, viewer default `True`). |
| `color` | `str \| list[str]` | Single color, list of colors, or D3 scheme name (`"Category10"`, `"Tableau10"`, …). Viewer default `#69b3a2`. |
| `x_axis_label` / `y_axis_label` | `str` | Axis labels. |
| `enable_export` | `bool` | *(dl2 0.5+)* Right-click **Export PNG** / **Export SVG** image export (viewer default `True`). |
| `export_file_name` | `str` | *(dl2 0.5+)* Base file name for exported images, no extension (viewer falls back to title → dataset id → chart type). |
| `context_menu` | `bool` | *(dl2 0.5+)* Right-click context menu (viewer default `True`). |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Choosing a mode

- **Data mode** (`data_column`) is simplest: embed the raw values and let the
  viewer compute quartiles and outliers. Best for datasets small enough to
  ship.
- **Pre-calculated mode** (the five `*_column` stats) keeps huge distributions
  out of the HTML — compute the summary in pandas (`df.groupby(...).quantile`)
  and embed only one row per box. Outlier display is not available in this
  mode.

## Related

- [Histogram](histogram.md) — full distribution shape of a single group.
- [Datasets & compression](../features/datasets.md) — if you do ship raw
  values, compress them.
- [Chart image export](../features/chart-export.md) — PNG/SVG export details *(dl2 0.5+)*.
