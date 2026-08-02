# Persistent View State *(dl2 0.4+)*

Runtime view changes — table sort, hidden columns, grouping, checklist status
chips, and the active tab of tab groups — are saved to the browser's
localStorage and restored on reload, **per report and per visual `id`**.

## Enabling it

Give the visual a stable `id` — that's it:

```python
row.add_table("orders", id="orders-table")            # persists automatically
row.add_tabs(id="views")                              # active tab persists
row.add_table("orders", id="tmp", persist_state=False)  # opt out
```

- A visual persists only if it has an `id`; `persist_state=False` opts out.
- Ids must be **stable and unique** — duplicate ids break persistence and
  [links](../visuals/link.md) (the viewer validator warns), and a changed id
  orphans previously saved state.

## Report identity

Saved state is namespaced by the report's identity, resolved in order:

1. `<meta name="report-id">` — set via `DL2Report(title, report_id="my-report")`
   or `report.set_report_id("my-report")`
2. the report title
3. the file path

Set a stable `report_id` if the title may ever change, or state will appear
to "reset" when it does.

## What persists

| Visual | Persisted state |
|--------|-----------------|
| [Table](../visuals/table.md) | Sort, hidden columns, grouping. |
| [Checklist](../visuals/checklist.md) | Sort, hidden columns, status chip toggles. |
| [Tabs](../visuals/tabs.md) | Active tab. |
| [Calendar](../visuals/calendar.md) *(dl2 0.5+)* | Active view (month/week/day). |

## Resetting

Viewers can reset:

- **Per visual:** right-click the visual header → **Reset view**.
- **Whole report:** the **Reset view** button in the headbar (appears only
  when saved customizations exist).

## Related

- [Report configuration](report-configuration.md) — `report_id`.
- [Common visual properties](common-props.md) — `id` and `persist_state`.
