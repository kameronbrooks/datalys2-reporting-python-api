# Getting Started

`dl2-reports` builds interactive, self-contained HTML reports from pandas
DataFrames. You describe a report as a tree of pages, layout rows, and typed
visual components; `report.save()` compiles everything (data included) into a
single HTML file that runs the Datalys2 viewer from a CDN.

## Installation

```bash
pip install dl2-reports
```

Optional extras:

```bash
pip install dl2-reports[migrate]   # the legacy→typed-API codemod
```

`IPython` is required only for [Jupyter rendering](features/jupyter.md).

## A minimal report

```python
import pandas as pd
from dl2_reports import DL2Report, KPI, Table

report = DL2Report(title="My Report")

df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
report.add_df("my_data", df, compress=True)

page = report.add_page("Overview")
page.add_row(
    KPI("my_data", value_column="A", title="Metric A"),
    Table("my_data", page_size=10),
)

report.save("report.html")   # or report.show() in a notebook
```

## Report anatomy

```
DL2Report
├── datasets            add_df(), add_derived_dataset()
├── pages               add_page() → Page (one tab each)
│   └── rows            page.add_row() → Layout
│       └── children    visuals, nested layouts, tabs containers
└── modals              add_modal() → Modal (global overlays)
```

- **Datasets** are registered once on the report and referenced by id from any
  number of visuals — see [Datasets & compression](features/datasets.md).
- **Pages** become tabs across the top of the report.
- **Rows** are [layouts](features/layouts.md) (`row`, `column`, or `grid`
  direction) and can nest arbitrarily.
- **Visuals** are the leaves — every type has its own page under
  [visuals/](README.md#visuals).
- **Modals** are overlay pages triggered from visuals — see
  [Modals](features/modals.md).

## The typed component API (v2)

Since 0.5.0 the recommended way to add visuals is with **typed component
classes**, one class per visual, imported from the package root:

```python
from dl2_reports import (
    KPI, Table, Card, Pie, Bar, Line, Area, Scatter, Checklist,
    Histogram, Heatmap, Gauge, Boxplot, Tabs, Link, ModalButton,
)
```

plus typed shapes for structured props:

```python
from dl2_reports import (
    Threshold, SortSpec, TotalRow, TotalColumn, GaugeRange,
    AggregateColumn, Tab, ColumnFormat, ConditionalFormat,
)
```

Add components either by passing them to `page.add_row(...)` or with
`row.add(component)` (which returns the component for chaining):

```python
from dl2_reports import DL2Report, Line, Table, Tabs, Tab, Threshold, SortSpec, TotalRow

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

Why the typed API is better:

- **Typos fail fast.** `Table("sales", pagesize=20)` raises
  `TypeError: unknown prop 'pagesize' (did you mean 'page_size'?)` at
  construction — the JS viewer silently ignores unknown props, so a typo would
  otherwise be an invisible bug.
- **Autocomplete and type checking** work everywhere (the package ships
  `py.typed`).
- **`extra={...}`** passes unmodeled viewer props through explicitly when you
  need forward compatibility — see
  [Generic visual passthrough](visuals/generic-visual.md).

### Legacy helpers

The original `row.add_kpi(...)`, `row.add_table(...)`, … helpers keep working
unchanged — they delegate to the component classes, and unknown kwargs still
pass through (flagged by the [compile lint](features/linting.md)). A
[codemod](features/migration.md) can rewrite legacy call sites for you.

## Naming conventions

The Python API is `snake_case` everywhere (`page_size`, `x_column`,
`show_legend`); the compiled report JSON is `camelCase` (`pageSize`,
`xColumn`). The conversion is automatic. The exception is **column names used
as dict keys** (e.g. `total_row={"fns": {"My Column": "sum"}}`,
`column_formats=` keys) — those are preserved verbatim; wrap your own
column-keyed passthrough dicts in `dl2_reports.RawDict` to get the same
protection.

## Compiling, saving, showing

```python
html_str = report.compile()          # full HTML string (lints props, warns)
report.compile(strict=True)          # raise on unknown props instead
report.save("report.html")           # write to disk
report.show(height=800)              # render inline in Jupyter
```

See [Report configuration](features/report-configuration.md) for metadata,
`report_id`, CDN overrides, and compression defaults.

## Next steps

- Browse the [visual gallery](README.md#visuals) — every type has a runnable
  example script.
- Slice one dataset many ways with [filtering](features/filtering.md),
  [aggregation](features/aggregation.md), and
  [formula datasources](features/formula-datasources.md).
- Add [thresholds](features/thresholds.md) and
  [annotations](features/annotations.md) to charts.
- Wire up [modals](features/modals.md) and [links](visuals/link.md) for
  drill-down navigation.
