# Conditional Layout — `on_condition()`

`layout.on_condition(condition)` conditionally adds visuals at **report-build
time**. It evaluates a plain Python `bool` and either delegates the following
`add_*` call to the real layout or silently discards it — no `if` blocks
needed around layout code.

## Quick start

```python
TARGET = 120_000
worst = min(report.get_value("sales", "revenue", i) for i in range(len(sales_df)))

warning_row = page.add_row()
warning_row.on_condition(worst < TARGET).add_card(
    title="Warning: underperforming region detected",
    text=f"Lowest revenue is ${worst:,} — below the ${TARGET:,} target.",
)

# Toggle a chart with a flag
detail_row = page.add_row()
detail_row.on_condition(show_details).add_table("sales", title="Detail View")
```

## How it works

- `condition=True` → the call is forwarded exactly as if you had called
  `layout.add_*(...)` directly, and the created component is returned.
- `condition=False` → nothing is added, no element id is consumed, and a
  falsy `NullComponent` is returned.
- The wrapper itself is **not** a tree node — it never occupies a slot in the
  report tree regardless of the condition, so it doesn't disturb the id
  sequence of the compiled report.

All the layout's `add_*` methods work through it: typed components via
`.add(component)`, legacy helpers (`.add_card`, `.add_table`, …),
`.add_layout()`, `.add_tabs()`, `.add_visual()`.

## `NullComponent` (0.5.0+)

`on_condition(False).add_*` returns a chain-safe sentinel rather than `None`:

- **Falsy**, so `if result:` keeps working.
- Any further chained call — `.add_trend()`, `.add_element()`, nested
  `.add_tab().add_line(...)` — is silently absorbed instead of raising
  `AttributeError`:

```python
row.on_condition(flag).add_line("sales", x_column="Month",
                                y_columns=["Revenue"]).add_trend(color="red")
# safe whether flag is True or False
```

- `.props` returns `{}` and `.get_value()` returns `None`.

> Migrating pre-0.5 code: replace `is None` checks with truthiness checks
> (`if not result:`).

## Related

- [Reading values](reading-values.md) — `get_value()` supplies the conditions.
- [Layouts](layouts.md) — the methods being wrapped.
