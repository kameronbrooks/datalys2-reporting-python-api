# Migrating to the Typed API (Codemod)

A codemod ships with the package that rewrites legacy helper calls to the v2
typed component API. Built on **libcst**, so comments and formatting are
preserved. Migration is optional — the old helper API keeps working — and can
be done file-by-file.

## What it rewrites

```python
# before
row.add_kpi("sales", value_column="Revenue", format="currency")
row.add_line("sales", x_column="Month", y_columns=["Revenue"],
             threshold={"value": 5000, "mode": "above"})

# after
row.add(KPI("sales", value_column="Revenue", format="currency"))
row.add(Line("sales", x_column="Month", y_columns=["Revenue"],
             threshold=Threshold(value=5000, mode="above")))
```

- `row.add_<visual>(...)` → `row.add(<Component>(...))`
- Known literal-dict props are upgraded to typed shapes:
  `threshold=` → `Threshold(...)`, `total_row=` → `TotalRow(...)`,
  `default_sort=` → `[SortSpec(...)]`, …
- The `from dl2_reports import ...` line is managed automatically.

## Usage

```bash
pip install dl2-reports[migrate]                       # installs libcst

python -m dl2_reports.migrate my_report.py             # dry run: prints a unified diff
python -m dl2_reports.migrate my_report.py --write     # apply in place
python -m dl2_reports.migrate notebooks/ --write       # directories recurse into *.py and *.ipynb
```

`PATH` may be a `.py` file, a `.ipynb` notebook, or a directory (multiple
paths allowed).

## Known limitations

Left unchanged — all still supported by the package:

- Generic `add_visual("type", ...)` calls.
- `group_aggregates=` / `aggregates=` dicts (`as` is a Python keyword — use
  the [`aggregates.agg`](aggregation.md) builder).
- `column_formats=` dicts (keys are column names, values may be shorthand
  strings — left as-is).
- Dynamic patterns: helpers called via `getattr`, `**kwargs` splats,
  non-literal dicts.
- Notebook cells that fail to parse as pure Python (e.g. `%magics`) are
  skipped.

## After migrating

- Run your script — typed constructors will surface any prop typos the old
  API silently passed through (see [Linting](linting.md)).
- `on_condition(...)` chains keep working; note the
  [NullComponent](conditional-layout.md#nullcomponent-050) behavior change if
  you checked `is None`.

## Related

- [Getting started — the typed API](../getting-started.md#the-typed-component-api-v2)
- [Linting & validation](linting.md)
