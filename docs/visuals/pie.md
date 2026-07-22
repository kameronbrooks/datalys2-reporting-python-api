# Pie / Donut (`type: "pie"`)

A pie chart showing each category's share of a total. Set `inner_radius` for a
donut.

> **Class:** `dl2_reports.Pie` · **Legacy helper:** `row.add_pie(...)` ·
> **Example:** [06_pie.py](../../examples/all_visuals/06_pie.py)

## Quick start

```python
from dl2_reports import Pie

page.add_row(
    Pie("share", category_column="Browser", value_column="Users",
        show_legend=True),
    Pie("share", category_column="Browser", value_column="Users",
        inner_radius=70, show_legend=True),          # donut
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `category_column` | `str \| int` | Column for slice labels. |
| `value_column` | `str \| int` | Column for slice size. |
| `inner_radius` | `int` | Inner radius in px — nonzero makes a donut. |
| `show_legend` | `bool` | Show the legend. |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Pies over raw (ungrouped) data

The dataset does **not** have to be pre-grouped. Attach an
[`aggregate=`](../features/aggregation.md) and the browser groups the rows
client-side; `value_column` then refers to the aggregate's *output* column:

```python
from dl2_reports import Pie, aggregates as A

# Sum Amount per Region — output column named by as_
Pie("orders",
    category_column="Region",
    value_column="Total",
    aggregate=A.aggregate("Region", A.agg("Amount", "sum", as_="Total")),
    show_legend=True)

# Slice size = row count per group ("count" ignores its column argument)
Pie("orders",
    category_column="Region",
    value_column="Orders",
    aggregate=A.aggregate("Region", A.agg("Region", "count", as_="Orders")))
```

Without `as_`, the output column is named `"{fn}_{column}"` (e.g.
`sum_Amount`). A `filter=` (or a formula datasource like
`Pie("orders[Amount >= 100]", ...)`) runs before the grouping.

## Related

- [Bar](bar.md) — better than a pie when categories are many or values are
  close.
- [Aggregation](../features/aggregation.md) — the client-side grouping used
  above.
