# Aggregation *(dl2 0.3+)*

Any visual accepts `aggregate=` — a client-side group-by applied **after** the
visual's [`filter=`](filtering.md), in the browser. One raw dataset can feed a
table of transactions, a pie of totals per region, and a bar of counts per
category — no pre-grouping in pandas, no duplicate data in the HTML.

## Quick start

```python
from dl2_reports import aggregates as A

row.add_bar(
    "sales",
    x_column="Region",
    y_columns=["sum_Amount"],     # default output name: "{fn}_{column}"
    aggregate=A.aggregate("Region", A.agg("Amount", "sum")),
)
```

## The aggregate spec

```python
{
    "groupBy": ["Region"],
    "aggregates": [{"column": "Amount", "fn": "sum", "as": "Total"}],
}
```

| Field | Description |
|-------|-------------|
| `groupBy` | Non-empty list of column names/indices. |
| `aggregates[].column` | Column to aggregate (ignored by `count`). |
| `aggregates[].fn` | One of the functions below. |
| `aggregates[].as` | Output column name. **Defaults to `"{fn}_{column}"`** (e.g. `sum_Amount`). |

The result is one row per group, in `records` format, containing the group-by
columns plus the aggregate output columns — **reference the output names** in
the visual's column props.

### Functions

`sum`, `avg`, `min`, `max`, `count`, `countDistinct`, `first`, `last`

## The `aggregates` builder module

```python
from dl2_reports import aggregates as A

A.agg("Amount", "sum")                    # {"column": "Amount", "fn": "sum"}
A.agg("Amount", "sum", as_="Total")       # named output column
A.aggregate("Region", A.agg("Amount", "sum"), A.agg("Amount", "avg"))
A.aggregate(["Region", "Category"], A.agg("Amount", "sum"))   # multi-column groupBy
```

Invalid function names raise `ValueError` at build time. The typed
`AggregateColumn("Amount", "sum", as_="Total")` shape is equivalent to
`A.agg(...)`.

`aggregates.validate_aggregate(spec)` checks a hand-written dict (accepts
`groupBy` or `group_by`).

## Worked example — three views of one dataset

```python
from dl2_reports import Pie, Table, aggregates as A, filters as F

report.add_df("orders", orders_df, compress=True)

page.add_row(
    Table("orders"),                                   # raw rows
    Pie("orders", category_column="Region", value_column="Total",
        aggregate=A.aggregate("Region", A.agg("Amount", "sum", as_="Total"))),
    Pie("orders", category_column="Region", value_column="Orders",
        filter=F.gte("Amount", 100),                   # filter runs first
        aggregate=A.aggregate("Region", A.agg("Region", "count", as_="Orders"))),
)
```

## Related sites

- **Per-visual:** `aggregate=` on any visual (this page).
- **Named dataset:** [`add_derived_dataset(..., aggregate=...)`](derived-datasets.md)
  when several visuals need the *same* grouped view.
- **Group headers in tables:** `group_aggregates=` on
  [Table](../visuals/table.md) shows per-group stats without collapsing rows.

## Build-time note

Aggregation runs in the browser; aggregated values are not available to
[`report.get_value()`](reading-values.md). Compute with pandas
(`df.groupby(...)`) if you need them while building.
