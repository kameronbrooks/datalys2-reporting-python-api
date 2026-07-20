# datalys2-reporting 0.3/0.4 — Config Schema Reference

*Extracted 2026-07-20 from the JS/TS source at `../datalys2-reporting` (v0.4.0).
This is the contract the Python API must emit. Citations are `file:line` in that repo.*

Top-level types: `src/lib/types.ts`. The runtime auto-mounts on script load by reading
`<div id="root">` and `<script id="report-data">` (`src/index.tsx:91-103, 168-173`) —
no init call; this is unchanged from 0.2.

## Top-level config (`ApplicationData`, types.ts:328-332)

```json
{
  "pages":    [ ReportPage, ... ],
  "modals":   [ ReportModal, ... ],
  "datasets": { "id1": Dataset, ... }
}
```

- `datasets` is a **dict keyed by id** (not a list). No `theme` key exists — theming is CSS-only.
- `ReportPage` (types.ts:314-319): `title` (required), `description?`, `lastUpdated?`, `rows?: Layout[]`.
- `ReportModal` (types.ts:133-140): `id`, `title` (both required), `description?`, `rows?: Layout[]`, `buttonLabel?`.
- Meta tags read from the HTML head: `description`, `author`, `last-updated`,
  **`report-id`** (0.4, state namespace), `gc-compressed-data`, **`dl2-validate`** (`"false"` disables validation).

## 1. Filter grammar (`FilterExpression`, types.ts:43-60; eval filter-utility.ts)

A filter is a **leaf condition** or a **boolean group**; groups nest arbitrarily.

