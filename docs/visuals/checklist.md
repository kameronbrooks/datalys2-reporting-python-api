# Checklist (`type: "checklist"`)

A task list with completion status and due-date warnings. Since dl2 0.4.1 it is
built on the shared table infrastructure, so it has **full table parity**
(type-aware sorting, column hiding, CSV export, context menus, sticky header,
row modals, persistent state) plus status filter chips and a completion
progress bar.

**Read-only by design** — status always comes from the dataset; viewers cannot
check items off.

> **Class:** `dl2_reports.Checklist` · **Legacy helper:** `row.add_checklist(...)` ·
> **Example:** [05_checklist.py](../../examples/all_visuals/05_checklist.py)

## Quick start

```python
from dl2_reports import Checklist

page.add_row(
    Checklist("tasks",
              status_column="Done",        # truthy = complete
              warning_column="Due",        # date column
              warning_threshold=5,         # warn 5 days before due
              hide_completed=True,
              id="task-list"),
)
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `status_column` | `str` | **Required.** Column containing a boolean/truthy completion value. |
| `warning_column` | `str` | Date column checked for due-soon/overdue status. |
| `warning_threshold` | `int` | Days before the due date to trigger a warning (viewer default 3). |
| `columns` | `list[str]` | Subset of columns to display. |
| `page_size` | `int` | Rows per page (viewer default 10). |
| `show_search` | `bool` | Show the search bar (viewer default `True`). |
| `sortable` | `bool` | *(dl2 0.4.1+)* Type-aware sorting; Shift+click multi-sort (viewer default `True`). The Status header sorts by urgency. |
| `default_sort` | `list` | *(dl2 0.4.1+)* Initial sort (`SortSpec` or dicts). Accepts the special column `"status"` — urgency rank: overdue → due soon → pending → complete. Viewer default: urgency, then due date. |
| `hidden_columns` | `list[str]` | *(dl2 0.4.1+)* Columns hidden initially. |
| `allow_column_hiding` | `bool` | *(dl2 0.4.1+)* Runtime Columns menu (viewer default `True`). |
| `enable_export` | `bool` | *(dl2 0.4.1+)* CSV export / clipboard copy (viewer default `True`). Exports include a derived `Status` column. |
| `export_file_name` | `str` | *(dl2 0.4.1+)* File name for CSV export. |
| `context_menu` | `bool` | *(dl2 0.4.1+)* Right-click context menus (viewer default `True`). |
| `max_height` | `int` | *(dl2 0.4.1+)* Max body height in px; scrollable body + sticky header. |
| `sticky_header` | `bool` | *(dl2 0.4.1+)* Defaults to `True` when `max_height` is set. |
| `row_modal` | `bool` | *(dl2 0.4.1+)* Built-in row detail modal on double-click; leads with the status. |
| `row_modal_id` | `str` | *(dl2 0.4.1+)* Open a custom modal from `modals` instead; implies `row_modal`. |
| `row_modal_columns` | `list[str]` | *(dl2 0.4.1+)* Columns listed in the built-in detail modal. |
| `row_modal_title` | `str` | *(dl2 0.4.1+)* Title of the built-in detail modal (viewer default `'Details'`). |
| `show_status_filter` | `bool` | *(dl2 0.4.1+)* Status filter chips with counts — All / Pending / Due Soon / Overdue / Complete (viewer default `True`). Clicking a chip hides/shows that status (persisted). |
| `show_progress` | `bool` | *(dl2 0.4.1+)* Completion progress bar next to the "X / Y Completed" summary (viewer default `True`). |
| `hide_completed` | `bool` | *(dl2 0.4.1+)* Start with completed tasks hidden — the Complete chip toggled off (viewer default `False`). |
| `column_formats` | `dict` | *(dl2 0.4.1+)* Per-column display formats — see [Column formatting](../features/column-formatting.md). |
| `conditional_formats` | `list` | *(dl2 0.4.1+)* Highlight rules — see [Conditional formatting](../features/conditional-formatting.md). |
| `id` | `str` | Stable element id (persistence + link targeting). |
| `persist_state` | `bool` | Persist sort/columns/status chips (viewer default: `True` when `id` is set). |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). |

## Status model

Each row gets a derived status from `status_column` + `warning_column`:

| Status | Meaning |
|--------|---------|
| **Complete** | `status_column` is truthy. |
| **Overdue** | Not complete and the `warning_column` date is in the past. |
| **Due Soon** | Not complete and due within `warning_threshold` days. |
| **Pending** | Not complete, no warning. |

The status drives the chips, the urgency sort, the progress bar, the derived
`Status` column in CSV exports, and the leading line of the built-in row modal.

## Related

- [Table](table.md) — the underlying infrastructure; every table concept
  applies here.
- [Conditional formatting](../features/conditional-formatting.md) — highlight
  rows beyond the built-in status coloring.
