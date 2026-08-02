# Datalys2 Reporting Python API
**Version 0.7.0**

A Python library to build and compile interactive HTML reports using the Datalys2 Reporting framework.

**Note:** Compatible with dl2 version 0.4.1
https://github.com/kameronbrooks/datalys2-reporting

## Documentation

📚 **[Full documentation lives in docs/](docs/README.md)** — organized so
every visual type and every feature has its own page:

- [Getting started](docs/getting-started.md)
- [Visuals](docs/README.md#visuals) — one page per visual type (KPI, Table,
  Pie, Line, Gauge, Tabs, …), each with a parameter table and a runnable
  example in [examples/all_visuals/](examples/all_visuals/)
- [Features](docs/README.md#features) — one page per feature (filtering,
  aggregation, formula datasources, thresholds, modals, persistence, …)

This README keeps a condensed reference below; the raw JSON config the viewer
consumes is documented in the
[datalys2-reporting viewer repo](https://github.com/kameronbrooks/datalys2-reporting).

## Installation

```bash
pip install dl2-reports
```

## Quick Start

```python
import pandas as pd
from dl2_reports import DL2Report, KPI, Table

# Create a report
report = DL2Report(title="My Report")

# Add data
df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
report.add_df("my_data", df, compress=True)

# Add a page and visuals (typed component API)
page = report.add_page("Overview")
page.add_row(
    KPI("my_data", value_column="A", title="Metric A"),
    Table("my_data", page_size=10),
)

# Save to HTML or show in Jupyter
report.save("report.html")
report.show()
```

## The Typed Component API (v2)

Since 0.5.0 the recommended way to build reports is with **typed component classes** —
one class per visual, imported from the package root:

`KPI, Table, Card, Pie, Bar, Line, Area, Scatter, Checklist, Histogram, Heatmap, Gauge, Boxplot, Calendar, Tabs, Link, ModalButton`

plus typed shapes for structured props:

`Threshold, SortSpec, TotalRow, TotalColumn, GaugeRange, AggregateColumn, Tab, ColumnFormat, ConditionalFormat`

```python
from dl2_reports import DL2Report, Line, Table, Tabs, Tab, Threshold, TotalRow, SortSpec

page.add_row(
    Line("sales", x_column="Month", y_columns=["Revenue"],
         threshold=Threshold(value=5000, mode="above")),
)
row = page.add_row()
row.add(Table("sales",
              id="orders-table",
              group_by="Region",
              default_sort=[SortSpec("Amount", "desc")],
              total_row=TotalRow(fns={"Units": "sum", "Amount": "avg"})))
row.add(Tabs(id="views", tabs=[
    Tab("Chart", children=[Line("sales", x_column="Month", y_columns=["Revenue"])]),
    Tab("Data",  children=[Table("sales")]),
]))
```

Why it's better:

- **Typos fail fast.** `Table("sales", pagesize=20)` raises `TypeError: unknown prop
  'pagesize' (did you mean 'page_size'?)` at construction — previously it serialized
  silently and the viewer ignored it.
- **Autocomplete and type checking** work everywhere (the package ships `py.typed`).
- **`extra={...}`** passes unmodeled viewer props through explicitly when you need
  forward compatibility.
- **`compile()` lints legacy calls too**: props the viewer doesn't know are reported as
  `[dl2]` warnings with suggestions (`report.compile(strict=True)` turns them into errors).

The legacy `row.add_kpi(...)` helpers keep working unchanged — they now delegate to the
component classes, and their unknown kwargs still pass through (flagged by the compile
lint). `add()` returns the component, so chaining (`.add_trend()`, `.get_value()`)
works as before.

### Migrating existing scripts

A codemod ships with the package (comments and formatting preserved; requires
`pip install dl2-reports[migrate]`):

```bash
python -m dl2_reports.migrate my_report.py            # dry run: shows a diff
python -m dl2_reports.migrate my_report.py --write    # apply
python -m dl2_reports.migrate notebooks/ --write      # directories & .ipynb work too
```

## Data Compression

**Always use compression for production reports.** The Python API provides automatic gzip compression for your datasets, which significantly reduces file size and improves browser performance.

### Why Compression Matters

- **Large datasets will cause severe performance issues or fail to load entirely without compression**
- Compressed reports load faster and consume less memory in the browser
- File sizes can be reduced by 80-90% or more
- The browser automatically decompresses data on-the-fly using the built-in `DecompressionStream` API

### Using Compression

#### Report-Level Default

When creating a `DL2Report`, you can set the default compression behavior:

```python
from dl2_reports import DL2Report

# Enable compression by default (recommended)
report = DL2Report(
    title="My Report",
    compress_visuals=True  # This is the default
)
```

#### Per-Dataset Control

Control compression for individual datasets using the `compress` parameter in `add_df()`:

```python
import pandas as pd
from dl2_reports import DL2Report

report = DL2Report(title="Sales Report")

# Compress large datasets (recommended for most data)
large_df = pd.read_csv("sales_data.csv")
report.add_df("salesData", large_df, compress=True)

# Small datasets can be uncompressed for easier debugging
small_df = pd.DataFrame({"kpi": [100]})
report.add_df("kpiData", small_df, compress=False)
```

### How It Works

When you set `compress=True`, the Python API automatically:

1. Serializes your data to JSON
2. Compresses it using gzip
3. Encodes it as a Base64 string
4. Stores it in a separate `<script>` tag in the HTML
5. Adds the `gc-compressed-data` meta tag for automatic memory cleanup

The browser then decompresses the data when the report loads.

### Best Practices

- **✅ Always compress in production** - essential for performance and reliability
- **✅ Compress any dataset with more than a few rows** - the overhead is minimal
- **❌ Only disable compression when:**
  - Debugging and you need to inspect the raw JSON in the HTML file
  - Working with extremely small datasets (single-row KPI values) during development

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
- `border`: bool or CSS border string (e.g. `"2px dashed #f59e0b"`; CSS strings honored by the viewer since dl2 0.4.1)
- `shadow`: bool or CSS box-shadow string (CSS strings honored by the viewer since dl2 0.4.1)
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
- `area` (via `add_area`)
- `checklist` (via `add_checklist`)
- `histogram` (via `add_histogram`)
- `heatmap` (via `add_heatmap`)
- `boxplot` (via `add_boxplot`)
- `modal` (via `add_modal_button`)
- `tabs` (via `add_tabs`, dl2 0.3+)
- `link` (via `add_link`, dl2 0.4+)
- `calendar` (via `add_calendar`, dl2 0.5+) — month/week/day calendar with spanning multi-day events, category coloring, and event detail modals

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
| `comparison_text` | `str` | The comparison text to show alongside the comparison value. Ex. ("Last Month", "Yesterday", etc.)
| `row_index` | `int \| None` | `None` | Row index to display (supports negative indices). |
| `format` | `str \| None` | `None` | `'number'`, `'currency'`, `'percent'`, `'date'`, `'hms'`. |
| `
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
| `page_size` | `int \| None` | `None` | Rows per page (groups per page while grouped). |
| `table_style` | `str \| None` | `None` | `'plain'`, `'bordered'`, or `'alternating'`. |
| `show_search` | `bool \| None` | `None` | Whether to show the search box. |
| `sortable` | `bool \| None` | `None` | Type-aware sorting; Shift+click multi-sort (viewer default true). |
| `default_sort` | `list[dict] \| None` | `None` | Initial sort, e.g. `[{"column": "Amount", "direction": "desc"}]`. |
| `hidden_columns` | `list[str] \| None` | `None` | Columns hidden initially. |
| `allow_column_hiding` | `bool \| None` | `None` | Runtime Columns menu (viewer default true). |
| `group_by` | `str \| None` | `None` | Initial grouping column (collapsible groups). |
| `group_aggregates` | `list[dict] \| None` | `None` | Per-group aggregates, e.g. `[aggregates.agg("Amount", "sum")]`. |
| `groups_collapsed` | `bool \| None` | `None` | Whether groups start collapsed. |
| `enable_export` | `bool \| None` | `None` | CSV export / clipboard copy (viewer default true). |
| `export_file_name` | `str \| None` | `None` | File name for CSV export. |
| `context_menu` | `bool \| None` | `None` | Right-click context menus (viewer default true). |
| `max_height` | `int \| None` | `None` | Max body height in px (scrollable body + sticky header). |
| `sticky_header` | `bool \| None` | `None` | Viewer default: true when `max_height` is set. |
| `total_row` | `bool \| dict \| None` | `None` | `True` or `{"label": ..., "fns": {"<col>": "<fn>"}}` — grand-total row (dl2 0.4+). |
| `total_column` | `bool \| dict \| None` | `None` | `True` or `{"label": ..., "columns": [...]}` — per-row total column (dl2 0.4+). |
| `row_modal` | `bool \| None` | `None` | Built-in row detail modal on double-click (dl2 0.4+). |
| `row_modal_id` | `str \| None` | `None` | Open a custom modal instead; cards can use `{{ row.Col }}` templates (dl2 0.4+). |
| `row_modal_columns` | `list[str] \| None` | `None` | Columns listed in the built-in detail modal. |
| `row_modal_title` | `str \| None` | `None` | Title of the built-in detail modal. |
| `column_formats` | `dict \| None` | `None` | Per-column display formats (dl2 0.4.1+) — see [Column Formatting](#column-formatting-dl2-041). |
| `conditional_formats` | `list \| None` | `None` | Highlight rules (dl2 0.4.1+) — see [Conditional Formatting](#conditional-formatting-dl2-041). |
| `id` | `str \| None` | `None` | Stable element id (persistence + link targeting). |
| `persist_state` | `bool \| None` | `None` | Persist sort/columns/grouping (viewer default: true when `id` is set). |
| `**kwargs` | `Any` | — | Additional common visual properties (e.g. `filter=`, `aggregate=`). |

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
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Bar (Clustered / Stacked)

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `x_column` | `str \| int` | (required) | Column for X-axis categories. |
| `y_columns` | `list[str]` | (required) | Series columns for Y values. |
| `stacked` | `bool` | `False` | If `True`, uses stacked bars; otherwise clustered. |
| `threshold` | `dict \| None` | `None` | Optional pass/fail coloring (see [Threshold Configuration](#threshold-configuration)). |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `show_legend` | `bool \| None` | `None` | Whether to show the legend. |
| `show_labels` | `bool \| None` | `None` | Whether to show value labels. |
| `horizontal` | `bool \| None` | `None` | Whether to render bars horizontally (viewer-dependent). |
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
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
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
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
| `threshold` | `dict \| None` | `None` | Optional pass/fail coloring (see [Threshold Configuration](#threshold-configuration)). |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Area

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `x_column` | `str \| int` | (required) | Column for X values. |
| `y_columns` | `list[str] \| str` | (required) | Column(s) for Y series. |
| `smooth` | `bool \| None` | `None` | Whether to render smooth curves. |
| `show_line` | `bool \| None` | `True` | Show line stroke on top of fill. |
| `show_markers` | `bool \| None` | `True` | Show interactive marker points. |
| `fill_opacity` | `float \| None` | `0.3` | Area fill opacity (0-1). |
| `show_legend` | `bool \| None` | `None` | Whether to show the legend. |
| `show_labels` | `bool \| None` | `None` | Whether to show value labels. |
| `min_y` | `float \| int \| None` | `None` | Optional minimum Y. |
| `max_y` | `float \| int \| None` | `None` | Optional maximum Y. |
| `colors` | `list[str] \| None` | `None` | Optional list of series colors. |
| `threshold` | `dict \| None` | `None` | Optional pass/fail coloring (see [Threshold Configuration](#threshold-configuration)). |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Checklist

Since dl2 0.4.1 the checklist has full table parity (type-aware sorting, column hiding,
CSV export, context menus, sticky header, row detail modals, persistent view state) plus
status filter chips and a completion progress bar. It remains **read-only by design** —
status always comes from the dataset.

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `status_column` | `str` | (required) | Column containing a truthy completion value. |
| `warning_column` | `str \| None` | `None` | Optional date column to evaluate for warnings. |
| `warning_threshold` | `int \| None` | `None` | Days before due date to trigger warning (viewer default 3). |
| `columns` | `list[str] \| None` | `None` | Optional subset of columns to display. |
| `page_size` | `int \| None` | `None` | Rows per page. |
| `show_search` | `bool \| None` | `None` | Whether to show the search box. |
| `sortable` | `bool \| None` | `None` | Type-aware sorting; Shift+click multi-sort (viewer default true). The Status header sorts by urgency (dl2 0.4.1+). |
| `default_sort` | `list \| None` | `None` | Initial sort — `SortSpec` or dicts. Accepts the special column `"status"` (urgency: overdue → due soon → pending → complete). Viewer default: urgency, then due date (dl2 0.4.1+). |
| `hidden_columns` | `list[str] \| None` | `None` | Columns hidden initially (dl2 0.4.1+). |
| `allow_column_hiding` | `bool \| None` | `None` | Runtime Columns menu (viewer default true) (dl2 0.4.1+). |
| `enable_export` | `bool \| None` | `None` | CSV export / clipboard copy; exports include a derived `Status` column (viewer default true) (dl2 0.4.1+). |
| `export_file_name` | `str \| None` | `None` | File name for CSV export (dl2 0.4.1+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menus (viewer default true) (dl2 0.4.1+). |
| `max_height` | `int \| None` | `None` | Max body height in px (scrollable body + sticky header) (dl2 0.4.1+). |
| `sticky_header` | `bool \| None` | `None` | Viewer default: true when `max_height` is set (dl2 0.4.1+). |
| `row_modal` | `bool \| None` | `None` | Built-in row detail modal on double-click; leads with the status (dl2 0.4.1+). |
| `row_modal_id` | `str \| None` | `None` | Open a custom modal instead; cards can use `{{ row.Col }}` templates (dl2 0.4.1+). |
| `row_modal_columns` | `list[str] \| None` | `None` | Columns listed in the built-in detail modal (dl2 0.4.1+). |
| `row_modal_title` | `str \| None` | `None` | Title of the built-in detail modal (dl2 0.4.1+). |
| `show_status_filter` | `bool \| None` | `None` | Status filter chips with counts — All / Pending / Due Soon / Overdue / Complete (viewer default true) (dl2 0.4.1+). |
| `show_progress` | `bool \| None` | `None` | Completion progress bar next to the "X / Y Completed" summary (viewer default true) (dl2 0.4.1+). |
| `hide_completed` | `bool \| None` | `None` | Start with completed tasks hidden — the Complete chip toggled off (dl2 0.4.1+). |
| `column_formats` | `dict \| None` | `None` | Per-column display formats — see [Column Formatting](#column-formatting-dl2-041) (dl2 0.4.1+). |
| `conditional_formats` | `list \| None` | `None` | Highlight rules — see [Conditional Formatting](#conditional-formatting-dl2-041) (dl2 0.4.1+). |
| `id` | `str \| None` | `None` | Stable element id (persistence + link targeting). |
| `persist_state` | `bool \| None` | `None` | Persist sort/columns/status chips (viewer default: true when `id` is set). |
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
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
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
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
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
| `enable_export` | `bool \| None` | `None` | Right-click image export — Export PNG / Export SVG (viewer default true) (dl2 0.5+). |
| `export_file_name` | `str \| None` | `None` | Base file name for image export, without extension (dl2 0.5+). |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true) (dl2 0.5+). |
| `**kwargs` | `Any` | — | Additional common visual properties. |

#### Modal Button

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `modal_id` | `str` | (required) | The global modal id to open. |
| `button_label` | `str` | (required) | Button label text. |
| `**kwargs` | `Any` | — | Additional common visual properties. |

> Note: Most visuals also support `modal_id` as a keyword argument to enable an "expand" icon that opens a modal on click.

### Threshold Configuration

Color chart elements based on whether values pass or fail a threshold. Applies to **Line**, **Area**, and **Clustered Bar**.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `value` | `number` | (required) | The threshold value to compare against. |
| `pass_color` | `str` | `#22c55e` | Color for passing values. |
| `fail_color` | `str` | `#ef4444` | Color for failing values. |
| `mode` | `'above'`\|`'below'`\|`'equals'` | `'above'` | How to determine pass/fail. |
| `show_line` | `bool` | `True` | Show reference line at threshold. |
| `line_style` | `'solid'`\|`'dashed'`\|`'dotted'` | `'dashed'` | Threshold line style. |
| `blend_width` | `number` | `5` | Gradient blend zone width (line/area only). |
| `apply_to` | `'both'`\|`'markers'`\|`'lines'` | `'both'` | Which elements get threshold colors. |

**Mode Options:**
- `'above'` - Values >= threshold pass
- `'below'` - Values <= threshold pass
- `'equals'` - Only exact matches pass

### Chart Image Export (dl2 0.5+)

All 10 SVG chart types (`line`, `area`, `stackedBar`, `clusteredBar`, `pie`, `scatter`, `histogram`, `heatmap`, `boxplot`, `gauge`) support right-click → **Export PNG** / **Export SVG**, using the same prop names as the table's CSV export:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `enable_export` | `bool` | viewer default true | Enable image export. |
| `export_file_name` | `str` | title → dataset id → chart type | Base file name, without extension. |
| `context_menu` | `bool` | viewer default true | Right-click context menu. |

Exports capture the chart `<svg>` only (not titles or containers); PNG renders at 2× scale, and the current theme colors are baked in.




#### Tabs (dl2 0.3+)

`row.add_tabs()` returns a `Tabs` container; `tabs.add_tab(title)` returns a full `Layout`, so every `add_*` helper works inside a tab. Tabs can be nested.

```python
tabs = page.add_row().add_tabs(id="sales-tabs", default_tab=0, title="Sales Views")
tabs.add_tab("Chart").add_line("sales", x_column="Month", y_columns=["Revenue"])
tabs.add_tab("Data", direction="column").add_table("sales", id="sales-table")
```

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `id` | `str \| None` | auto | Stable id — enables active-tab persistence (dl2 0.4+) and link targeting. |
| `default_tab` | `int \| None` | `None` | Index of the initially active tab (viewer default 0). |
| `title` | `str \| None` | `None` | Optional title above the tab strip. |
| `**kwargs` | `Any` | — | Container props (`padding`, `border`, `shadow`, `flex`, `persist_state`, ...). |

`add_tab(title, direction="column", **layout_kwargs)` — the kwargs are layout props (`gap`, `wrap`, `columns`, ...).

#### Link (dl2 0.4+)

Navigate to any visual with an `id` (switches page, activates containing tabs, scrolls, flashes) or to an external URL. Exactly one of `target_id` / `href` is required.

```python
row.add_link(target_id="sales-table", label="Jump to data", link_style="button")
row.add_link(href="https://example.com", label="Docs")
```

#### Calendar (dl2 0.5+)

A month/week/day calendar (`type: "calendar"`) with spanning multi-day events, category coloring with a legend, and event detail modals. Available as the `dl2_reports.Calendar` component class or the legacy `row.add_calendar(...)` helper. A dataset is required, plus **exactly one** date mapping: `date_column` (single-date events) or `start_column` (+ optional `end_column` for spanning events).

```python
from dl2_reports import Calendar
page.add_row(Calendar("events",
    start_column="Start", end_column="End",
    title_column="Task", category_column="Team",
    default_view="week", time_format="24h", id="team-calendar"))
```

| Parameter | Type | Default | Description |
|----------|------|---------|-------------|
| `dataset_id` | `str` | (required) | The dataset id. |
| `date_column` | `str \| int \| None` | `None` | Column with the event date (single-date events). Mutually exclusive with `start_column`. |
| `start_column` | `str \| int \| None` | `None` | Event start column (spanning events). |
| `end_column` | `str \| int \| None` | `None` | Event end column; only meaningful with `start_column`. |
| `title_column` | `str \| int \| None` | `None` | Column for event titles (viewer default: first unused dataset column). |
| `category_column` | `str \| int \| None` | `None` | Column for tag-based coloring with a legend. |
| `default_view` | `str \| None` | `None` | `'month'`, `'week'`, or `'day'` (viewer default `'month'`). |
| `default_date` | `str \| None` | `None` | Initial date as an ISO string, e.g. `"2026-08-01"` (viewer default: today, UTC). |
| `week_starts_on` | `int \| None` | `None` | `0` (Sunday, viewer default) or `1` (Monday). |
| `show_weekends` | `bool \| None` | `None` | Show Saturday/Sunday columns (viewer default true). |
| `day_start_hour` | `int \| None` | `None` | First hour shown on the week/day hour grid, 0-23 (viewer default 0). |
| `day_end_hour` | `int \| None` | `None` | Hour the grid ends at, 1-24 (viewer default 24; must be greater than `day_start_hour`). |
| `hour_height` | `int \| None` | `None` | Pixel height of one hour row (viewer default 48). |
| `max_events_per_day` | `int \| None` | `None` | Events shown per month cell before the "+N more" clamp (viewer default 3; released when printing). |
| `time_format` | `str \| None` | `None` | `'12h'` (viewer default) or `'24h'`. |
| `max_height` | `int \| None` | `None` | Max height in px of the month grid (viewer default 560). |
| `empty_label` | `str \| None` | `None` | Text shown when the dataset has no events (viewer default `"No events."`). |
| `color` | `str \| list[str] \| None` | `None` | Category palette — D3 scheme name, single color, or list (viewer default `'tableau10'`). |
| `show_legend` | `bool \| None` | `None` | Category legend (viewer default: true when `category_column` is set). |
| `legend_title` | `str \| None` | `None` | Legend heading. |
| `row_modal` | `bool \| None` | `None` | Built-in event detail modal on double-click. |
| `row_modal_id` | `str \| None` | `None` | Open a custom modal instead; cards can use `{{ row.Col }}` templates. |
| `row_modal_columns` | `list[str] \| None` | `None` | Columns listed in the built-in detail modal. |
| `row_modal_title` | `str \| None` | `None` | Title of the built-in detail modal. |
| `context_menu` | `bool \| None` | `None` | Right-click context menu (viewer default true). |
| `id` | `str \| None` | `None` | Stable element id (persistence + link targeting). |
| `persist_state` | `bool \| None` | `None` | Persist the active view (viewer default: true when `id` is set). |
| `**kwargs` | `Any` | — | Additional common visual properties. |

Notes:

- **Dtypes drive event kind:** columns declared `"date"` render as all-day events; `"datetime"` columns render as timed events on the week/day hour grid (see the `add_df` dtype inference under [Date dtypes](#date-dtypes--dtype_overrides-dl2-05)). All calendar math is UTC.
- The Python class raises `ValueError` on conflicting or missing date mappings and on out-of-range hours/enums.
- Unlike charts, the calendar has no `width`/`height` props — size it with `max_height` and `flex`.

### Filtering & Aggregation (dl2 0.3+)

Any visual accepts `filter=` and `aggregate=` — several visuals can show different client-side slices of one shared dataset, with no extra data embedded in the HTML. Use the `filters` and `aggregates` builder modules (plain dicts work too); invalid operators/functions raise `ValueError` at build time.

```python
from dl2_reports import DL2Report, aggregates as A, filters as F

# Filter: leaf conditions + and_/or_/not_ composition
row.add_table(
    "sales",
    filter=F.and_(F.gte("Amount", 200), F.isin("Region", ["South", "West"])),
)

# Aggregate: groupBy + aggregate fns (applied after the filter)
row.add_bar(
    "sales",
    x_column="Region",
    y_columns=["sum_Amount"],   # default output name is "{fn}_{column}"
    aggregate=A.aggregate("Region", A.agg("Amount", "sum")),
)
```

Filter shortcuts: `eq, neq, gt, gte, lt, lte, isin, notin, contains, starts_with, ends_with, between, is_null, not_null` (plus generic `where(column, op, ...)`).
Aggregate fns: `sum, avg, min, max, count, countDistinct, first, last`. Use `A.agg("Amount", "sum", as_="Total")` to name the output column.

### Formula Datasources (0.7.0+)

Anywhere a dataset is referenced as an input — any visual's `dataset_id` or a derived
dataset's `source` — you can write a **pandas-style formula** instead of building a
`filter=` dict. Formulas are parsed with Python's `ast` module at construction time and
compile to the plain dataset id plus the standard filter grammar; nothing new reaches
the report JSON, and typos fail fast with a `ValueError`.

```python
# Filter rows (any visual)
row.add_table("sales[Amount > 200]")
row.add_bar("sales[Region == 'West' and Amount >= 100]",
            x_column="Month", y_columns=["Revenue"])

# Select columns with double brackets (table-like visuals)
row.add_table("sales[['Region', 'Amount']]")

# Chain like pandas — filters AND together, one projection allowed
row.add_table("sales[Amount > 200][['Region', 'Amount']]")

# Derived datasets accept formula sources too
report.add_derived_dataset(
    "big_by_region",
    "sales[Amount > 100]",
    aggregate=A.aggregate("Region", A.agg("Amount", "sum", as_="Total")),
)
```

Supported inside the brackets:

| Form | Compiles to |
|------|-------------|
| `==  !=  >  >=  <  <=` (either operand order) | `eq/neq/gt/gte/lt/lte` |
| `Region in ['S', 'W']` / `not in` | `in` / `nin` |
| `100 <= Amount <= 200` | `between` (inclusive) |
| `Amount == None` / `is None` / `!= None` / `is not None` | `isNull` / `notNull` |
| `and`, `or`, `not` — or pandas-style `&`, `\|`, `~` | `and` / `or` / `not` groups |
| `.contains(x)`, `.startswith(x)`, `.endswith(x)`, `.isin([...])`, `.between(lo, hi)`, `.isnull()`/`.isna()`, `.notnull()`/`.notna()` (optional `.str`) | the matching filter op |

Column references are bare names (`Amount`), attribute style (`sales.amount`), or
subscript style for names that aren't Python identifiers or are keywords:
`sales[sales["Due Date"] > "2026-01-01"]`.

Notes:

- A formula's filter **AND-combines** with an explicit `filter=` (formula first), so
  both constraints apply.
- `[[...]]` projection works on visuals that model `columns` (Table, Checklist) and
  raises elsewhere — the viewer ignores `columns` on charts, and on derived-dataset
  sources, which support only filter + aggregate.
- As in pandas, `&`/`|` bind tighter than comparisons — parenthesize each term:
  `(Amount > 100) & (Units < 5)`. The unparenthesized form raises rather than
  mis-filtering.
- Values must be literals (strings, numbers, booleans, `None`, lists/tuples of those).
  Interpolate Python variables with an f-string *outside* the formula:
  `f"sales[Amount > {threshold}]"`.
- Formula filters run **in the browser** like `filter=` — `report.get_value()` and
  `add_trend()` auto-coefficients still read the unfiltered source DataFrame.

### Derived Datasets (dl2 0.3+)

Declare a dataset computed **in the browser** from another dataset — filtered and/or aggregated at load time. Chains are supported and declaration order doesn't matter (sources are checked at `compile()`).

```python
report.add_derived_dataset(
    "north_by_category",
    source="sales",
    filter=F.eq("Region", "North"),
    aggregate=A.aggregate("Category", A.agg("Amount", "sum", as_="Total")),
)
page.add_row().add_table("north_by_category")

# Or equivalently with a formula source (0.7.0+):
report.add_derived_dataset(
    "north_by_category",
    source="sales[Region == 'North']",
    aggregate=A.aggregate("Category", A.agg("Amount", "sum", as_="Total")),
)
```

Note: derived values are not available to `report.get_value()` at compile time (they only exist in the browser) — compute with pandas if you need them while building.

### Remote Datasets (dl2 0.5+)

Declare a dataset fetched **in the browser** from a URL at load time — nothing is embedded in the HTML. The report renders immediately; visuals bound to the dataset show a loading placeholder until the fetch settles. The endpoint must be CORS-accessible from wherever the report is opened.

```python
report.add_remote_dataset(
    "live_orders",
    url="https://api.example.com/orders",
    extract="result.rows",     # rows live inside a JSON wrapper object
    refresh_interval=60,       # re-fetch every 60 seconds
    columns=["Region", "Amount", "Updated"],
    dtypes=["string", "number", "datetime"],
)
page.add_row().add_table("live_orders")
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | The unique dataset id. |
| `url` | `str` | (required) | The URL to fetch the data from. |
| `response_type` | `str \| None` | `None` | `'json'` (viewer default) or `'csv'`. |
| `extract` | `str \| None` | `None` | Dot-path to the rows inside a JSON wrapper object, e.g. `"result.rows"`. JSON only. |
| `headers` | `dict \| None` | `None` | HTTP request headers (string values). **Plain text in the HTML** — see below. |
| `refresh_interval` | `int \| float \| None` | `None` | Re-fetch every N seconds. Omit or `0` to fetch once. |
| `columns` | `list[str] \| None` | `None` | Declared column names (otherwise inferred from the response). |
| `dtypes` | `list[str] \| None` | `None` | Declared column dtypes, aligned with `columns`. |
| `format` | `str \| None` | `None` | Declared data format (`'records'`, `'table'`, `'list'`, or `'record'`; viewer default `'records'`). |

- A JSON response (the default) may be a bare array of rows or a full `{columns, dtypes, format, data}` dataset object — response fields win over the declaration. A CSV response parses into a records dataset with its header row as columns.
- Declared `dtypes` still drive date conversion — declare `"date"`/`"datetime"` columns so tables, charts, and calendars treat them as dates.
- Refreshes swap data in place; a failed refresh keeps the last good data.
- Derived datasets can use a remote dataset as their `source` — derivation waits for the fetch and re-runs on every refresh.
- **`headers` are embedded as plain text in the compiled HTML** — anyone who can open the report can read them. Only use tokens that are safe to treat as public.
- `report.get_value()` raises for remote datasets (the data only exists in the browser).
- Validation mirrors the viewer's remote-dataset warnings: `ValueError` on an empty `url`, `extract` with a CSV response, a negative `refresh_interval`, non-string header values, or a `columns`/`dtypes` length mismatch.

### Date dtypes & `dtype_overrides` (dl2 0.5+)

`add_df()` now declares date-like columns as `"datetime"` when any value carries a time of day, and `"date"` when every value is midnight (previously always `"date"`). This matters for the calendar visual — `"date"` columns render as all-day events, `"datetime"` columns as timed events on the hour grid.

Override the inference per column with the new `dtype_overrides` parameter:

```python
report.add_df("tasks", df, compress=True,
              dtype_overrides={"Due": "datetime"})   # force timed events
```

Keys must be columns of the DataFrame — unknown columns raise `ValueError`.

### Table Totals & Row Detail Modals (dl2 0.4+)

```python
page.add_row().add_table(
    "orders",
    id="orders-table",
    total_row={"label": "Totals", "fns": {"Units": "sum", "Amount": "avg"}},
    total_column={"columns": ["Units", "Amount"]},
    row_modal_id="order-detail",       # or row_modal=True for the built-in modal
)

modal = report.add_modal("order-detail", "Order Details")
modal.add_row().add_card(
    title="Order — {{ row.Region }}",
    text="**Rep:** {{ row.Rep }}\n**Amount:** {{ formatCurrency(row.Amount) }}",
    content_type="md",
)
```

The column names in `total_row["fns"]` are preserved exactly as written (they are not snake_case→camelCase converted). For your own passthrough props whose dict **keys** are column names, wrap them in `dl2_reports.RawDict` to get the same protection.

### Column Formatting (dl2 0.4.1+)

Give Table and Checklist columns display formats with `column_formats=` — a mapping of
column name → `ColumnFormat`, dict, or shorthand kind string:

```python
from dl2_reports import ColumnFormat

page.add_row().add_table(
    "orders",
    column_formats={
        "Amount": ColumnFormat("currency", digits=0),   # or {"format": "currency", "digits": 0}
        "Growth": ColumnFormat("percent", digits=1),    # raw values are ratios (0.42 → 42.0%)
        "Due": "date",                                  # shorthand string
        "Runtime": "hms",                               # seconds → HH:MM:SS
    },
)
```

- Kinds: `'number'`, `'currency'`, `'percent'`, `'date'`, `'hms'`; options: `digits` (currency default 2, percent default 1) and `symbol` (currency only, default `'$'`).
- Applies to cells, total row/column, group aggregates (matched by the aggregate's `as` name), and row detail modals.
- **Display-only:** CSV export keeps raw values; clipboard copy matches the formatted view.
- Column names used as keys are preserved verbatim (no snake_case→camelCase conversion).

### Conditional Formatting (dl2 0.4.1+)

Highlight cells or whole rows with `conditional_formats=` — a list of rules evaluated per
row using the standard filter grammar:

```python
from dl2_reports import ConditionalFormat, filters as F

page.add_row().add_table(
    "orders",
    conditional_formats=[
        ConditionalFormat(when=F.gte("Amount", 300), style="success"),
        ConditionalFormat(when=F.lt("Amount", 100), target="row", style="error"),
        ConditionalFormat(
            when=F.and_(F.eq("Region", "West"), F.gt("Units", 10)),
            columns=["Units"],                       # required for compound `when`
            css={"font_weight": 600, "background_color": "#fef3c7"},
        ),
    ],
)
```

- `style` is a named theme-aware preset: `'success'`, `'warning'`, `'error'`, `'info'`, or `'muted'` (note: the field is `style`, not `preset`). `css` layers inline overrides on top; snake_case keys become camelCase React style names.
- `target` is `'cell'` (default — styles the matching cell(s)) or `'row'`. For cell targets, `columns` defaults to the `when` condition's own column; compound (`and`/`or`/`not`) conditions must set `columns` explicitly (the Python API enforces this).
- First matching rule wins per target; one row rule and one cell rule can compose. Totals/aggregate rows are exempt. Rules see raw values (before `column_formats`).
- Every rule needs `style` and/or `css` — `ConditionalFormat` raises `ValueError` otherwise, and validates `when` at construction time.

Both props work identically on `Checklist` (dl2 0.4.1 rebuilt it on the table infrastructure).

### Persistent View State (dl2 0.4+)

Runtime view changes (table sort/hidden columns/grouping, active tabs) are saved to localStorage per report + visual `id` and restored on reload.

- Give tables/tabs a stable `id=` and the viewer persists them automatically; opt out per visual with `persist_state=False`.
- Set a stable report identity so state survives title changes: `DL2Report(title, report_id="my-report")` or `report.set_report_id("my-report")` (emits `<meta name="report-id">`).
- Users can reset via right-click → Reset view, or the report-wide Reset view button.

### Printing (dl2 0.5+)

Printing a report (Ctrl+P, or a headless `page.pdf()`) renders the entire report — all pages, tabs flattened, tables and checklists unpaginated, and the calendar's "+N more" clamp released — with a pinned light palette. No configuration is needed from the Python side.

### Layout Options (dl2 0.3+)

Layouts own spacing now (`gap` defaults to 10px; visuals default to `margin: 0`). Rows/columns accept `wrap=True`, `align=...`, `justify=...`; grids accept `min_child_width=250` for responsive `auto-fit` columns. `flex=0` and `padding=0`/`margin=0` are respected.

```python
page.add_row(wrap=True, gap=16, justify="space-between")
page.add_row(direction="grid", min_child_width=250)
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

Supported on `line`, `area`, `scatter`, `clusteredBar`, `stackedBar`, and `histogram`
visuals (before dl2 0.4.1 the viewer only rendered trends on scatter plots).

```python
chart = page.add_row().add_scatter("my_data", "A", "B")

# Auto-calculate linear trend (degree 1)
chart.add_trend(color="red")

# Auto-calculate polynomial trend (e.g., degree 2)
chart.add_trend(coefficients=2, color="blue", line_style="dashed")

# Manually provide coefficients [intercept, slope, ...]
chart.add_trend(coefficients=[0, 1.5], color="green")
```

> **Units:** on categorical X axes (line, area, bars) the viewer evaluates coefficients
> against the 0-based category index; numeric axes (scatter, histogram) use real axis
> units. Auto-calculation needs `x_column` and `y_column` props, so histograms (binned
> counts) and multi-series charts (`y_columns`) require explicit `coefficients`.

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

## Reading Values

The API provides two ways to read scalar values back from your data after the report is built. These are useful for conditional layout logic, threshold checks, or computing derived metrics without re-querying the original DataFrame.

### `report.get_value()`

Query a value from any registered dataset by name — no visual reference required.

```python
report.get_value(data_source_name, column_name, row_index=-1)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_source_name` | `str` | (required) | The dataset name passed to `add_df()`. |
| `column_name` | `str` | (required) | The column to read from. |
| `row_index` | `int` | `-1` | Row index. Negative indices count from the end (e.g. `-1` = last row). |

This is the right tool when you need to inspect a value **before** or **without** creating a visual — for example, deciding whether to add a row at all:

```python
report = DL2Report(title="Sales Report")
report.add_df("sales", sales_df, format="records", compress=False)

page = report.add_page("Overview")

# Add a bar chart
bar_row = page.add_row()
bar_row.add_bar(dataset_id="sales", x_column="region", y_columns=["revenue"])

# Only add a warning card if the worst region is below target
TARGET = 120_000
revenues = [report.get_value("sales", "revenue", i) for i in range(len(sales_df))]
worst = min(revenues)

if worst < TARGET:
    warning_row = page.add_row()
    warning_row.add_card(
        title="Warning: underperforming region detected",
        text=f"Lowest revenue is ${worst:,} — below the ${TARGET:,} target.",
        content_type="md",
    )
```

### `visual.get_value()`

Read the scalar value that a specific visual represents, directly from its backing DataFrame. The visual must be part of the report tree (i.e. already added to a row) and its props must include `row_index` and `value_column`.

```python
value = visual.get_value()
```

This is the right tool when you already have a visual reference and want to inspect or act on its value:

```python
kpi = page.add_row().add_kpi(
    dataset_id="sales",
    value_column="revenue",
    row_index=0,
    title="Revenue – North",
    format="currency",
)

north_revenue = kpi.get_value()
print(f"North revenue: {north_revenue:,}")
```

### `visual.copy()`

Create a duplicate of a visual with the same `type`, `dataset_id`, props, and annotations, but a new unique ID. Use this to stamp the same visual configuration into multiple rows without re-specifying every argument.

```python
copied_visual = visual.copy()
```

After copying, add the copy back into any layout row using `row.add_visual(copy.type, visual=copy)`. You can then mutate `copy.props` to override only what differs:

```python
# Build a prototype KPI once
proto = row.add_kpi(
    dataset_id="sales",
    value_column="revenue",
    row_index=0,
    title="Revenue – North",
    format="currency",
)

# Stamp copies for remaining regions
for i, region in enumerate(["South", "East", "West"], start=1):
    copy = proto.copy()
    copy.props["row_index"] = i
    copy.props["title"] = f"Revenue – {region}"
    row.add_visual(copy.type, visual=copy)

# Each copy exposes get_value() once it is in the tree
total = proto.get_value() + sum(
    row.children[i].get_value() for i in range(1, 4)
)
```

## Conditional Layout

Use `layout.on_condition()` to conditionally add visuals to a row at report-build time. This is a compile-time guard — it evaluates a plain Python `bool` and either delegates the `add_*` call to the real layout or silently discards it.

```python
layout.on_condition(condition).add_<visual>(...)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `condition` | `bool` | If `True`, the visual is added normally and returned. If `False`, nothing is added and `None` is returned. |

### How It Works

- When `condition` is `True`, the call is forwarded to the parent layout exactly as if you had called `layout.add_<visual>(...)` directly.
- When `condition` is `False`, no visual is created, no element ID is consumed, and `None` is returned.
- The wrapper is **not** a tree node — it never occupies a slot in the report tree regardless of the condition.

### Example: Show a warning card only when a threshold is breached

```python
report = DL2Report(title="Sales Report")
report.add_df("sales", sales_df, format="records", compress=False)

page = report.add_page("Overview")
row = page.add_row()
row.add_bar(dataset_id="sales", x_column="region", y_columns=["revenue"])

TARGET = 120_000
worst = min(report.get_value("sales", "revenue", i) for i in range(len(sales_df)))

warning_row = page.add_row()
warning_row.on_condition(worst < TARGET).add_card(
    title="Warning: underperforming region detected",
    text=f"Lowest revenue is ${worst:,} — below the ${TARGET:,} target.",
)
```

### Example: Toggle a chart based on a flag

```python
show_details = True  # could come from any Python logic

detail_row = page.add_row()
detail_row.on_condition(show_details).add_table("sales", title="Detail View")
```

> **Tip:** Since 0.5.0, `on_condition(False)` returns a falsy `NullComponent` instead of `None` — chained calls like `.add_trend()` are silently absorbed, so no guard is needed. Truthiness checks (`if result:`) keep working; `is None` checks should become truthiness checks.

## Datalys2 Documentation

For the organized per-visual / per-feature documentation of this Python API, see [docs/](docs/README.md).

For the underlying JSON configuration and the viewer itself, see the
[datalys2-reporting repo](https://github.com/kameronbrooks/datalys2-reporting) —
it has the full, up-to-date JSON spec.
