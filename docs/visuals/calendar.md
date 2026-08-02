# Calendar (`type: "calendar"`) *(dl2 0.5+)*

Month, week, and day views with a prev/next/Today toolbar. The month grid draws
true spanning bars for multi-day events (with lane stacking and a "+N more"
overflow that drills into day view); week and day views add an all-day section
and a scrollable hour grid with a current-time line. All calendar math is UTC,
matching date rendering in tables and charts.

> **Class:** `dl2_reports.Calendar` · **Legacy helper:** `row.add_calendar(...)` ·
> **Example:** [16_calendar.py](../../examples/all_visuals/16_calendar.py)

## Quick start

```python
from dl2_reports import Calendar

# Spanning events with start/end, colored by team
page.add_row(
    Calendar("events",
             start_column="Start", end_column="End",
             title_column="Task", category_column="Team",
             default_view="week", time_format="24h",
             id="team-calendar"),
)

# Single-date events
page.add_row(Calendar("holidays", date_column="Day", title_column="Holiday"))
```

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | `str` | **Required.** Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `date_column` | `str \| int` | Event date column (single-date events). Exactly one of `date_column` / `start_column` is required. |
| `start_column` | `str \| int` | Event start column (spanning events). |
| `end_column` | `str \| int` | Event end column; only meaningful with `start_column`. |
| `title_column` | `str \| int` | Event title column (viewer default: first dataset column not used by another mapping). |
| `category_column` | `str \| int` | Tag-based coloring with a legend; empty values bucket as `(none)`. |
| `title` / `description` | `str` | Text above the calendar. |
| `default_view` | `str` | `'month'` (viewer default), `'week'`, or `'day'`. |
| `default_date` | `str` | Initial date as an ISO string, e.g. `"2026-08-01"` (viewer default: today, UTC). |
| `week_starts_on` | `int` | `0` = Sunday (viewer default), `1` = Monday. |
| `show_weekends` | `bool` | Show Saturday/Sunday columns (viewer default `True`). |
| `day_start_hour` | `int` | First hour on the week/day grid, 0–23 (viewer default `0`). |
| `day_end_hour` | `int` | Hour the grid ends at, 1–24 (viewer default `24`). Must be greater than `day_start_hour`. |
| `hour_height` | `int` | Pixel height of one hour row (viewer default `48`). |
| `max_events_per_day` | `int` | Events per month cell before the "+N more" clamp (viewer default `3`). Released when [printing](../features/printing.md). |
| `time_format` | `str` | `'12h'` (viewer default) or `'24h'`. |
| `max_height` | `int` | Max height in px of the month grid (viewer default `560`). |
| `empty_label` | `str` | Text when the dataset has no events (viewer default `"No events."`). |
| `color` | `str \| list[str]` | Category palette — D3 scheme name, single color, or list (viewer default `tableau10`), as in other categorical visuals. |
| `show_legend` | `bool` | Category legend (viewer default `True` when `category_column` is set). |
| `legend_title` | `str` | Legend heading (viewer default `"Legend"`). |
| `row_modal` | `bool` | Built-in event detail modal on double-click (or right-click → Open details). |
| `row_modal_id` | `str` | Open a custom modal instead; cards inside can use `{{ row.Col }}` templates. Same API as [table row modals](../features/modals.md). |
| `row_modal_columns` | `list[str]` | Columns listed in the built-in detail modal. |
| `row_modal_title` | `str` | Title of the built-in detail modal (viewer default `"Details"`). |
| `context_menu` | `bool` | Right-click context menu (viewer default `True`). |
| `extra` | `dict` | [Passthrough props](generic-visual.md). |
| `**common` | | [Common visual properties](../features/common-props.md). Give the calendar an `id` to persist the active view; `persist_state=False` opts out. Note: the calendar has no `width`/`height` props — size it with `max_height` and `flex`. |

## All-day vs timed events

The dtype of the start column decides how events render:

- dtype `"date"` → **all-day events** (spanning bars, all-day section).
- dtype `"datetime"` → **timed events** placed on the week/day hour grid;
  overlapping events lay out side-by-side.

`add_df` declares a date-like column as `"datetime"` when any value carries a
time of day and `"date"` when every value is midnight UTC — pass
`dtype_overrides={"Due": "datetime"}` to force either (see
[Datasets](../features/datasets.md)).

## Validation

The class raises `ValueError` at construction for mistakes the viewer would
only warn about: both or neither of `date_column`/`start_column`, `end_column`
without `start_column`, a bad `default_view`/`time_format`/`week_starts_on`,
`day_start_hour` outside 0–23, and `day_end_hour` outside 1–24 or not greater
than `day_start_hour`. Use `extra={...}` to bypass.

## Related

- [Modals](../features/modals.md) — event detail modals share the table's row-modal API.
- [Persistent view state](../features/persistent-view-state.md) — the active view persists when the visual has an `id`.
- [Printing](../features/printing.md) — printed calendars release the "+N more" clamps.
- [Datasets](../features/datasets.md) — `date` vs `datetime` dtype inference.
