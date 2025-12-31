# Datalys2 Reporting Python API
**Version 0.2.2**

A Python library to build and compile interactive HTML reports using the Datalys2 Reporting framework.

**Note:** Compatible with dl2 version 0.2.2
https://github.com/kameronbrooks/datalys2-reporting

## Installation

```bash
pip install dl2-reports
```

## Quick Start

```python
import pandas as pd
from dl2_reports import DL2Report

# Create a report
report = DL2Report(title="My Report")

# Add data
df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
report.add_df("my_data", df, compress=True)

# Add a page and visual
page = report.add_page("Overview")
page.add_row().add_kpi("my_data", value_column="A", title="Metric A")

# Save to HTML or show in Jupyter
report.save("report.html")
report.show()
```

## Features

### Jupyter Notebook Support

You can render reports directly inside Jupyter Notebooks (including VS Code and JupyterLab).

*   **`report.show(height=800)`**: Displays the report in an iframe.
*   **Automatic Rendering**: Simply placing the `report` object at the end of a cell will render it automatically.

**Requirements:**
*   `IPython` must be installed in your environment.

## Available Visuals

All visuals are added to a layout row using `row.add_<type>(...)`.

### Common Visual Keyword Arguments

All `Layout.add_*` visual helpers accept `**kwargs` which are passed through to the viewer as visual properties.


Common properties supported by the viewer include:

- `padding`: number (px)
- `margin`: number (px)
- `border`: bool or CSS border string
- `shadow`: bool or CSS box-shadow string
- `flex`: number (flex grow)
- `modal_id`: string (global modal id opened via the expand icon)

The Python API accepts these in `snake_case`; the compiled report JSON uses `camelCase`.

### Layout Visual Helper APIs

Below are the current convenience helpers available on `Layout` (rows are layouts).

### Visual Types (Quick Summary)

These are the visual types you can add via the `Layout` helpers:

- `kpi` (via `add_kpi`)
- `table` (via `add_table`)
- `card` (via `add_card`)
- `pie` (via `add_pie`)
- `clusteredBar` / `stackedBar` (via `add_bar(stacked=...)`)
- `scatter` (via `add_scatter`)
- `line` (via `add_line`)
- `checklist` (via `add_checklist`)
- `histogram` (via `add_histogram`)
- `heatmap` (via `add_heatmap`)
- `boxplot` (via `add_boxplot`)
- `modal` (via `add_modal_button`)

You can also add any viewer-supported visual type directly using `add_visual(type=..., ...)`.

#### Generic Visual

Use this when you want to pass through viewer props that don't have a dedicated helper yet.

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `type` | `str` | (required) | Visual type (e.g., `'kpi'`, `'table'`, `'line'`, `'scatter'`). |
| `dataset_id` | `str \| None` | `None` | Dataset id to bind to this visual (required for most chart/data visuals). |
| `**kwargs` | `Any` | — | Additional visual properties (serialized to JSON). Common ones include `padding`, `margin`, `border`, `shadow`, `flex`, `modal_id`. |

#### KPI

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `value_column` | `str \| int` | (required) | Column for the main KPI value. |
| `title` | `str \| None` | `None` | Optional KPI card title. |
| `comparison_column` | `str \| int \| None` | `None` | Column for the comparison value. |
| `comparison_row_index` | `int \| None` | `None` | Row index to use for comparison (supports negative indices). If not provided, the viewer uses the same row as `row_index`. |
| `row_index` | `int \| None` | `None` | Row index to display (supports negative indices). |
| `format` | `str \| None` | `None` | `'number'`, `'currency'`, `'percent'`, or `'date'`. |
| `currency_symbol` | `str \| None` | `None` | Currency symbol (viewer default is usually `'$'`). |
| `good_direction` | `str \| None` | `None` | Which direction is “good” (`'higher'` or `'lower'`). |
| `breach_value` | `float \| int \| None` | `None` | Value that triggers a breach indicator. |
| `warning_value` | `float \| int \| None` | `None` | Value that triggers a warning indicator. |
| `description` | `str \| None` | `None` | Optional description text. |
| `width` | `int \| None` | `None` | Optional width. |
| `height` | `int \| None` | `None` | Optional height. |
| `**kwargs` | `Any` | — | Additional common visual properties (e.g., `modal_id`, padding/margins, etc.). |

