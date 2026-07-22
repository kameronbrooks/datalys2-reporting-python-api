# Reading Values Back

Read scalar values from your registered data while building the report —
useful for conditional layout, threshold checks, or derived metrics without
re-querying the original DataFrame. Plus `visual.copy()` for stamping
configured visuals.

## `report.get_value(data_source_name, column_name, row_index=-1)`

Query any registered dataset by name — no visual required:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_source_name` | `str` | (required) | The dataset name passed to `add_df()`. |
| `column_name` | `str` | (required) | The column to read. |
| `row_index` | `int` | `-1` | Row index; negatives count from the end (`-1` = last row). |

Raises `ValueError` for unknown datasets/columns, `IndexError` for
out-of-range rows, and `ValueError` for [derived datasets](derived-datasets.md)
(they exist only in the browser — compute with pandas instead).

```python
TARGET = 120_000
worst = min(report.get_value("sales", "revenue", i) for i in range(len(sales_df)))

if worst < TARGET:
    page.add_row().add_card(
        title="Warning: underperforming region detected",
        text=f"Lowest revenue is ${worst:,} — below the ${TARGET:,} target.",
        content_type="md",
    )
```

(Or use [`on_condition()`](conditional-layout.md) instead of the `if`.)

## `visual.get_value()`

Read the value a specific visual represents, from its backing DataFrame. The
visual must be in the report tree, and its props must include `row_index` and
`value_column` (so it fits [KPI](../visuals/kpi.md)- and
[Gauge](../visuals/gauge.md)-style visuals):

```python
kpi = page.add_row().add_kpi("sales", value_column="revenue", row_index=0,
                             title="Revenue – North", format="currency")
north_revenue = kpi.get_value()
```

## `visual.copy()`

Duplicate a visual — same type, dataset, props, and annotations, new unique
id. Mutate `copy.props` for what differs, then re-add with
`row.add_visual(copy.type, visual=copy)`:

```python
proto = row.add_kpi("sales", value_column="revenue", row_index=0,
                    title="Revenue – North", format="currency")

for i, region in enumerate(["South", "East", "West"], start=1):
    copy = proto.copy()
    copy.props["row_index"] = i
    copy.props["title"] = f"Revenue – {region}"
    row.add_visual(copy.type, visual=copy)
```

Each copy exposes `get_value()` once it's in the tree.

## What build-time reads can't see

`get_value()` reads the **original, unfiltered** DataFrame stored at
`add_df()` time. Client-side [`filter=`](filtering.md) /
[`aggregate=`](aggregation.md) / [formulas](formula-datasources.md) and
[derived datasets](derived-datasets.md) run in the browser and don't affect
it — use pandas for filtered/aggregated build-time values.

## Related

- [Conditional layout](conditional-layout.md) — act on the values you read.
- [Card templates](../visuals/card.md#template-syntax) — compute at *view*
  time instead.
