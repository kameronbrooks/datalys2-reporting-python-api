# Datalys2 Reporting Documentation
**Version 0.6.0**


This documentation guides you on how to create HTML reports using the Datalys2 Reporting library.

**Note:**
This is still early in development and each patch version could have breaking changes.

## HTML Structure

To create a report, you need a standard HTML file that includes the library's CSS, the library's JavaScript bundle, a root container, and a special script tag for the data.

You can also use standard HTML meta tags to configure the report header information.

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Report Metadata -->
    <title>Your Report Title</title>
    <meta name="description" content="A brief description of this report">
    <meta name="author" content="Report Author Name">
    <meta name="last-updated" content="2024-01-01">
    <meta name="dl-version" content="0.4.1">

    <!-- Include the library styles -->
    <link rel="stylesheet" href="path/to/dl2-style.css">
</head>
<body>
    <!-- The root element where the app will mount -->
    <div id="root"></div>

    <!-- The configuration data for the report -->
    <script id="report-data" type="application/json">
    {
        "pages": [],
        "datasets": {}
    }
    </script>

    <!-- Include the library script -->
    <script src="path/to/datalys2-reporting.js"></script>
</body>
</html>
```

### Report Metadata

The application reads the following tags from the `<head>` to populate the report header:

| Tag / Name | Description |
|------------|-------------|
| `<title>` | Sets the main title of the report. |
| `description` | Sets the report description text. |
| `author` | Displays the author's name. |
| `last-updated` | Displays the last updated date/time. |
| `report-id` | Optional (0.4+). Stable id used to namespace persisted view state in localStorage. Falls back to the title, then the file path. |
| `dl2-validate` | Optional (0.3+). Set content to `"false"` to disable config validation warnings. |
| `gc-compressed-data` | Optional. Set content to `"true"` to free compressed source strings after decompression. |

## The `report-data` Script

The core of the report configuration lives inside the `<script id="report-data" type="application/json">` tag. This JSON object must adhere to the `ApplicationData` structure.

**Alternative: Compressed report-data**

For reports with large configuration objects, you can compress the `report-data` itself using gzip and base64 encoding. Simply change the script type to `text/b64-gzip` and provide the compressed string:

```html
<script id="report-data" type="text/b64-gzip">
H4sIAAAAAAAAA6tWKkktLlGyUlAqS8wpTtVRKi1OLUpV0lFQSixOVbICMqAMqFpbAJ2MupsmAAAA
</script>
```

The library will automatically detect the compressed format and decompress it before parsing the configuration.

### Root Object

| Property | Type | Description |
|----------|------|-------------|
| `pages` | `ReportPage[]` | An array of page definitions. |
| `modals` | `ReportModal[]` | Optional. An array of global modal definitions. |
| `datasets` | `Record<string, Dataset>` | A dictionary of datasets used by the visuals. |

### Datasets

Datasets are defined in the `datasets` object. The key is the `datasetId` referenced by visuals.

| Property | Type | Description |
|----------|------|-------------|
| `id` | `string` | The unique ID of the dataset. Auto-filled from the dictionary key when omitted (0.3+). |
| `data` | `any[]` | The actual data records (can be empty if using compression). |
| `columns` | `string[]` | Array of column names. |
| `dtypes` | `string[]` | Array of data types for columns (e.g., 'string', 'number'). |
| `format` | `string` | Data format: `'table'`, `'records'`, `'list'`, or `'record'`. |
| `compression` | `string` | Optional. Set to `'gzip'` to enable decompression. |
| `compressedData` | `string` | Optional. The ID of a script tag containing the base64-encoded gzip data. |
| `source` | `string` | Optional (0.3+). Makes this a **derived dataset** computed from another dataset at load time (see [Derived Datasets](#derived-datasets)). |
| `filter` | `FilterExpression` | Optional (0.3+). Filter applied to the source rows (derived datasets only). |
| `aggregate` | `AggregateSpec` | Optional (0.3+). Aggregation applied after the filter (derived datasets only). |

**Example Dataset (Records Format):**
```json
"salesData": {
    "id": "salesData",
    "format": "records",
    "columns": ["Region", "Sales"],
    "dtypes": ["string", "number"],
    "data": [
        { "Region": "North", "Sales": 1000 },
        { "Region": "South", "Sales": 1500 }
    ]
}
```

**Example Dataset (Table Format):**
```json
"inventoryData": {
    "id": "inventoryData",
    "format": "table",
    "columns": ["Item", "Quantity"],
    "dtypes": ["string", "number"],
    "data": [
        ["Widget A", 500],
        ["Widget B", 300]
    ]
}
```

## Data Compression

For large datasets, you can use gzip compression to reduce the HTML file size. The library uses the built-in `DecompressionStream` API (available in modern browsers) to decompress data on the fly.

### How to use Compression

1.  **Compress your data**: Gzip your JSON data and encode it as a Base64 string.
2.  **Store in a separate script tag**: Place the Base64 string in a `<script>` tag with `type="text/b64-gzip"`.
3.  **Reference the script ID**: In your `report-data` JSON, set `compression: "gzip"` and `compressedData` to the ID of that script tag.

**Example:**

```html
<!-- The compressed data -->
<script id="large-data-source" type="text/b64-gzip">
H4sIAAAAAAAACouOVvIsSc1VcFTSMTQwiNWBcp2UdIyQuM5KOsYGBrGxAEZgS5ouAAAA
</script>