#### Table

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `title` | `str \| None` | `None` | Optional table title. |
| `columns` | `list[str] \| None` | `None` | Optional list of columns to display. |
| `page_size` | `int \| None` | `None` | Rows per page. |
| `table_style` | `str \| None` | `None` | `'plain'`, `'bordered'`, or `'alternating'`. |
| `show_search` | `bool \| None` | `None` | Whether to show the search box. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Card

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `title` | `str \| None` | (required) | Optional title (supports template syntax in the viewer). |
| `text` | `str` | (required) | Main card text (supports template syntax in the viewer). |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Pie / Donut

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `category_column` | `str \| int` | (required) | Column for slice labels. |
| `value_column` | `str \| int` | (required) | Column for slice values. |
| `inner_radius` | `int \| None` | `None` | Inner radius for donut styling. |
| `show_legend` | `bool \| None` | `None` | Whether to show the legend. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Bar (Clustered / Stacked)

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `x_column` | `str \| int` | (required) | Column for X-axis categories. |
| `y_columns` | `list[str]` | (required) | Series columns for Y values. |
| `stacked` | `bool` | `False` | If `True`, uses stacked bars; otherwise clustered. |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `show_legend` | `bool \| None` | `None` | Whether to show the legend. |
| `show_labels` | `bool \| None` | `None` | Whether to show value labels. |
| `horizontal` | `bool \| None` | `None` | Whether to render bars horizontally (viewer-dependent). |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Scatter

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `x_column` | `str \| int` | (required) | Column for numeric X values. |
| `y_column` | `str \| int` | (required) | Column for numeric Y values. |
| `category_column` | `str \| int \| None` | `None` | Optional column for coloring points by category. |
| `show_trendline` | `bool \| None` | `None` | Whether to show a trendline. |
| `show_correlation` | `bool \| None` | `None` | Whether to show correlation stats. |
| `point_size` | `int \| None` | `None` | Point size. |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Line

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `x_column` | `str \| int` | (required) | Column for X values (time or category). |
| `y_columns` | `list[str] \| str` | (required) | Column(s) for Y series. |
| `smooth` | `bool \| None` | `None` | Whether to render smooth curves. |
| `show_legend` | `bool \| None` | `None` | Whether to show the legend. |
| `show_labels` | `bool \| None` | `None` | Whether to show value labels. |
| `min_y` | `float \| int \| None` | `None` | Optional minimum Y. |
| `max_y` | `float \| int \| None` | `None` | Optional maximum Y. |
| `colors` | `list[str] \| None` | `None` | Optional list of series colors. |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Checklist

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `status_column` | `str` | (required) | Column containing a truthy completion value. |
| `warning_column` | `str \| None` | `None` | Optional date column to evaluate for warnings. |
| `warning_threshold` | `int \| None` | `None` | Days before due date to trigger warning. |
| `columns` | `list[str] \| None` | `None` | Optional subset of columns to display. |
| `page_size` | `int \| None` | `None` | Rows per page. |
| `show_search` | `bool \| None` | `None` | Whether to show the search box. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Histogram

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `column` | `str \| int` | (required) | Numeric column to bin. |
| `bins` | `int \| None` | `None` | Number of bins. |
| `color` | `str \| None` | `None` | Bar color. |
| `show_labels` | `bool \| None` | `None` | Whether to show count labels. |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Heatmap

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `x_column` | `str \| int` | (required) | Column for X categories. |
| `y_column` | `str \| int` | (required) | Column for Y categories. |
| `value_column` | `str \| int` | (required) | Column for cell values. |
| `show_cell_labels` | `bool \| None` | `None` | Whether to show values inside cells. |
| `min_value` | `float \| int \| None` | `None` | Optional minimum for the color scale. |
| `max_value` | `float \| int \| None` | `None` | Optional maximum for the color scale. |
| `color` | `str \| list[str] \| None` | `None` | D3 interpolator name (e.g., `'Viridis'`) or custom colors. |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Boxplot

