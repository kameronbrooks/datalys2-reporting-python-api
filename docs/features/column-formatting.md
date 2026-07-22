# Column Formatting *(dl2 0.4.1+)*

Give [Table](../visuals/table.md) and [Checklist](../visuals/checklist.md)
columns display formats with `column_formats=` — a mapping of **column name**
→ `ColumnFormat`, dict, or shorthand kind string.

## Quick start

```python
from dl2_reports import ColumnFormat

page.add_row().add_table(
    "orders",
    column_formats={
        "Amount":  ColumnFormat("currency", digits=0),   # or {"format": "currency", "digits": 0}
        "Growth":  ColumnFormat("percent", digits=1),    # raw values are ratios (0.42 → 42.0%)
        "Due":     "date",                               # shorthand string
        "Runtime": "hms",                                # seconds → HH:MM:SS
    },
)
```

## `ColumnFormat`

| Field | Type | Description |
|-------|------|-------------|
| `format` | `str` | `'number'`, `'currency'`, `'percent'`, `'date'`, or `'hms'`. Invalid kinds raise `ValueError` at construction. |
| `digits` | `int` | Decimal places (viewer defaults: currency 2, percent 1). |
| `symbol` | `str` | Currency symbol (currency only; viewer default `'$'`). |

### Format kinds

| Kind | Behavior |
|------|----------|
| `number` | Plain number formatting. |
| `currency` | Symbol + thousands separators. |
| `percent` | **Multiplies by 100** — store ratios (`0.42` → `42.0%`). |
| `date` | Locale date rendering of date values. |
| `hms` | Treats the value as **seconds** → `HH:MM:SS`. |

## Where formats apply

Formats apply to body cells, the [total row/column](../visuals/table.md),
group aggregates (matched by the aggregate's `as` output name), and
[row detail modals](modals.md#row-detail-modals).

**Display-only:** CSV export keeps raw values; clipboard copy matches the
formatted view.

## Column-name keys are verbatim

The mapping's keys are column names and are **never** snake→camel converted —
`"my_column"` stays `"my_column"`. (The typed API wraps the mapping in
`RawDict` for you; do the same for your own column-keyed passthrough dicts.)

## Validation

The viewer warns about unknown columns and unknown format kinds in
`column_formats` — see [Linting](linting.md).

## Related

- [Conditional formatting](conditional-formatting.md) — value-driven
  highlighting on the same visuals.
- [KPI `format=`](../visuals/kpi.md) / [Gauge `format=`](../visuals/gauge.md)
  — the same kinds for single values.
