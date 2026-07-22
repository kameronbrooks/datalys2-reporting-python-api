# Derived Datasets *(dl2 0.3+)*

A derived dataset is **declared, not embedded**: it names a source dataset
plus an optional [filter](filtering.md) and [aggregate](aggregation.md), and
the browser computes it at load time. No extra data reaches the HTML — ideal
when several visuals need the same filtered/grouped view.

## `report.add_derived_dataset(name, source, filter=None, aggregate=None)`

```python
from dl2_reports import aggregates as A, filters as F

report.add_derived_dataset(
    "north_by_category",
    source="sales",
    filter=F.eq("Region", "North"),
    aggregate=A.aggregate("Category", A.agg("Amount", "sum", as_="Total")),
)
page.add_row().add_table("north_by_category")

# Equivalent with a formula source (0.7.0+):
report.add_derived_dataset(
    "north_by_category",
    source="sales[Region == 'North']",
    aggregate=A.aggregate("Category", A.agg("Amount", "sum", as_="Total")),
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Id of the derived dataset (what visuals reference). |
| `source` | `str` | Id of the dataset to derive from — or a [formula](formula-datasources.md) like `"sales[Amount > 100]"` (its filter AND-combines with `filter=`; `[[...]]` projection is **not** allowed here). |
| `filter` | `dict` | Filter applied to the source rows. |
| `aggregate` | `dict` | Aggregation applied after the filter. Output columns default to `"{fn}_{column}"` names unless `as` is set. |

Filters and aggregates are validated at call time (`ValueError` on bad
ops/fns).

## Chains and ordering

- **Chains are supported** — a derived dataset can use another derived
  dataset as its source. Cycles produce a console warning in the viewer.
- **Declaration order doesn't matter** — sources are checked at
  `compile()`, which raises if a source is unknown.

## Derived vs. per-visual `filter=`/`aggregate=`

| | Per-visual props | Derived dataset |
|---|---|---|
| Scope | One visual | Any number of visuals |
| Named id | No | Yes (`datasetId` in JSON) |
| Best for | A one-off slice | A shared view several visuals reference |

## Limitation: build-time reads

Derived values exist only in the browser.
[`report.get_value()`](reading-values.md) raises for derived datasets —
compute the equivalent with pandas if you need the value while building.

## Related

- [Filtering](filtering.md) · [Aggregation](aggregation.md) ·
  [Formula datasources](formula-datasources.md) ·
  [Datasets & compression](datasets.md)
