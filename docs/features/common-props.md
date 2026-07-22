# Common Visual Properties

Every typed component (and every legacy `add_*` helper) accepts these
properties in addition to its own. They control container styling, identity,
and client-side data shaping. Anything outside this set and the component's
own parameters raises `TypeError` at construction — use `extra={...}` for
deliberate passthrough (see [Generic visual](../visuals/generic-visual.md)).

```python
from dl2_reports import Table, filters as F

Table("sales",
      id="sales-table",            # identity: anchors, links, persistence
      border=True, shadow=True,    # styling
      flex=2, padding=8,
      modal_id="sales-details",    # expand icon → modal
      filter=F.eq("Region", "West"))   # client-side slice
```

## Reference

| Property | Type | Description |
|----------|------|-------------|
| `id` | `str` | Stable element id. Every visual with an id is a DOM anchor *(dl2 0.4+)*, can be a [link target](../visuals/link.md), and can [persist view state](persistent-view-state.md). Give persisted/linked visuals **stable, unique** ids. |
| `title` | `str` | Title (most visuals render it as a header). |
| `description` | `str` | Description text (visual-dependent). |
| `padding` | `int` | Padding in px (viewer default 0; zero is respected since dl2 0.3). |
| `margin` | `int` | Margin in px (viewer default 0 since dl2 0.3 — spacing is owned by layout `gap`). |
| `border` | `bool \| str` | `True` for the theme default border, or a CSS border string like `"2px dashed #f59e0b"` (CSS strings honored since dl2 0.4.1). |
| `shadow` | `bool \| str` | `True` for the theme default box-shadow, or a CSS box-shadow string (since dl2 0.4.1). |
| `flex` | `int` | Flex grow value (`flex=0` is respected since dl2 0.3). |
| `width` / `height` | `int` | Fixed size in px (visual-dependent). |
| `modal_id` | `str` | Id of a global [modal](modals.md) — hovering the visual shows an expand icon that opens it. |
| `filter` | `dict` | *(dl2 0.3+)* Client-side [filter](filtering.md) applied to this visual's view of its dataset. |
| `aggregate` | `dict` | *(dl2 0.3+)* Client-side [aggregation](aggregation.md) applied after `filter`. |
| `persist_state` | `bool` | *(dl2 0.4+)* Opt in/out of [view-state persistence](persistent-view-state.md) (viewer default: `True` when `id` is set, for visuals that persist anything). |

## Notes

- **snake_case → camelCase:** all props serialize to camelCase in the report
  JSON (`modal_id` → `modalId`). Column names used as dict *keys* are the
  exception — they are preserved verbatim.
- `filter=` and `aggregate=` are validated at construction time
  (`ValueError` on bad ops/fns), and only work on `records`/`table` format
  datasets.
- Layouts accept the styling subset too (`padding`, `margin`, `border`,
  `shadow`, `flex`, plus their own `gap`/`wrap`/… props) — see
  [Layouts](layouts.md).