<!-- The report configuration -->
<script id="report-data" type="application/json">
{
    "datasets": {
        "compressedDataset": {
            "id": "compressedDataset",
            "format": "table",
            "columns": ["Item", "Value"],
            "dtypes": ["string", "number"],
            "compression": "gzip",
            "compressedData": "large-data-source",
            "data": []
        }
    }
}
</script>
```

### Memory Management (GC)

Decompressing large strings can consume significant memory. You can instruct the library to clear the source strings from memory once decompression is complete by adding a meta tag to your `<head>`:

```html
<meta name="gc-compressed-data" content="true">
```

When this tag is present, the library will:
1.  Clear the `textContent` of any script tags referenced by `compressedData`.
2.  Delete the `compressedData` property from the dataset objects.

This allows the browser's Garbage Collector to reclaim the memory used by the large Base64 strings.

## Pages

Each page in the `pages` array represents a tab in the report.

| Property | Type | Description |
|----------|------|-------------|
| `title` | `string` | The title of the tab/page. |
| `description` | `string` | Optional description. |
| `lastUpdated` | `string` | ISO date string. |
| `rows` | `Layout[]` | An array of layout rows. |

### Layouts & Visuals

The `rows` array contains layout objects. Layouts can contain other layouts or visuals.

#### Common Properties (All Elements)

| Property | Type | Description |
|----------|------|-------------|
| `type` | `string` | The type of component (e.g., `layout`, `card`, `kpi`). |
| `id` | `string` | Optional. Stable element id. Every visual with an id is a DOM anchor (0.4+), can be a link target, and can persist view state. |
| `padding` | `number` | Padding in pixels (default 0; zero is respected as of 0.3). |
| `margin` | `number` | Margin in pixels (default 0 as of 0.3 — spacing is owned by layout `gap`). |
| `border` | `boolean/string` | CSS border string (e.g. `"2px dashed #f59e0b"`) or boolean to enable the theme default. CSS strings honored on layouts and visuals since 0.4.1. |
| `shadow` | `boolean/string` | CSS box-shadow string or boolean to enable the theme default. CSS strings honored on layouts and visuals since 0.4.1. |
| `flex` | `number` | Flex grow value (`flex: 0` is respected as of 0.3). |
| `modalId` | `string` | Optional. The ID of a modal to open when the element is hovered and the expand icon is clicked. |
| `filter` | `FilterExpression` | Optional (0.3+). Client-side filter applied to this visual's view of its dataset. See [Filtering & Aggregation](#filtering--aggregation-03). |
| `aggregate` | `AggregateSpec` | Optional (0.3+). Client-side aggregation applied after `filter`. |

#### Layout Component (`type: "layout"`)

| Property | Type | Description |
|----------|------|-------------|
| `direction` | `'row' \| 'column' \| 'grid'` | Direction of children. |
| `columns` | `number` | Optional. Number of columns for grid layout (default: 3). |
| `gap` | `string \| number` | Optional. Gap between elements (default: `10px` as of 0.3). |
| `wrap` | `boolean` | Optional (0.3+). Enables flex wrapping for row/column layouts. |
| `align` | `string` | Optional (0.3+). CSS `align-items` for row/column layouts. |
| `justify` | `string` | Optional (0.3+). CSS `justify-content` for row/column layouts. |
| `minChildWidth` | `number \| string` | Optional (0.3+). Responsive grid: `repeat(auto-fit, minmax(X, 1fr))`. Numbers are px. |
| `flex` | `number` | Optional. Flex grow (default 1; honored as of 0.3). |
| `title` | `string` | Optional. Rendered above the content in all directions. |
| `children` | `Array` | Array of child elements (Layouts or Visuals). Untyped objects with a `children` array also render as layouts (0.3+). |

#### Visual Components

All visuals require a `datasetId` pointing to a key in the `datasets` object. Most visuals also support an optional `otherElements` array for adding annotations like trend lines, markers, and custom axes.

**1. Card (`type: "card"`)**

Displays a simple text card.

| Property | Type | Description |
|----------|------|-------------|
| `title` | `string` | Optional title header. |
| `text` | `string` | The main content text. |

`title` and `text` support a template syntax using `{{ ... }}` placeholders. The contents of each placeholder are evaluated as a **JavaScript expression**.

Available variables inside `{{ ... }}`:

- `datasets`: the datasets object from `report-data`
- `props`: reserved for future use (currently `{}` for cards)
- `helpers`: helper functions
- `row` (0.4+): when the card is inside a modal opened via a table's `rowModalId`, the clicked row's values (e.g. `{{ row.Region }}`, `{{ formatCurrency(row.Amount) }}`)

Convenience: the following helper functions are also available directly (they are destructured from `helpers`):

- `count(datasetId)`
- `sum(datasetId, column)`, `avg(datasetId, column)`, `min(datasetId, column)`, `max(datasetId, column)` (these operate on `table`-format datasets)
- `formatNumber(value, digits?)`, `formatPercent(value, digits?)`, `formatCurrency(value, symbol?, digits?)`

⚠️ **Security note:** because `report-data` is embedded in the HTML, this means your report configuration can execute arbitrary code in the viewer’s browser. Only use this if the HTML/JSON is trusted.

**Example Card with computed text:**

```json
{
    "type": "card",
    "title": "Dataset Summary",
    "text": "Rows in tasksData: {{count('tasksData')}}"
}
```

You can also provide an object form if you want the whole value to be a single expression:

```json
{
    "type": "card",
    "title": { "expr": "'Rows: ' + count('tasksData')" },
    "text": { "expr": "formatCurrency(sum('kpiData', 'Value'), '$', 0)" }
}
```

**2. KPI (`type: "kpi"`)**

Displays a Key Performance Indicator with optional comparison and breach status.

| Property | Type | Description |
|----------|------|-------------|
| `valueColumn` | `string \| number` | Column for the main value. |
| `comparisonColumn` | `string \| number` | Column for the comparison value (e.g., yesterday). |
| `comparisonRowIndex` | `number` | Index of the row in the dataset to use for comparison. Supports negative indices (e.g., -1 for last row). If not provided, uses the same row as `rowIndex`. |
| `comparisonText` | `string` | The comparison text to show alongside the comparison value. Ex. ("Last Month", "Yesterday", etc.) |
| `rowIndex` | `number` | Index of the row in the dataset to display (default 0). Supports negative indices (e.g., -1 for last row). |
| `format` | `'number' \| 'currency' \| 'percent' \| 'date' \| 'hms'` | Formatting style. |
| `roundingPrecision` | `number` | The rounding precision for the output |
| `currencySymbol` | `string` | Symbol for currency (default '$'). |
| `goodDirection` | `'higher' \| 'lower'` | Which direction is considered "good". |
| `breachValue` | `number` | Value that triggers a breach indicator. |
| `warningValue` | `number` | Value that triggers a warning indicator. |
| `title` | `string` | Optional title for the KPI card. |
| `description` | `string` | Optional description text displayed at the bottom. |
| `width` | `number` | Optional width for the KPI card. |
| `height` | `number` | Optional height for the KPI card. |

**3. Pie Chart (`type: "pie"`)**

| Property | Type | Description |
|----------|------|-------------|
| `categoryColumn` | `string \| number` | Column for slice labels. |
| `valueColumn` | `string \| number` | Column for slice size. |
| `innerRadius` | `number` | For donut chart style. |
| `showLegend` | `boolean` | Whether to show the legend. |

**4. Stacked / Clustered Bar Chart (`type: "stackedBar"`, `type: "clusteredBar"`)**

| Property | Type | Description |
|----------|------|-------------|
| `xColumn` | `string \| number` | Column for X-axis categories. |
| `yColumns` | `string[]` | Array of columns for Y-axis values (series). |
| `xAxisLabel` | `string` | Label for X-axis. |
| `yAxisLabel` | `string` | Label for Y-axis. |
| `showLegend` | `boolean` | Whether to show the legend. |
| `showLabels` | `boolean` | Whether to show value labels on bars. |
| `threshold` | `ThresholdConfig` | Optional. Threshold configuration for pass/fail coloring (clusteredBar only). See [Threshold Configuration](#threshold-configuration). |

**5. Scatter Plot (`type: "scatter"`)**

| Property | Type | Description |
|----------|------|-------------|
| `xColumn` | `string \| number` | Column for X-axis values (numeric). |
| `yColumn` | `string \| number` | Column for Y-axis values (numeric). |
| `categoryColumn` | `string \| number` | Optional column for coloring points by category. |
| `showTrendline` | `boolean` | Whether to show a linear regression trendline. |
| `showCorrelation` | `boolean` | Whether to show correlation stats (r, r², equation). |
| `pointSize` | `number` | Size of the data points (default 5). |
| `xAxisLabel` | `string` | Label for X-axis. |
| `yAxisLabel` | `string` | Label for Y-axis. |

**6. Table (`type: "table"`)**

Displays data in a tabular format with sorting, filtering, grouping, export, and pagination.

| Property | Type | Description |
|----------|------|-------------|
| `columns` | `string[]` | Optional array of column names to display. Defaults to all. |
| `pageSize` | `number` | Number of rows per page (default 10). While grouped, groups per page. |
| `tableStyle` | `'plain' \| 'bordered' \| 'alternating'` | Visual style of the table (default 'plain'). |
| `showSearch` | `boolean` | Whether to show the search bar (default true). |
| `title` | `string` | Optional title for the table. |
| `sortable` | `boolean` | (0.3+) Type-aware sorting; Shift+click for multi-column sort (default true). |
| `defaultSort` | `{column, direction}[]` | (0.3+) Initial sort, e.g. `[{"column": "Amount", "direction": "desc"}]`. |
| `hiddenColumns` | `string[]` | (0.3+) Columns hidden initially. |
| `allowColumnHiding` | `boolean` | (0.3+) Runtime Columns menu (default true). |
| `groupBy` | `string` | (0.3+) Initial grouping column (collapsible groups). |
| `groupAggregates` | `{column, fn, as?}[]` | (0.3+) Per-group aggregates shown in group headers. |
| `groupsCollapsed` | `boolean` | (0.3+) Whether groups start collapsed (default false). |
| `enableExport` | `boolean` | (0.3+) CSV export and clipboard copy (default true). |
| `exportFileName` | `string` | (0.3+) File name for CSV export. |
| `contextMenu` | `boolean` | (0.3+) Right-click menus on headers/cells (default true). |
| `maxHeight` | `number` | (0.3+) Max body height in px; enables scrollable body + sticky header. |
| `stickyHeader` | `boolean` | (0.3+) Defaults to true when `maxHeight` is set. |
| `totalRow` | `boolean \| {label?, fns?}` | (0.4+) Grand-total row over the filtered data (all pages). `true` sums numeric columns, or `fns` maps column names to aggregate fns, e.g. `{"Amount": "avg"}`. Display-only. |
| `totalColumn` | `boolean \| {label?, columns?}` | (0.4+) Per-row total column. `true` sums numeric visible columns, or pick `columns`. Display-only. |
| `rowModal` | `boolean` | (0.4+) Double-click a row (or right-click → Open details) to open a built-in detail modal. |
| `rowModalColumns` | `string[]` | (0.4+) Columns listed in the built-in detail modal. |
| `rowModalTitle` | `string` | (0.4+) Title of the built-in detail modal (default 'Details'). |
| `rowModalId` | `string` | (0.4+) Open a custom modal from `modals` instead; cards inside can use `{{ row.ColumnName }}` templates. Implies `rowModal`. |
| `persistState` | `boolean` | (0.4+) Persist runtime sort/hidden-columns/grouping to localStorage. Defaults to true when the table has an `id`. |
| `columnFormats` | `Record<string, ColumnFormat \| string>` | (0.4.1+) Per-column display formats — see [Column & Conditional Formatting](#column--conditional-formatting-041). |
| `conditionalFormats` | `ConditionalFormat[]` | (0.4.1+) Highlight rules — see [Column & Conditional Formatting](#column--conditional-formatting-041). |

Set `contextMenu: false`, `enableExport: false`, `allowColumnHiding: false`, `sortable: false` to fully restore pre-0.3 behavior.

**7. Checklist (`type: "checklist"`)**

Displays a list of tasks with completion status and due date warnings. Since 0.4.1 it is
built on the shared table infrastructure and supports the full table UX (sorting, column
hiding, export, context menus, sticky header, row modals, persistent state) plus status
filter chips and a completion progress bar. Read-only by design — status always comes
from the dataset.

| Property | Type | Description |
|----------|------|-------------|
| `statusColumn` | `string` | **Required**. Column name containing boolean/truthy value for completion. |
| `warningColumn` | `string` | Optional. Column name containing a date to check against. |
| `warningThreshold` | `number` | Optional. Days before due date to trigger warning (default 3). |
| `columns` | `string[]` | Optional array of column names to display. |
| `pageSize` | `number` | Number of rows per page (default 10). |
| `showSearch` | `boolean` | Whether to show the search bar (default true). |
| `sortable` | `boolean` | (0.4.1+) Type-aware sorting; Shift+click multi-sort (default true). The Status header sorts by urgency. |
| `defaultSort` | `{column, direction}[]` | (0.4.1+) Initial sort. Accepts the special column `"status"` (urgency rank: overdue → due soon → pending → complete). Default: urgency, then due date. |
| `hiddenColumns` | `string[]` | (0.4.1+) Columns hidden initially. |
| `allowColumnHiding` | `boolean` | (0.4.1+) Runtime Columns menu (default true). |
| `enableExport` | `boolean` | (0.4.1+) CSV export / clipboard copy (default true). Exports include a derived `Status` column. |
| `exportFileName` | `string` | (0.4.1+) File name for CSV export. |
| `contextMenu` | `boolean` | (0.4.1+) Right-click context menus (default true). |
| `maxHeight` | `number` | (0.4.1+) Max body height in px; enables scrollable body + sticky header. |
| `stickyHeader` | `boolean` | (0.4.1+) Defaults to true when `maxHeight` is set. |
| `rowModal` | `boolean` | (0.4.1+) Built-in row detail modal on double-click; leads with the status. |
| `rowModalId` | `string` | (0.4.1+) Open a custom modal from `modals` instead. Implies `rowModal`. |
| `rowModalColumns` | `string[]` | (0.4.1+) Columns listed in the built-in detail modal. |
| `rowModalTitle` | `string` | (0.4.1+) Title of the built-in detail modal (default 'Details'). |
| `showStatusFilter` | `boolean` | (0.4.1+) Status filter chips with counts — All / Pending / Due Soon / Overdue / Complete (default true). Clicking a chip hides/shows that status (persisted). |
| `showProgress` | `boolean` | (0.4.1+) Completion progress bar next to the "X / Y Completed" summary (default true). |
| `hideCompleted` | `boolean` | (0.4.1+) Start with completed tasks hidden — the Complete chip toggled off (default false). |
| `persistState` | `boolean` | (0.4.1+) Persist view state to localStorage. Defaults to true when the checklist has an `id`. |
| `columnFormats` | `Record<string, ColumnFormat \| string>` | (0.4.1+) Per-column display formats — see [Column & Conditional Formatting](#column--conditional-formatting-041). |
| `conditionalFormats` | `ConditionalFormat[]` | (0.4.1+) Highlight rules — see [Column & Conditional Formatting](#column--conditional-formatting-041). |

**8. Histogram (`type: "histogram"`)**

Displays the distribution of a numerical dataset.

| Property | Type | Description |
|----------|------|-------------|
| `column` | `string \| number` | Column containing the numerical values to bin. |
| `bins` | `number` | Number of bins to divide the data into (default 10). |
| `color` | `string` | Color of the bars (default "#69b3a2"). |
| `showLabels` | `boolean` | Whether to show count labels on top of bars. |
| `xAxisLabel` | `string` | Label for X-axis. |
| `yAxisLabel` | `string` | Label for Y-axis. |

**9. Heatmap (`type: "heatmap"`)**

Displays data in a matrix where values are represented by colors.

| Property | Type | Description |
|----------|------|-------------|
| `xColumn` | `string \| number` | Column for X-axis categories. |
| `yColumn` | `string \| number` | Column for Y-axis categories. |
| `valueColumn` | `string \| number` | Column for the heat value. |
| `showCellLabels` | `boolean` | Whether to show the value text inside cells. |
| `minValue` | `number` | Optional minimum value for color scale. |
| `maxValue` | `number` | Optional maximum value for color scale. |
| `color` | `string \| string[]` | Color scheme or array of colors for the heat scale. Supports D3 interpolator names (e.g., "Viridis", "Magma", "YlOrRd") or an array of color strings for custom interpolation. |
| `xAxisLabel` | `string` | Label for X-axis. |
| `yAxisLabel` | `string` | Label for Y-axis. |

**Example Heatmap with custom colors:**

```json
{
    "type": "heatmap",
    "datasetId": "salesMatrix",
    "xColumn": "Month",
    "yColumn": "Region",
    "valueColumn": "Sales",
    "color": "Viridis"
}
```

**10. Line Chart (`type: "line"`)**

Displays data points connected by straight or smooth lines.

| Property | Type | Description |
|----------|------|-------------|
| `xColumn` | `string \| number` | Column for X-axis values (usually time or category). |
| `yColumns` | `string \| string[]` | Column(s) for Y-axis values (series). |
| `smooth` | `boolean` | Whether to use a smooth curve instead of straight lines. |
| `showLegend` | `boolean` | Whether to show the legend. |
| `showLabels` | `boolean` | Whether to show value labels on points. |
| `minY` | `number` | Optional minimum Y-axis value. |
| `maxY` | `number` | Optional maximum Y-axis value. |
| `colors` | `string[]` | Array of colors for the lines. |
| `xAxisLabel` | `string` | Label for X-axis. |
| `yAxisLabel` | `string` | Label for Y-axis. |
| `threshold` | `ThresholdConfig` | Optional. Threshold configuration for pass/fail coloring. See [Threshold Configuration](#threshold-configuration). |

**Example Line Chart with Threshold:**

```json
{
    "type": "line",
    "datasetId": "salesData",
    "xColumn": "Month",
    "yColumns": ["Revenue"],
    "smooth": true,
    "threshold": {
        "value": 5000,
        "passColor": "#22c55e",
        "failColor": "#ef4444",
        "mode": "above",
        "showLine": true,
        "blendWidth": 8
    }
}
```

**11. Area Chart (`type: "area"`)**

Displays data as filled areas below lines. Supports all the same features as Line Chart plus additional fill options.

| Property | Type | Description |
|----------|------|-------------|
| `xColumn` | `string \| number` | Column for X-axis values (usually time or category). |
| `yColumns` | `string \| string[]` | Column(s) for Y-axis values (series). |
| `smooth` | `boolean` | Whether to use a smooth curve instead of straight lines. |
| `showLegend` | `boolean` | Whether to show the legend. |
| `showLabels` | `boolean` | Whether to show value labels on points. |
| `showLine` | `boolean` | Whether to show the line stroke on top of the area (default: true). |
| `showMarkers` | `boolean` | Whether to show interactive marker points (default: true). |
| `fillOpacity` | `number` | Opacity of the area fill, 0-1 (default: 0.3). |
| `minY` | `number` | Optional minimum Y-axis value. |
| `maxY` | `number` | Optional maximum Y-axis value. |
| `colors` | `string[]` | Array of colors for the areas. |
| `xAxisLabel` | `string` | Label for X-axis. |
| `yAxisLabel` | `string` | Label for Y-axis. |
| `threshold` | `ThresholdConfig` | Optional. Threshold configuration for pass/fail coloring. See [Threshold Configuration](#threshold-configuration). |

**Example Area Chart:**

```json
{
    "type": "area",
    "datasetId": "temperatureData",
    "xColumn": "Date",
    "yColumns": ["Temperature"],
    "smooth": true,
    "fillOpacity": 0.4,
    "showMarkers": true,
    "threshold": {
        "value": 75,
        "passColor": "#22c55e",
        "failColor": "#ef4444",
        "mode": "below",
        "showLine": true,
        "applyTo": "both"
    }
}
```

**12. Box Plot (`type: "boxplot"`)****

Displays the distribution of data through their quartiles. Supports two modes: raw data calculation and pre-calculated values.

| Property | Type | Description |
|----------|------|-------------|
| `dataColumn` | `string \| number` | **Data Mode**. Column containing raw numerical values to calculate box stats. |
| `categoryColumn` | `string \| number` | Optional. Column to group data by (Data Mode) or label rows (Pre-calc Mode). |
| `minColumn` | `string \| number` | **Pre-calc Mode**. Column for minimum value. |
| `q1Column` | `string \| number` | **Pre-calc Mode**. Column for first quartile. |
| `medianColumn` | `string \| number` | **Pre-calc Mode**. Column for median. |
| `q3Column` | `string \| number` | **Pre-calc Mode**. Column for third quartile. |
| `maxColumn` | `string \| number` | **Pre-calc Mode**. Column for maximum value. |
| `meanColumn` | `string \| number` | Optional. Column for mean value. |
| `direction` | `'vertical' \| 'horizontal'` | Orientation of the boxes (default 'vertical'). |
| `showOutliers` | `boolean` | Whether to show outliers as rhombus shapes (Data Mode only, default true). |
| `color` | `string \| string[]` | Fill color for the boxes. Supports a single color string, an array of colors, or D3 scheme names (e.g., "Category10", "Tableau10"). (default "#69b3a2"). |
| `xAxisLabel` | `string` | Label for X-axis. |
| `yAxisLabel` | `string` | Label for Y-axis. |

**Example Box Plot (Raw Data Mode):**

```json
{
    "type": "boxplot",
    "datasetId": "surveyResults",
    "dataColumn": "Score",
    "categoryColumn": "Department",
    "color": "Tableau10",
    "direction": "horizontal"
}
```

**13. Gauge (`type: "gauge"`)**

Displays a gauge/speedometer visualization with an animated needle, optional range bands, and value display. The gauge animates smoothly when first rendered.

| Property | Type | Description |
|----------|------|-------------|
| `valueColumn` | `string \| number` | Column containing the gauge value (default: 0). |
| `rowIndex` | `number` | Row index to read the value from (default: 0). |
| `minValue` | `number` | Minimum value for the gauge scale (default: 0). |
| `maxValue` | `number` | Maximum value for the gauge scale (default: 100). |
| `title` | `string` | Optional title displayed above the gauge. |
| `thickness` | `number` | Arc thickness in pixels (default: 24). |
| `startAngle` | `number` | Start angle in radians (default: -π/2, i.e., -90°). |
| `endAngle` | `number` | End angle in radians (default: π/2, i.e., 90°). |
| `ranges` | `GaugeRange[]` | Optional array of range bands with colors. |
| `trackColor` | `string` | Background track color when no ranges are defined. |
| `valueColor` | `string` | Color for the value arc when no ranges are defined. |
| `needleColor` | `string` | Color of the needle (default: `var(--dl2-text-main)`). |
| `showNeedle` | `boolean` | Whether to show the needle (default: true). |
| `showValue` | `boolean` | Whether to show the center value (default: true). |
| `showLegend` | `boolean` | Whether to show a legend for the ranges (default: false). |
| `showMinMax` | `boolean` | Whether to show min/max labels (default: true). |
| `format` | `'number' \| 'currency' \| 'percent'` | Display format for the value. |
| `roundingPrecision` | `number` | Decimal precision for the value (default: 1). |
| `currencySymbol` | `string` | Currency symbol when format is 'currency' (default: '$'). |
| `unit` | `string` | Optional unit text displayed below the value. |
| `colors` | `ColorProperty` | Color palette for ranges (D3 scheme or array). |

**GaugeRange Object:**

| Property | Type | Description |
|----------|------|-------------|
| `from` | `number` | Start value of the range. |
| `to` | `number` | End value of the range. |
| `color` | `string` | Optional. Color for this range segment. |
| `label` | `string` | Optional. Label for this range. |
| `showPlus` | `boolean` | Optional. If true, displays the range as "{from}+" instead of "{from} - {to}" in the legend and tooltip. |

**Features:**
- **Animation:** The needle animates from 0 to the target value when the gauge first appears.
- **Interactivity:** Hovering over arc segments highlights them and shows a tooltip with range information.
- **Value Background:** A subtle background appears behind the value text when the needle might overlap it for better readability.
- **Legend:** Optionally displays a legend below the gauge with color indicators, labels, and range values with support for "X+" format.

**Example Gauge (Simple):**

```json
{
    "type": "gauge",
    "datasetId": "scoreData",
    "valueColumn": "Score",
    "title": "Performance Score",
    "minValue": 0,
    "maxValue": 100,
    "unit": "pts"
}
```

**Example Gauge with Ranges:**

```json
{
    "type": "gauge",
    "datasetId": "csatData",
    "valueColumn": "CSAT",
    "title": "Customer Satisfaction",
    "minValue": 0,
    "maxValue": 100,
    "unit": "%",
    "ranges": [
        { "from": 0, "to": 50, "color": "#e74c3c", "label": "Poor" },
        { "from": 50, "to": 75, "color": "#f39c12", "label": "Average" },
        { "from": 75, "to": 100, "color": "#27ae60", "label": "Good" }
    ]
}
```

**14. Tabs (`type: "tabs"`, alias `"tabgroup"`)** *(0.3+)*

A container visual holding tabs of arbitrary layouts/visuals. Works in rows, grids, and nested inside other tab groups. Does not require a dataset.

| Property | Type | Description |
|----------|------|-------------|
| `tabs` | `Tab[]` | **Required.** Array of tabs. Each tab: `{ "title": string, "children": LayoutElement[] }` or `{ "title": string, "layout": Layout }` (`layout` takes precedence). |
| `defaultTab` | `number` | Index of the initially active tab (default 0). |
| `title` | `string` | Optional title above the tab strip. |
| `id` | `string` | Enables active-tab persistence (0.4+) and link targeting. |
| `persistState` | `boolean` | (0.4+) Persist the active tab (default true when `id` is set). |

```json
{
    "type": "tabs",
    "id": "sales-tabs",
    "tabs": [
        { "title": "Chart", "children": [ { "type": "line", "datasetId": "sales", "xColumn": "Month", "yColumns": ["Revenue"] } ] },
        { "title": "Data",  "layout": { "type": "layout", "direction": "column", "children": [ { "type": "table", "datasetId": "sales" } ] } }
    ]
}
```

**15. Link (`type: "link"`)** *(0.4+)*

Navigation element. Requires `targetId` **or** `href`.

| Property | Type | Description |
|----------|------|-------------|
| `targetId` | `string` | Id of a visual to navigate to: switches to the containing page, activates containing tabs (nested included), scrolls to the visual, and flashes it. |
| `href` | `string` | External URL (opens in a new tab). |
| `label` | `string` | Link text (alias: `text`). Defaults to the target/href. |
| `linkStyle` | `'link' \| 'button'` | Rendering style (default 'link'). |

Every visual with an `id` is also a DOM anchor — plain `#visual-id` hash links (including in markdown cards and deep links on page load) navigate the same way.

