# Layouts

Layouts arrange visuals (and other layouts) in rows, columns, and grids. A
page's `add_row()` returns a `Layout`; layouts nest arbitrarily via
`add_layout()`.

## Quick start

```python
# A row of three visuals (v2 style: pass components directly)
page.add_row(kpi_a, kpi_b, kpi_c)

# Layout props
page.add_row(wrap=True, gap=16, justify="space-between")

# Responsive grid
page.add_row(direction="grid", min_child_width=250)

# Nesting
row = page.add_row()
left = row.add_layout("column", flex=1)
right = row.add_layout("column", flex=2)
```

## `page.add_row(*children, direction="row", **props)`

Adds a layout row to a page (or modal). Components may be passed directly;
a single leading string positional is treated as the direction (legacy:
`page.add_row("column")`).

## Layout properties

| Property | Type | Description |
|----------|------|-------------|
| `direction` | `str` | `'row'`, `'column'`, or `'grid'`. |
| `gap` | `int \| str` | Gap between children (viewer default `10px` since dl2 0.3). |
| `wrap` | `bool` | *(dl2 0.3+)* Flex wrapping for row/column layouts. |
| `align` | `str` | *(dl2 0.3+)* CSS `align-items` for row/column layouts. |
| `justify` | `str` | *(dl2 0.3+)* CSS `justify-content` for row/column layouts. |
| `columns` | `int` | Number of grid columns (viewer default 3). |
| `min_child_width` | `int \| str` | *(dl2 0.3+)* Responsive grid: `repeat(auto-fit, minmax(X, 1fr))`; numbers are px. |
| `flex` | `int` | Flex grow (viewer default 1; `flex=0` respected since dl2 0.3). |
| `title` | `str` | Rendered above the content. |
| `padding` / `margin` / `border` / `shadow` / `height` | | Container styling — same semantics as [common visual props](common-props.md). |

## Spacing model (dl2 0.3+)

Layouts own spacing: `gap` defaults to 10px and **visuals default to
`margin: 0`**. Prefer adjusting the layout's `gap` over per-visual margins.
`padding=0` / `margin=0` are respected (not treated as unset).

## Layout methods

| Method | Description |
|--------|-------------|
| `add(component)` | Add a constructed typed component / layout / tabs container; returns it (v2 entry point). |
| `add_layout(direction="row", **props)` | Nested layout. |
| `add_tabs(id=None, default_tab=None, title=None, **props)` | [Tabs container](../visuals/tabs.md). |
| `add_visual(type, dataset_id=None, visual=None, **kwargs)` | [Generic visual](../visuals/generic-visual.md). |
| `add_kpi / add_table / add_card / ...` | Legacy helpers, one per visual type. |
| `on_condition(condition)` | [Conditional wrapper](conditional-layout.md) — adds only when `condition` is `True`. |
| `remove_visual(visual)` | Remove a child visual. |

## Related

- [Tabs](../visuals/tabs.md) — tabbed containers holding layouts.
- [Common visual properties](common-props.md) — styling shared with visuals.
