# Datalys2 Reporting Python API

A Python library to build and compile interactive HTML reports using the Datalys2 Reporting framework.

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

**Pro Tip:** Use `%autoreload` to see your code changes immediately without restarting the kernel:
```python
%load_ext autoreload
%autoreload 2
```

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

## Available Visuals

All visuals are added to a layout row using `row.add_<type>(...)`.

### Charts & Data

| Method | Description | Key Arguments |
|--------|-------------|---------------|
| `add_kpi` | Large metric display. | `dataset_id`, `value_column`, `title` |
| `add_table` | Interactive data table. | `dataset_id`, `title`, `page_size` |
| `add_bar` | Clustered or Stacked bar chart. | `dataset_id`, `x_column`, `y_columns` (list), `stacked` (bool) |
| `add_scatter` | Scatter plot. | `dataset_id`, `x_column`, `y_column` |
| `add_pie` | Pie or Donut chart. | `dataset_id`, `category_column`, `value_column` |
| `add_card` | Simple text card. | `title`, `text` |

### Interactive Elements

| Method | Description | Key Arguments |
|--------|-------------|---------------|
| `add_modal_button` | A button that opens a modal. | `modal_id`, `button_label` |

> **Note:** Most visuals also support `modal_id` as a keyword argument to enable an "expand" icon that opens a modal on click.

## Documentation

For detailed information on available visuals and configuration, see [DOCUMENTATION.md](DOCUMENTATION.md).
