# Histogram (`type: "histogram"`)

The distribution of one numeric column, binned into equal-width bars.

> **Class:** `dl2_reports.Histogram` · **Legacy helper:** `row.add_histogram(...)` ·
> **Example:** [11_histogram.py](../../examples/all_visuals/11_histogram.py)

## Quick start

```python
from dl2_reports import Histogram

page.add_row(
    Histogram("survey", column="Score", bins=20,
              show_labels=True, x_axis_label="Score", y_axis_label="Count"),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `column` | `str \| int` | Numeric column to bin. |
| `bins` | `int` | Number of bins (viewer default 10). |
| `color` | `str` | Bar color (viewer default `#69b3a2`). |
| `show_labels` | `bool` | Show count labels on top of bars. |
| `x_axis_label` / `y_axis_label` | `str` | Axis labels. |
| `enable_export` | `bool` | *(dl2 0.5+)* Right-click **Export PNG** / **Export SVG** image export (viewer default `True`). |
| `export_file_name` | `str` | *(dl2 0.5+)* Base file name for exported images, no extension (viewer falls back to title → dataset id → chart type). |
| `context_menu` | `bool` | *(dl2 0.5+)* Right-click context menu (viewer default `True`). |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Notes

- Binning happens in the browser from the raw values — no need to pre-bucket
  in pandas.
- Trend annotations render on histograms *(dl2 0.4.1+)* in real axis units,
  but `.add_trend()` **cannot auto-calculate** here (the Y values are binned
  counts, not a column) — pass explicit `coefficients`. See
  [Annotations](../features/annotations.md).
- Use a [`filter=`](../features/filtering.md) or formula datasource
  (`Histogram("survey[Score > 0]", column="Score")`) to exclude outliers or
  sentinel values before binning.

## Related

- [Box plot](boxplot.md) — quartile summary, better for comparing groups.
- [Bar](bar.md) — categorical counts you computed yourself.
- [Chart image export](../features/chart-export.md) — PNG/SVG export details *(dl2 0.5+)*.
