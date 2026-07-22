# Filtering *(dl2 0.3+)*

Any visual accepts `filter=` — a client-side filter applied to that visual's
view of its dataset, **in the browser**. Several visuals can show different
slices of one shared dataset with no extra data embedded in the HTML. The
same grammar powers [derived datasets](derived-datasets.md) and
[conditional formatting](conditional-formatting.md) rules.

## Quick start

```python
from dl2_reports import filters as F

row.add_table(
    "sales",
    filter=F.and_(F.gte("Amount", 200), F.isin("Region", ["South", "West"])),
)
```

Prefer writing pandas-style strings? See
[Formula datasources](formula-datasources.md):
`row.add_table("sales[Amount >= 200 and Region in ['South', 'West']]")`.

## The filter grammar

A filter expression is either a **leaf condition**:

```python
{"column": "Region", "op": "eq", "value": "West"}
```

or a **boolean group** (`and` / `or` / `not`), nested arbitrarily:

```python
{"and": [
    {"column": "Amount", "op": "gte", "value": 200},
    {"or": [
        {"column": "Region", "op": "in", "values": ["South", "West"]},
        {"not": {"column": "Category", "op": "isNull"}},
    ]},
]}
```

| Field | Description |
|-------|-------------|
| `column` | Column name (or integer column index). |
| `op` | One of the operators below. |
| `value` | Scalar comparison value. |
| `values` | List for `in` / `nin` / `between` (`[low, high]`). |

### Operators

| Op | Meaning |
|----|---------|
| `eq` / `neq` | Equal / not equal. |
| `gt` / `gte` / `lt` / `lte` | Ordered comparison (numeric/date aware). |
| `in` / `nin` | Value in / not in a list. |
| `contains` / `startsWith` / `endsWith` | Case-insensitive string match. |
| `between` | Inclusive range (`values=[low, high]`). |
| `isNull` / `notNull` | Null / undefined / empty-string checks. |

Semantics: string ops are case-insensitive; `between` is inclusive; `isNull`
matches null, undefined, and empty string; comparisons on date columns are
date-aware. Only `records` and `table` format datasets can be filtered.

## The `filters` builder module

Builders produce these plain dicts and **validate eagerly** — a bad operator
raises `ValueError` at build time instead of a silent console warning in the
browser.

```python
from dl2_reports import filters as F
```

| Builder | Filter |
|---------|--------|
| `F.eq(col, v)` / `F.neq(col, v)` | `eq` / `neq` |
| `F.gt(col, v)` / `F.gte(col, v)` / `F.lt(col, v)` / `F.lte(col, v)` | ordered comparisons |
| `F.isin(col, values)` / `F.notin(col, values)` | `in` / `nin` |
| `F.contains(col, s)` / `F.starts_with(col, s)` / `F.ends_with(col, s)` | string matches |
| `F.between(col, low, high)` | `between` |
| `F.is_null(col)` / `F.not_null(col)` | null checks |
| `F.where(col, op, value=None, values=None)` | any op, generic |
| `F.and_(*exprs)` / `F.or_(*exprs)` / `F.not_(expr)` | boolean groups |

Hand-written dicts are accepted anywhere builders are;
`filters.validate_filter(expr)` checks one explicitly.

## Where filters apply

| Site | Prop |
|------|------|
| Any visual | `filter=` ([common prop](common-props.md)) — runs before that visual's `aggregate=`. |
| Derived dataset | `report.add_derived_dataset(..., filter=...)` — see [Derived datasets](derived-datasets.md). |
| Conditional format rule | `ConditionalFormat(when=...)` — see [Conditional formatting](conditional-formatting.md). |
| Formula datasource | Compiled from the bracket expression — see [Formula datasources](formula-datasources.md). |

## Build-time vs view-time

`filter=` runs **in the browser**. Python-side helpers
([`report.get_value()`](reading-values.md), `add_trend()` auto-coefficients)
read the *unfiltered* source DataFrame. If you need the filtered values in
Python, filter with pandas first.
