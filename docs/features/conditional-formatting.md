# Conditional Formatting *(dl2 0.4.1+)*

Highlight cells or whole rows in [Table](../visuals/table.md) and
[Checklist](../visuals/checklist.md) with `conditional_formats=` — a list of
rules evaluated per data row using the standard
[filter grammar](filtering.md).

## Quick start

```python
from dl2_reports import ConditionalFormat, filters as F

page.add_row().add_table(
    "orders",
    conditional_formats=[
        ConditionalFormat(when=F.gte("Amount", 300), style="success"),
        ConditionalFormat(when=F.lt("Amount", 100), target="row", style="error"),
        ConditionalFormat(
            when=F.and_(F.eq("Region", "West"), F.gt("Units", 10)),
            columns=["Units"],                        # required for compound `when`
            css={"font_weight": 600, "background_color": "#fef3c7"},
        ),
    ],
)
```

## `ConditionalFormat`

| Field | Type | Description |
|-------|------|-------------|
| `when` | `dict` | **Required.** A [filter expression](filtering.md) — builders or plain dicts. Validated at construction. |
| `target` | `str` | `'cell'` (default — styles the matching cell(s)) or `'row'` (styles the whole row). |
| `columns` | `list[str]` | Cell-target columns to style. Defaults to the `when` condition's own column; **required for compound (`and`/`or`/`not`) conditions** — the constructor enforces this. |
| `style` | `str` | Named theme-aware preset: `'success'`, `'warning'`, `'error'`, `'info'`, `'muted'`. ⚠️ The field is `style`, **not** `preset`. |
| `css` | `dict` | Inline overrides layered on top of `style`. Keys are React style names; snake_case is converted (`background_color` → `backgroundColor`). |

Every rule needs `style` and/or `css` — the constructor raises `ValueError`
otherwise (the viewer would skip such a rule silently).

## Evaluation semantics

- Rules are evaluated per data row against **raw values** (before
  [`column_formats`](column-formatting.md) are applied).
- **First matching rule wins per target** — one `row` rule and one `cell`
  rule can compose on the same row.
- Totals and aggregate rows are exempt.
- Named presets are theme-aware (they adapt to light/dark).

## Plain-dict form

Dicts work everywhere shapes do, e.g.
`{"when": {"column": "Amount", "op": "gte", "value": 300}, "style": "success"}` —
the typed shape just validates eagerly.

## Related

- [Filtering](filtering.md) — the `when` grammar.
- [Column formatting](column-formatting.md) — value display formats.
- [Checklist](../visuals/checklist.md) — has built-in status coloring; rules
  layer on top.
