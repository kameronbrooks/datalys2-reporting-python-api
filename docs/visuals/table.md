# Table (`type: "table"`)

A data table with searching, type-aware sorting, grouping, column hiding, CSV
export, totals, row detail modals, per-column formatting, and persistent view
state.

> **Class:** `dl2_reports.Table` · **Legacy helper:** `row.add_table(...)` ·
> **Example:** [04_table.py](../../examples/all_visuals/04_table.py)

## Quick start

```python
from dl2_reports import Table, SortSpec, TotalRow

page.add_row(
    Table("orders",
          id="orders-table",
          title="Orders",
          group_by="Region",
          default_sort=[SortSpec("Amount", "desc")],
          total_row=TotalRow(label="Totals", fns={"Units": "sum", "Amount": "avg"}),
          page_size=15),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md) — `[[...]]` projection selects columns). |
| `title` | `str` | Table title. |
| `columns` | `list[str]` | Columns to display (default: all). |
| `page_size` | `int` | Rows per page (viewer default 10). While grouped: groups per page. |
| `table_style` | `str` | `'plain'` (default), `'bordered'`, or `'alternating'`. |
| `show_search` | `bool` | Show the search bar (viewer default `True`). |
| `sortable` | `bool` | *(dl2 0.3+)* Type-aware sorting; Shift+click for multi-column sort (viewer default `True`). |
| `default_sort` | `list` | *(dl2 0.3+)* Initial sort — list of `SortSpec` or `{"column", "direction"}` dicts. List order = sort priority. |
| `hidden_columns` | `list[str]` | *(dl2 0.3+)* Columns hidden initially. |
| `allow_column_hiding` | `bool` | *(dl2 0.3+)* Runtime "Columns" menu (viewer default `True`). |
| `group_by` | `str` | *(dl2 0.3+)* Initial grouping column (collapsible groups). |
| `group_aggregates` | `list` | *(dl2 0.3+)* Per-group aggregates shown in group headers — `AggregateColumn`, `aggregates.agg(...)`, or `{"column", "fn", "as"?}` dicts. |
| `groups_collapsed` | `bool` | *(dl2 0.3+)* Whether groups start collapsed (viewer default `False`). |
| `enable_export` | `bool` | *(dl2 0.3+)* CSV export and clipboard copy (viewer default `True`). |
| `export_file_name` | `str` | *(dl2 0.3+)* File name for CSV export. |
| `context_menu` | `bool` | *(dl2 0.3+)* Right-click menus on headers/cells (viewer default `True`). |
| `max_height` | `int` | *(dl2 0.3+)* Max body height in px; enables scrollable body + sticky header. |
| `sticky_header` | `bool` | *(dl2 0.3+)* Defaults to `True` when `max_height` is set. |
| `total_row` | `bool \| TotalRow \| dict` | *(dl2 0.4+)* Grand-total row over the filtered data (all pages). `True` sums numeric columns; or `TotalRow(label=..., fns={"Amount": "avg"})`. Display-only. |
| `total_column` | `bool \| TotalColumn \| dict` | *(dl2 0.4+)* Per-row total column. `True` sums numeric visible columns; or `TotalColumn(label=..., columns=[...])`. Display-only. |
| `row_modal` | `bool` | *(dl2 0.4+)* Double-click a row (or right-click → Open details) to open a built-in detail modal. |
| `row_modal_columns` | `list[str]` | *(dl2 0.4+)* Columns listed in the built-in detail modal. |
| `row_modal_title` | `str` | *(dl2 0.4+)* Title of the built-in detail modal (viewer default `'Details'`). |
| `row_modal_id` | `str` | *(dl2 0.4+)* Open a **custom** modal instead; cards inside can use `{{ row.Col }}` templates. Implies `row_modal`. |
| `column_formats` | `dict` | *(dl2 0.4.1+)* Per-column display formats — see [Column formatting](../features/column-formatting.md). |
| `conditional_formats` | `list` | *(dl2 0.4.1+)* Highlight rules — see [Conditional formatting](../features/conditional-formatting.md). |
| `id` | `str` | Stable element id — enables [persistence](../features/persistent-view-state.md) and [link targeting](link.md). |
| `persist_state` | `bool` | *(dl2 0.4+)* Persist runtime sort/hidden-columns/grouping (viewer default: `True` when `id` is set). |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Typed shapes

```python
from dl2_reports import SortSpec, TotalRow, TotalColumn, AggregateColumn

SortSpec("Amount", "desc")                       # direction: 'asc' (default) | 'desc'
TotalRow(label="Totals", fns={"Units": "sum"})   # fns: column name → aggregate fn
TotalColumn(label="Total", columns=["Q1", "Q2"])
AggregateColumn("Amount", "sum", as_="Total")    # for group_aggregates
```

Plain dicts are accepted everywhere shapes are; shapes just validate eagerly
(bad directions/fns raise `ValueError` at construction).

## Notes

- **Column-name keys are preserved verbatim.** The keys of
  `total_row["fns"]` and `column_formats` are column names and are *not*
  snake→camel converted. For your own column-keyed passthrough dicts, wrap in
  `dl2_reports.RawDict`.
- **Pre-0.3 behavior:** set `context_menu=False, enable_export=False,
  allow_column_hiding=False, sortable=False` to fully restore it.
- `filter=` / `aggregate=` (common props) let a table show a client-side slice
  of a shared dataset — see [Filtering](../features/filtering.md) and
  [Aggregation](../features/aggregation.md).
- Totals are display-only; CSV export keeps raw values.

## Related

- [Checklist](checklist.md) — task-list variant built on the same
  infrastructure.
- [Modals](../features/modals.md) — row detail modals in depth.
- [Persistent view state](../features/persistent-view-state.md).