Supports two modes:

- **Data mode:** provide `data_column` (and optional `category_column`)
- **Pre-calculated mode:** provide `min_column`, `q1_column`, `median_column`, `q3_column`, `max_column` (and optional `mean_column`)

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `data_column` | `str \| int \| None` | `None` | Raw values column (data mode). |
| `category_column` | `str \| int \| None` | `None` | Grouping/label column. |
| `min_column` | `str \| int \| None` | `None` | Pre-calculated minimum column. |
| `q1_column` | `str \| int \| None` | `None` | Pre-calculated Q1 column. |
| `median_column` | `str \| int \| None` | `None` | Pre-calculated median column. |
| `q3_column` | `str \| int \| None` | `None` | Pre-calculated Q3 column. |
| `max_column` | `str \| int \| None` | `None` | Pre-calculated maximum column. |
| `mean_column` | `str \| int \| None` | `None` | Pre-calculated mean column (optional). |
| `direction` | `str \| None` | `None` | `'vertical'` or `'horizontal'`. |
| `show_outliers` | `bool \| None` | `None` | Whether to show outliers. |
| `color` | `str \| list[str] \| None` | `None` | Fill color or scheme. |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Modal Button

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `modal_id` | `str` | (required) | The global modal id to open. |
| `button_label` | `str` | (required) | Button label text. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

> Note: Most visuals also support `modal_id` as a keyword argument to enable an "expand" icon that opens a modal on click.



### Modals

Create detailed overlays that can be triggered from any element.

```python
# Define a modal
modal = report.add_modal("details", "Detailed View")
modal.add_row().add_table("my_data")

# Trigger from a visual
page.add_row().add_kpi("my_data", "A", "Metric", modal_id="details")

# Or add a dedicated button
page.add_row().add_modal_button("details", "Open Details")
```

### Visual Elements (Annotations)

Add trend lines, markers, and custom axes to your charts.

#### Trend Lines

You can add a trend line using the `.add_trend()` method. It can automatically calculate linear or polynomial regression if you don't provide coefficients.

```python
chart = page.add_row().add_scatter("my_data", "A", "B")

# Auto-calculate linear trend (degree 1)
chart.add_trend(color="red")

# Auto-calculate polynomial trend (e.g., degree 2)
chart.add_trend(coefficients=2, color="blue", line_style="dashed")

# Manually provide coefficients [intercept, slope, ...]
chart.add_trend(coefficients=[0, 1.5], color="green")
```

#### Other Elements

Use `.add_element(type, **kwargs)` for other annotations.

| Element Type | Description | Key Arguments |
|--------------|-------------|---------------|
| `xAxis` | Vertical line at a specific X value. | `value`, `color`, `label`, `line_style` |
| `yAxis` | Horizontal line at a specific Y value. | `value`, `color`, `label`, `line_style` |
| `marker` | A point marker at a specific value. | `value`, `size`, `shape` (`circle`, `square`, `triangle`), `color` |
| `label` | A text label at a specific value. | `value`, `label`, `font_size`, `font_weight` |

```python
chart.add_element("yAxis", value=100, label="Target", color="green")
```

### Tree Traversal

All components (Pages, Rows, Layouts, Visuals) are part of a tree. You can access the root report from any component using `.get_report()`.

```python
visual = layout.add_visual("line", "my_data")
report = visual.get_report()
print(report.title)
```

## Datalys2 Documentation

For detailed information on available visuals and configuration, see [DOCUMENTATION.md](DOCUMENTATION.md).

Or see the github repo at https://github.com/kameronbrooks/datalys2-reporting