## Filtering & Aggregation (0.3+)

Any visual may declare `filter` and/or `aggregate` props — several visuals can then show different slices of one shared dataset, entirely client-side. The same grammar powers [derived datasets](#derived-datasets).

### FilterExpression

A filter is either a **leaf condition** or a **boolean group**; groups nest arbitrarily.

```json
{ "column": "Region", "op": "eq", "value": "West" }

{ "and": [
    { "column": "Amount", "op": "gte", "value": 200 },
    { "or": [
        { "column": "Region", "op": "in", "values": ["South", "West"] },
        { "not": { "column": "Category", "op": "isNull" } }
    ]}
]}
```

| Field | Description |
|-------|-------------|
| `column` | Column name (or integer column index). |
| `op` | `eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `nin`, `contains`, `startsWith`, `endsWith`, `between`, `isNull`, `notNull`. |
| `value` | Scalar comparison value (or `[low, high]` for `between`). |
| `values` | Array for `in` / `nin` / `between`. |

Notes: string ops are case-insensitive; `between` is inclusive; `isNull` matches null/undefined/empty-string; comparisons on date columns are date-aware. Only `table` and `records` dataset formats can be filtered.

### AggregateSpec

Applied after `filter`; produces one row per group (records format).

```json
{
    "groupBy": ["Region"],
    "aggregates": [ { "column": "Amount", "fn": "sum", "as": "Total" } ]
}
```

| Field | Description |
|-------|-------------|
| `groupBy` | Non-empty array of column names/indices. |
| `aggregates[].column` | Column to aggregate (ignored by `count`). |
| `aggregates[].fn` | `sum`, `avg`, `min`, `max`, `count`, `countDistinct`, `first`, `last`. |
| `aggregates[].as` | Optional output column name. **Defaults to `"{fn}_{column}"`** (e.g. `sum_Amount`) — reference that name in the visual's column props. |

## Derived Datasets

*(0.3+)* A dataset may declare a `source` (plus optional `filter`/`aggregate`) to be computed from another dataset at load time. Chains are supported; cycles produce a console warning.

```json
"datasets": {
    "sales": { "id": "sales", "format": "records", "columns": ["Region", "Amount"], "data": [ ... ] },
    "westTotals": {
        "id": "westTotals",
        "source": "sales",
        "filter": { "column": "Region", "op": "eq", "value": "West" },
        "aggregate": { "groupBy": ["Region"], "aggregates": [ { "column": "Amount", "fn": "sum", "as": "Total" } ] }
    }
}
```

## Persistent View State (0.4+)

Runtime view changes — table sort / hidden columns / grouping, and the active tab of tab groups — are saved to localStorage and restored on reload, **per report and per visual `id`**.

- A visual persists only if it has an `id`; opt out with `persistState: false`.
- Reports are namespaced by `<meta name="report-id">` (falling back to the title, then the path). Set a stable `report-id` if the title may change.
- Give persisted visuals **stable, unique ids** — duplicate ids break persistence and links (the validator warns).
- Reset: right-click a visual header → **Reset view**, or the report-wide **Reset view** button in the headbar (appears only when saved customizations exist).

## Column & Conditional Formatting (0.4.1+)

Tables and checklists accept two display-formatting props.

### `columnFormats`

An object mapping **column name** (verbatim — never camelCased) → a format spec or a
shorthand kind string:

```json
"columnFormats": {
    "Amount": { "format": "currency", "digits": 0 },
    "Growth": { "format": "percent", "digits": 1 },
    "Due": "date"
}
```

| Property | Type | Description |
|----------|------|-------------|
| `format` | `'number' \| 'currency' \| 'percent' \| 'date' \| 'hms'` | The format kind. `percent` multiplies by 100 (store ratios); `hms` treats the value as seconds → `HH:MM:SS`. |
| `digits` | `number` | Optional decimal places (currency default 2, percent default 1). |
| `symbol` | `string` | Optional currency symbol (default `'$'`; currency only). |

Applies to body cells, total row/column, group aggregates (matched by the aggregate's `as` name), and row detail modals. Display-only: CSV export keeps raw values; clipboard copy matches the formatted view.

### `conditionalFormats`

An array of highlight rules evaluated per data row (raw values, before `columnFormats`):

```json
"conditionalFormats": [
    { "when": { "column": "Amount", "op": "gte", "value": 300 }, "style": "success" },
    { "when": { "column": "Amount", "op": "lt", "value": 100 }, "target": "row", "style": "error" },
    { "when": { "and": [ { "column": "Region", "op": "eq", "value": "West" },
                          { "column": "Units", "op": "gt", "value": 10 } ] },
      "columns": ["Units"], "css": { "fontWeight": 600 } }
]
```

| Property | Type | Description |
|----------|------|-------------|
| `when` | `FilterExpression` | **Required.** Standard filter grammar (see [FilterExpression](#filterexpression)). |
| `target` | `'cell' \| 'row'` | Default `'cell'` — styles the matching cell(s); `'row'` styles the whole row. |
| `columns` | `string[]` | Cell-target columns. Defaults to the `when` condition's own column; **required for compound (`and`/`or`/`not`) conditions**. |
| `style` | `string` | Named theme-aware preset: `'success'`, `'warning'`, `'error'`, `'info'`, `'muted'`. (Field is `style`, not `preset`.) |
| `css` | `Record<string, string \| number>` | Inline overrides layered over `style` (camelCase React style keys). |

First matching rule wins per target; one row rule and one cell rule can compose. A rule needs `style` and/or `css`. Totals/aggregate rows are exempt.

## Config Validation (0.3+)

On load, the config is validated and helpful `[datalys2]` console warnings are emitted for unknown visual types, missing datasets, bad column names, invalid filter ops, empty layouts, duplicate visual ids, unknown `rowModalId` / link `targetId`, malformed tabs, etc. Warnings never block rendering. Opt out with `<meta name="dl2-validate" content="false">`. 0.4.1 adds warnings for unknown `columnFormats` columns/kinds, malformed `conditionalFormats` (bad `when`, unknown preset/target, unresolvable columns), and column checks for `statusColumn`/`warningColumn`.

## Visual Elements

Visual elements are annotations or additional layers that can be added to most chart-based visuals using the `otherElements` property.

### Common Visual Element Properties

| Property | Type | Description |
|----------|------|-------------|
| `visualElementType` | `string` | The type of element (`trend`, `xAxis`, `yAxis`, `marker`, `label`). |
| `color` | `string` | Optional. Color of the element. |
| `lineStyle` | `string` | Optional. `'solid'`, `'dashed'`, or `'dotted'`. |
| `lineWidth` | `number` | Optional. Width of the line. |
| `label` | `string` | Optional. Text label for the element. |

### Element Types

#### 1. Trend Line (`visualElementType: "trend"`)

Displays a trend line based on provided coefficients.

| Property | Type | Description |
|----------|------|-------------|
| `coefficients` | `number[]` | Array of coefficients for the trend line equation (e.g., `[intercept, slope]`). |

Since 0.4.1 trends render on `line`, `area`, `stackedBar`, `clusteredBar`, `histogram`, and `scatter` charts (previously only scatter). On categorical X axes the coefficients are evaluated against the 0-based category index; numeric axes (scatter, histogram) use real axis units.

#### 2. Axis Line (`visualElementType: "xAxis" | "yAxis"`)

Displays a custom axis line at a specific value.

| Property | Type | Description |
|----------|------|-------------|
| `value` | `number | Date | string` | The value where the axis line should be placed. |

#### 3. Marker (`visualElementType: "marker"`)

Displays a marker at a specific value.

| Property | Type | Description |
|----------|------|-------------|
| `value` | `number | Date | string` | The value where the marker should be placed. |
| `size` | `number` | Optional. Size of the marker. |
| `shape` | `string` | Optional. `'circle'`, `'square'`, or `'triangle'`. |

#### 4. Label (`visualElementType: "label"`)

Displays a text label at a specific value.

| Property | Type | Description |
|----------|------|-------------|
| `value` | `number | Date | string` | The value where the label should be placed. |
| `fontSize` | `number` | Optional. Font size of the label. |
| `fontWeight` | `string` | Optional. `'normal'`, `'bold'`, etc. |

**Example Visual with Trend Line:**

```json
{
    "type": "line",
    "datasetId": "salesData",
    "xColumn": "Month",
    "yColumns": ["Revenue"],
    "otherElements": [
        {
            "visualElementType": "trend",
            "color": "#ff0000",
            "lineStyle": "dashed",
            "coefficients": [100, 5.5]
        }
    ]
}
```

## Threshold Configuration

Threshold configuration allows you to color chart elements (lines, areas, bars, markers) based on whether values pass or fail a threshold. This is useful for highlighting values that meet or miss targets.

### ThresholdConfig Object

| Property | Type | Description |
|----------|------|-------------|
| `value` | `number` | **Required**. The threshold value to compare against. |
| `passColor` | `string` | Color for values that pass the threshold (default: `#22c55e` green). |
| `failColor` | `string` | Color for values that fail the threshold (default: `#ef4444` red). |
| `mode` | `string` | How to determine pass/fail: `'above'` (default), `'below'`, or `'equals'`. |
| `showLine` | `boolean` | Whether to show a reference line at the threshold value (default: true). |
| `lineStyle` | `string` | Style of the threshold line: `'solid'`, `'dashed'` (default), or `'dotted'`. |
| `blendWidth` | `number` | Width of the color blend zone as percentage of chart width, 0-50 (default: 5). For line/area charts only. |
| `applyTo` | `string` | Which elements to apply threshold coloring to: `'both'` (default), `'markers'`, or `'lines'`. |

### Supported Visuals

- **Line Chart** (`type: "line"`) - Colors lines with gradient blending at crossings, markers by value
- **Area Chart** (`type: "area"`) - Colors areas and lines with gradient blending, markers by value
- **Clustered Bar Chart** (`type: "clusteredBar"`) - Colors each bar based on its value

### Mode Options

| Mode | Description |
|------|-------------|
| `'above'` | Values >= threshold pass (green), values < threshold fail (red) |
| `'below'` | Values <= threshold pass, values > threshold fail |
| `'equals'` | Only values exactly equal to threshold pass |

### applyTo Options

| Value | Description |
|-------|-------------|
| `'both'` | Apply threshold colors to both lines/areas and markers |
| `'markers'` | Only markers use threshold colors; lines/areas keep original series colors |
| `'lines'` | Only lines/areas use threshold colors; markers keep original series colors |

### Gradient Blending (Line/Area Charts)

For line and area charts, the color transitions smoothly at threshold crossing points. The `blendWidth` property controls how gradual this transition is:
- `0` = Hard edge at the crossing point
- `5` = Subtle blend (default)
- `10-15` = More gradual, visible fade

**Example: Line Chart with Threshold**

```json
{
    "type": "line",
    "datasetId": "performanceData",
    "xColumn": "Week",
    "yColumns": ["Score"],
    "threshold": {
        "value": 80,
        "passColor": "#22c55e",
        "failColor": "#ef4444",
        "mode": "above",
        "showLine": true,
        "lineStyle": "dashed",
        "blendWidth": 8,
        "applyTo": "both"
    }
}
```

**Example: Multi-Series with Markers Only**

When you have multiple series and want to preserve distinct line colors while showing pass/fail on markers:

```json
{
    "type": "line",
    "datasetId": "salesData",
    "xColumn": "Quarter",
    "yColumns": ["Electronics", "Clothing", "Home"],
    "threshold": {
        "value": 4000,
        "mode": "above",
        "applyTo": "markers"
    }
}
```

**Example: Clustered Bar Chart with Threshold**

```json
{
    "type": "clusteredBar",
    "datasetId": "salesData",
    "xColumn": "Quarter",
    "yColumns": ["Revenue"],
    "threshold": {
        "value": 5000,
        "passColor": "#22c55e",
        "failColor": "#ef4444",
        "mode": "above",
        "showLine": true
    }
}
```

## Modals

Modals allow you to display additional details or visualizations in an overlay without leaving the current page. They function similarly to pages, containing their own layouts and visuals.

### Defining Modals

Modals are defined in the global `modals` array in the root of your configuration.

| Property | Type | Description |
|----------|------|-------------|
| `id` | `string` | Unique identifier for the modal. |
| `title` | `string` | The title displayed in the modal header. |
| `description` | `string` | Optional description text. |
| `rows` | `Layout[]` | An array of layout rows to display inside the modal. |

**Example Modal Definition:**

```json
"modals": [
    {
        "id": "revenue-details",
        "title": "Revenue Breakdown",
        "description": "Detailed view of revenue by region.",
        "rows": [
            {
                "type": "layout",
                "children": [
                    {
                        "type": "table",
                        "datasetId": "regionalRevenue",
                        "title": "Regional Data"
                    }
                ]
            }
        ]
    }
]
```

### Triggering Modals

There are two ways to trigger a modal:

#### 1. Using `modalId` on any Element

You can add the `modalId` property to any layout or visual element. When the user hovers over that element, an "expand" icon will appear in the top-right corner. Clicking this icon will open the modal with the corresponding ID.

```json
{
    "type": "kpi",
    "title": "Total Revenue",
    "datasetId": "kpiData",
    "valueColumn": "Revenue",
    "modalId": "revenue-details"
}
```

#### 2. Using a Modal Trigger Button

You can also place a dedicated button in your layout by using the `modal` type directly.

| Property | Type | Description |
|----------|------|-------------|
| `type` | `string` | Must be `"modal"`. |
| `id` | `string` | The ID of the global modal to open. |
| `buttonLabel` | `string` | The text to display on the button. |

```json
{
    "type": "modal",
    "id": "revenue-details",
    "buttonLabel": "View Detailed Breakdown"
}
```

#### 3. From a Table Row (0.4+)

Set `rowModalId` on a table to open a custom modal when a row is double-clicked (or right-click → Open details). Cards inside the modal can reference the clicked row through `{{ row.ColumnName }}` templates:

```json
{
    "type": "table",
    "datasetId": "orders",
    "rowModalId": "order-detail"
},
...
"modals": [
    {
        "id": "order-detail",
        "title": "Order Details",
        "rows": [
            { "type": "layout", "children": [
                { "type": "card", "contentType": "md",
                  "title": "Order — {{ row.Region }}",
                  "text": "**Rep:** {{ row.Rep }}\n**Amount:** {{ formatCurrency(row.Amount) }}" }
            ]}
        ]
    }
]
```

## Example Configuration

```json
{
    "pages": [
        {
            "title": "Dashboard",
            "rows": [
                {
                    "type": "layout",
                    "direction": "row",
                    "children": [
                        {
                            "type": "kpi",
                            "datasetId": "kpiData",
                            "title": "Total Revenue",
                            "valueColumn": "Revenue",
                            "format": "currency",
                            "border": true,
                            "shadow": true
                        },
                        {
                            "type": "card",
                            "datasetId": "dummy", 
                            "title": "Info",
                            "text": "Revenue is up by 5% this week.",
                            "border": true
                        }
                    ]
                }
            ]
        }
    ],
    "datasets": {
        "kpiData": {
            "id": "kpiData",
            "format": "records",
            "columns": ["Revenue"],
            "data": [{ "Revenue": 50000 }]
        },
        "dummy": {
            "id": "dummy",
            "format": "records",
            "columns": [],
            "data": []
        }
    }
}
```
