# Datalys2 Reporting Python API
**Version 0.4.0**

A Python library to build and compile interactive HTML reports using the Datalys2 Reporting framework.

**Note:** Compatible with dl2 version 0.4.0
https://github.com/kameronbrooks/datalys2-reporting

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

`KPI, Table, Card, Pie, Bar, Line, Area, Scatter, Checklist, Histogram, Heatmap, Gauge, Boxplot, Tabs, Link, ModalButton`

plus typed shapes for structured props:

`Threshold, SortSpec, TotalRow, TotalColumn, GaugeRange, AggregateColumn, Tab`

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
- `area` (via `add_area`)
- `checklist` (via `add_checklist`)
- `histogram` (via `add_histogram`)
- `heatmap` (via `add_heatmap`)
- `boxplot` (via `add_boxplot`)
- `modal` (via `add_modal_button`)
- `tabs` (via `add_tabs`, dl2 0.3+)
- `link` (via `add_link`, dl2 0.4+)

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
| `threshold` | `dict \| None` | `None` | Optional pass/fail coloring (see [Threshold Configuration](#threshold-configuration)). |
| `x_axis_label` | `str \| None` | `None` | Optional X-axis label. |
| `y_axis_label` | `str \| None` | `None` | Optional Y-axis label. |
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
```

Note: derived values are not available to `report.get_value()` at compile time (they only exist in the browser) — compute with pandas if you need them while building.

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

### Persistent View State (dl2 0.4+)

Runtime view changes (table sort/hidden columns/grouping, active tabs) are saved to localStorage per report + visual `id` and restored on reload.

- Give tables/tabs a stable `id=` and the viewer persists them automatically; opt out per visual with `persist_state=False`.
- Set a stable report identity so state survives title changes: `DL2Report(title, report_id="my-report")` or `report.set_report_id("my-report")` (emits `<meta name="report-id">`).
- Users can reset via right-click → Reset view, or the report-wide Reset view button.

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

For detailed information on available visuals and configuration, see [DOCUMENTATION.md](DOCUMENTATION.md).

Or see the github repo at https://github.com/kameronbrooks/datalys2-reporting
