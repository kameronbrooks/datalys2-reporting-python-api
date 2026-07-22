# Formula Datasources *(0.7.0+)*

Anywhere a dataset is referenced as an input — any visual's `dataset_id` or a
derived dataset's `source` — you can write a **pandas-style formula** instead
of building a `filter=` dict. Formulas are parsed with Python's `ast` module
at construction time and compile to the plain dataset id plus the standard
[filter grammar](filtering.md); nothing new reaches the report JSON, and
typos fail fast with `ValueError`.

## Quick start

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

## Supported forms inside the brackets

| Form | Compiles to |
|------|-------------|
| `==` `!=` `>` `>=` `<` `<=` (either operand order) | `eq` / `neq` / `gt` / `gte` / `lt` / `lte` |
| `Region in ['S', 'W']` / `not in` | `in` / `nin` |
| `100 <= Amount <= 200` | `between` (inclusive) |
| `Amount == None` / `is None` / `!= None` / `is not None` | `isNull` / `notNull` |
| `and`, `or`, `not` — or pandas-style `&`, `\|`, `~` | `and` / `or` / `not` groups |
| `.contains(x)`, `.startswith(x)`, `.endswith(x)`, `.isin([...])`, `.between(lo, hi)`, `.isnull()`/`.isna()`, `.notnull()`/`.notna()` (optional `.str` prefix) | the matching filter op |
| `[['Col1', 'Col2']]` | `columns` projection (table-like visuals only) |

Column references can be bare names (`Amount`), attribute style
(`sales.amount`), or subscript style for names that aren't Python identifiers
or are keywords: `sales[sales["Due Date"] > "2026-01-01"]`.

## Rules & gotchas

- **AND-combining:** a formula's filter AND-combines with an explicit
  `filter=` (formula first) — both constraints apply.
- **Projection scope:** `[[...]]` works on visuals that model `columns`
  ([Table](../visuals/table.md), [Checklist](../visuals/checklist.md)) and
  raises elsewhere — the viewer ignores `columns` on charts, and derived
  dataset sources support only filter + aggregate. Combining `[[...]]` with
  an explicit `columns=` raises (ambiguous).
- **Parenthesize `&`/`|`:** as in pandas, they bind tighter than comparisons —
  write `(Amount > 100) & (Units < 5)`. The unparenthesized form raises
  rather than mis-filtering.
- **Literals only:** values must be strings, numbers, booleans, `None`, or
  lists/tuples of those. Interpolate Python variables with an f-string
  *outside* the formula: `f"sales[Amount > {threshold}]"`.
- **Runs in the browser:** like `filter=`, formula filters are client-side —
  [`report.get_value()`](reading-values.md) and `add_trend()`
  auto-coefficients still read the unfiltered source DataFrame.
- Anything unsupported — arithmetic, calls on non-columns, column-to-column
  comparisons, variables — raises `ValueError` at construction time.

## Programmatic access

```python
from dl2_reports import parse_datasource

spec = parse_datasource("sales[Amount > 200][['Region']]")
spec.dataset_id   # "sales"
spec.filter       # {"column": "Amount", "op": "gt", "value": 200}
spec.columns      # ["Region"]
```

Plain dataset ids (and non-formula values, including legacy ids like
`"my-data"`) pass through verbatim.

## Related

- [Filtering](filtering.md) — the grammar formulas compile to.
- [Derived datasets](derived-datasets.md) — formula sources for named
  datasets.