Leaf: `{ "column": "region", "op": "eq", "value": "West" }`
- `column`: string name **or** integer index.
- `op`: `eq | neq | gt | gte | lt | lte | in | nin | contains | startsWith | endsWith | between | isNull | notNull`
- `value`: scalar (or `[low, high]` for `between`); `values`: array for `in`/`nin`/`between`
  (falls back to `value` if it's already an array).

Groups (exactly one key): `{"and": [...]}` · `{"or": [...]}` · `{"not": <expr>}`

Semantics: `contains/startsWith/endsWith` are case-insensitive; `between` is inclusive;
`isNull` matches `null`/`undefined`/`""`; comparisons on `date`/`datetime` dtype columns coerce
string/number values to epoch millis; null cells never match ordering ops; unknown op → console
warn, matches nothing. Only `table`/`records` dataset formats are filterable.

## 2. Aggregate spec (`AggregateSpec`, types.ts:81-84; aggregate-utility.ts)

```json
{
  "groupBy": ["region"],
  "aggregates": [ { "column": "amount", "fn": "sum", "as": "total" } ]
}
```

- `groupBy`: non-empty array of column names/indices.
- `fn`: `sum | avg | min | max | count | countDistinct | first | last`.
- `as` optional; **default output column name is `` `${fn}_${column}` ``** (e.g. `sum_amount`).
- Output is a records-format dataset: group columns first, then aggregate columns.
  Numeric fns skip nulls (null result if none); `min`/`max` on dates stay dates;
  `count`/`countDistinct` dtype `int`.

Applied per-visual via `visual.filter` → `visual.aggregate` (in that order,
component-registry.tsx:75-113) with zero changes to the visual's other props.

## 3. Derived datasets (dataset-utility.ts:162-211)

A dataset may declare (instead of inline data):

```json
"westTotals": {
  "source": "sales",
  "filter":    { ... FilterExpression ... },
  "aggregate": { ... AggregateSpec ... }
}
```

Resolved at load in dependency order; chains supported; cycles / missing sources → console warn.
Base dataset fields (types.ts:7-25): `id`, `data`, `columns`, `dtypes`, `format`
(`table|records|list|record`), `compression?` (`none|gzip`), `compressedData?` (script-tag id).
`id` auto-fills from the datasets dictionary key when omitted (dataset-utility.ts:113-115).

## 4. Tabs visual (TabsVisual.tsx)

`type: "tabs"` (alias `"tabgroup"`), dataset-less, placed in layout `children`.

```json
{
  "type": "tabs", "id": "sales-tabs", "defaultTab": 0,
  "tabs": [
    { "title": "Chart", "children": [ <element>, ... ] },
    { "title": "Grid",  "layout": { "type": "layout", "direction": "grid", "children": [...] } }
  ]
}
```

- Property is **`tabs`** (not `children`); per-tab: `title` (falls back to `Tab N`) plus
  **`children`** (rendered as a row layout) or **`layout`** (full layout object, takes precedence).
- `defaultTab` (default 0), `title`, `description`, standard container props
  (`padding/margin/border/shadow/flex`), `id`, `persistState` (default true when `id` set —
  persists the active tab).
- Validator: `tabs` must be non-empty; each tab needs `children` or `layout`.

## 5. Layout props (types.ts:284-303; PageRow.tsx:76-123)

| Prop | Values / default |
|------|------------------|
| `direction` | `row | column | grid` |
| `columns` | grid column count, default 3 |
| `gap` | string or number, **default `'10px'`** (0.3 breaking change — was 0) |
| `wrap` | bool → `flex-wrap: wrap` (row/column) |
| `align` / `justify` | CSS `align-items` / `justify-content` (row/column) |
| `minChildWidth` | number (px) or string → grid `repeat(auto-fit, minmax(X, 1fr))` |
| `flex` | number, default 1 — **`flex: 0` now respected** |
| `margin` / `padding` | numbers, default 0 — **zero values now respected** |
| `border` / `shadow` | string, or truthy → theme default |
| `title` | rendered as `<h3>` above content in all directions |

Common element props (`LayoutElement`): `type`, `elementType` (deprecated), `padding`, `margin`,
`border`, `shadow`, `flex`, `modalId`. Visuals default `margin: 0` in 0.3 (was 10).

## 6. Table props — 0.3 additions (Table.tsx:12-124)

| Prop | Type / default |
|------|----------------|
| `sortable` | bool, default true (type-aware multi-sort; Shift+click) |
| `defaultSort` | `[{ "column": "amount", "direction": "asc"|"desc" }, ...]` initial multi-sort |
| `hiddenColumns` | `string[]` initially hidden |
| `allowColumnHiding` | bool, default true (runtime Columns menu) |
| `groupBy` | string — initial grouping column |
| `groupAggregates` | `AggregateColumn[]` (same `{column, fn, as}` shape as §2) shown in group headers |
| `groupsCollapsed` | bool, default false |
| `enableExport` | bool, default true (CSV + TSV clipboard) |
| `exportFileName` | string, default title/datasetId |
| `contextMenu` | bool, default true (header/cell right-click menus) |
| `maxHeight` | number px → scrollable body |
| `stickyHeader` | bool, defaults true when `maxHeight` set |

Pre-0.3 props unchanged: `columns`, `pageSize` (10), `tableStyle`, `showSearch`, `title`.
Grouped tables paginate **by group** (pageSize = groups per page).

## 7. Table totals — 0.4 (Table.tsx:47-53, 293-333)

- `totalRow`: `true` (sum all numeric visible columns over the **filtered data, all pages**) or
  `{ "label": "Totals", "fns": { "<columnName>": "<AggFn>", ... } }` — only listed columns totaled.
  Default label `'Total'`. Sticky when `maxHeight` set.
  ⚠ `fns` keys are **column names used as dict keys** — must not be case-mangled by serialization.
- `totalColumn`: `true` (per-row sum of numeric visible columns) or
  `{ "label": "Total", "columns": ["units", "amount"] }`.
- Totals are display-only (excluded from CSV/clipboard export).

## 8. Row detail modals — 0.4 (Table.tsx:59-69, 127-184)

- `rowModal: true` — double-click / right-click → built-in details modal.
- `rowModalColumns`: string[] shown in the default modal (may include hidden cols).
- `rowModalTitle`: string, default `'Details'`.
- `rowModalId`: string — open a **custom modal** from the top-level `modals` array instead
  (implies `rowModal`). The clicked row goes into modal context; cards inside the modal can use
  the full template engine with a `row` variable:
  `"title": "Order #{{ row.id }}"`, `"text": "{{ formatCurrency(row.amount) }}"`.
  Available in `{{ }}`: `row`, `datasets`, `props`, helpers
  `count/sum/avg/min/max/formatNumber/formatPercent/formatCurrency` (JS expressions — trusted HTML only).

## 9. Persistent view state — 0.4 (state-persistence.ts)

- `persistState` on Table (sort/hidden/grouping) and Tabs (active tab): default **true when the
  visual has an `id`**; requires an `id`. Opt out with `persistState: false`.
- localStorage key `dl2state:<reportKey>:<visualId>`; reportKey = `<meta name="report-id">` →
  `document.title` → `location.pathname` (first match).
- Per-visual reset via right-click → Reset view; report-wide Reset view button in headbar.
- **Stable, unique visual ids matter** — duplicates break persistence and links (validator warns).

## 10. Link visual — 0.4 (LinkVisual.tsx)

`type: "link"`, dataset-less. Requires `targetId` **or** `href`.

| Prop | Meaning |
|------|---------|
| `targetId` | id of any visual — switches page, activates containing tabs (nested ok), scrolls, flashes |
| `href` | external URL (new tab) |
| `label` (or `text`) | link text; falls back to targetId/href, then `'Link'` |
| `linkStyle` | `'link'` (default) or `'button'` |

Also honors `padding`, `margin`, `flex` (default 0). Every visual with an `id` is a DOM anchor;
plain `#visual-id` hash links navigate too (incl. markdown cards and deep links on load).

## 11. Validation (validation-utility.ts:244+)

Console-warnings only (`[datalys2]`), never throws; disable with `<meta name="dl2-validate" content="false">`.
Checks: no pages / page without rows / empty layouts / unknown direction; unknown or missing visual
`type`; missing or unknown `datasetId`; filter shape + op + column existence; aggregate shape + fn +
column existence; derived `source` exists; duplicate visual ids; modal trigger / `rowModalId` /
link `targetId` referencing nothing; column-name checks for `xColumn, yColumn, valueColumn,
labelColumn, categoryColumn, groupBy` and list props `yColumns, columns, hiddenColumns,
rowModalColumns` (skipped when `aggregate` present); tabs shape.

## Notes for the Python emitter

- Column refs may be strings or integer indices everywhere (filter, aggregate, groupBy).
- Filter/aggregate grammar is identical per-visual and per-derived-dataset.
- Card `contentType`: `text` (default) / `html` / `md`; templates run in all three.
- jsDelivr CDN pattern unchanged: `.../datalys2-reporting@<ref>/dist/datalys2-reports.min.js` + `/dl2-style.css`.
