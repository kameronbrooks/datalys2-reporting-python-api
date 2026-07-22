# Generic Visual & Passthrough Props

Two escape hatches for viewer capabilities the typed API doesn't model (yet):
the `extra={...}` passthrough on every typed component, and the untyped
`row.add_visual()` helper.

## `extra={...}` on typed components

Every typed component accepts `extra` — a dict of props serialized verbatim
into the visual's JSON (snake_case keys are still camelCased):

```python
from dl2_reports import Line

row.add(Line("sales", x_column="Month", y_columns=["Revenue"],
             extra={"some_new_viewer_prop": True}))
```

Use this for forward compatibility when the viewer gains a prop before this
package models it. Props passed via `extra` are **not** flagged by the
[compile lint](../features/linting.md) — you are explicitly opting in.

## `row.add_visual(type, dataset_id=None, visual=None, **kwargs)`

The fully generic helper — any type string, any props:

```python
visual = row.add_visual("line", "my_data", x_column="Month", y_columns=["Revenue"])
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | `str` | **Required.** Visual type (`'kpi'`, `'table'`, `'line'`, or any viewer-supported type). |
| `dataset_id` | `str` | Dataset id (or a [formula datasource](../features/formula-datasources.md)). |
| `visual` | `Visual` | An existing `Visual` instance to add instead of constructing one — used to re-add [copies](../features/reading-values.md#visualcopy). |
| `**kwargs` | | Visual props, serialized to JSON (snake→camel). |

`add_visual` bypasses the typed constructors, so unknown props are *not*
rejected at construction — they surface as `[dl2]` warnings at
`compile()` time instead (see [Linting](../features/linting.md)).

## Re-adding a copied visual

```python
proto = row.add_kpi("sales", value_column="revenue", row_index=0, title="North")
copy = proto.copy()
copy.props["row_index"] = 1
copy.props["title"] = "South"
row.add_visual(copy.type, visual=copy)
```

See [Reading values](../features/reading-values.md) for the full pattern.

## When to prefer which

| Situation | Use |
|-----------|-----|
| Prop exists in the typed class | The typed parameter (fails fast on typos). |
| Viewer prop not modeled yet | Typed class + `extra={...}`. |
| Visual type not modeled at all | `row.add_visual(type, ...)`. |
| Stamping copies of a configured visual | `visual.copy()` + `row.add_visual(..., visual=copy)`. |
