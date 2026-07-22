# Tabs (`type: "tabs"`) *(dl2 0.3+)*

A container visual holding named tabs, each backed by a full layout — so any
visual or nested layout works inside a tab. Tabs work in rows and grids and
can be nested inside other tab groups. No dataset required.

> **Class:** `dl2_reports.Tabs` (container) + `dl2_reports.Tab` (shape) ·
> **Legacy helper:** `row.add_tabs(...)` ·
> **Example:** [01_tabs.py](../../examples/all_visuals/01_tabs.py)

## Two ways to build

**Declarative** — pass `Tab` shapes up front:

```python
from dl2_reports import Tabs, Tab, Line, Table

row.add(Tabs(id="views", tabs=[
    Tab("Chart", children=[Line("sales", x_column="Month", y_columns=["Revenue"])]),
    Tab("Data",  children=[Table("sales", id="sales-table")]),
]))
```

**Incremental** — `add_tab()` returns a full `Layout`, so every `add_*` helper
works inside it:

```python
tabs = page.add_row().add_tabs(id="sales-tabs", default_tab=0, title="Sales Views")
tabs.add_tab("Chart").add_line("sales", x_column="Month", y_columns=["Revenue"])
tabs.add_tab("Data", direction="column").add_table("sales", id="sales-table")
```

## `Tabs` parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Stable id — enables active-tab [persistence](../features/persistent-view-state.md) *(dl2 0.4+)* and [link targeting](link.md). Defaults to an auto id. |
| `default_tab` | `int` | Index of the initially active tab (viewer default 0). |
| `title` | `str` | Title rendered above the tab strip. |
| `tabs` | `list[Tab \| dict]` | Tabs declared up front (`{"title", "children"}` or `{"title", "layout"}` dicts also work; `layout` takes precedence over `children`). |
| `**kwargs` | | Container props: `padding`, `margin`, `border`, `shadow`, `flex`, `persist_state`, … |

## `Tab` shape

| Field | Type | Description |
|-------|------|-------------|
| `title` | `str` | The tab label. |
| `children` | `list` | Components/layouts for the tab's content (wrapped in a row layout). |
| `layout` | `Layout` | A fully configured layout instead of `children` (takes precedence). |

A `Tab` needs `children` **or** `layout`; providing neither raises
`ValueError`.

## `add_tab(title, direction="column", **layout_kwargs)`

Adds a tab and returns its content `Layout`. `direction` and the kwargs are
[layout props](../features/layouts.md) (`gap`, `wrap`, `columns`,
`min_child_width`, …).

## Notes

- Nesting works: a tab's layout can contain another `Tabs` container.
- [Links](link.md) targeting a visual inside a tab activate the containing
  tab(s) automatically — including nested ones.
- With an `id`, the active tab survives reloads; opt out with
  `persist_state=False`.

## Related

- [Layouts](../features/layouts.md) — what you're arranging inside each tab.
- [Persistent view state](../features/persistent-view-state.md).
