# Datalys2 Reporting Documentation

This documentation guides you on how to create HTML reports using the Datalys2 Reporting library.

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

## The `report-data` Script

The core of the report configuration lives inside the `<script id="report-data" type="application/json">` tag. This JSON object must adhere to the `ApplicationData` structure.

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
| `id` | `string` | The unique ID of the dataset. |
| `data` | `any[]` | The actual data records (can be empty if using compression). |
| `columns` | `string[]` | Array of column names. |
| `dtypes` | `string[]` | Array of data types for columns (e.g., 'string', 'number'). |
| `format` | `string` | Data format: `'table'`, `'records'`, `'list'`, or `'record'`. |
| `compression` | `string` | Optional. Set to `'gzip'` to enable decompression. |
| `compressedData` | `string` | Optional. The ID of a script tag containing the base64-encoded gzip data. |

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
| `padding` | `number` | Padding in pixels. |
| `margin` | `number` | Margin in pixels. |
| `border` | `boolean/string` | CSS border or boolean to enable default. |
| `shadow` | `boolean/string` | CSS box-shadow or boolean to enable default. |
| `flex` | `number` | Flex grow value. |
| `modalId` | `string` | Optional. The ID of a modal to open when the element is hovered and the expand icon is clicked. |

#### Layout Component (`type: "layout"`)

| Property | Type | Description |
|----------|------|-------------|
| `direction` | `'row' \| 'column'` | Direction of children. |
| `children` | `Array` | Array of child elements (Layouts or Visuals). |

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
| `rowIndex` | `number` | Index of the row in the dataset to display (default 0). |
| `format` | `'number' \| 'currency' \| 'percent'` | Formatting style. |
| `currencySymbol` | `string` | Symbol for currency (default '$'). |
| `goodDirection` | `'higher' \| 'lower'` | Which direction is considered "good". |
| `breachValue` | `number` | Value that triggers a breach indicator. |
| `warningValue` | `number` | Value that triggers a warning indicator. |

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

Displays data in a tabular format with sorting, filtering, and pagination.

| Property | Type | Description |
|----------|------|-------------|
| `columns` | `string[]` | Optional array of column names to display. Defaults to all. |
| `pageSize` | `number` | Number of rows per page (default 10). |
| `tableStyle` | `'plain' \| 'bordered' \| 'alternating'` | Visual style of the table (default 'plain'). |
| `showSearch` | `boolean` | Whether to show the search bar (default true). |
| `title` | `string` | Optional title for the table. |

**7. Checklist (`type: "checklist"`)**

Displays a list of tasks with completion status and due date warnings.

| Property | Type | Description |
|----------|------|-------------|
| `statusColumn` | `string` | **Required**. Column name containing boolean/truthy value for completion. |
| `warningColumn` | `string` | Optional. Column name containing a date to check against. |
| `warningThreshold` | `number` | Optional. Days before due date to trigger warning (default 3). |
| `columns` | `string[]` | Optional array of column names to display. |
| `pageSize` | `number` | Number of rows per page (default 10). |
| `showSearch` | `boolean` | Whether to show the search bar (default true). |

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

**11. Box Plot (`type: "boxplot"`)**

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
