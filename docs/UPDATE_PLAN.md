# Update Plan — Python API support for dl2-reporting 0.3 & 0.4

*Written 2026-07-20. Companion docs: [ARCHITECTURE.md](ARCHITECTURE.md) (current package state)
and [JS_CONFIG_REFERENCE_0.3-0.4.md](JS_CONFIG_REFERENCE_0.3-0.4.md) (target JSON contract).*

## Goal

Let report authors use every 0.3/0.4 runtime feature from Python with first-class, documented,
tested helpers. Because unknown kwargs already pass through to JSON, the work is: ergonomic
builders + new component types + one serialization fix + docs + tests. Target versions:
`package_version = 0.4.0`, `dl2_version = 0.4.0`.

## Serialization fix (prerequisite)

`Visual.to_dict()` / `camel_case_dict` camelCase **every** dict key recursively. Two new JS props
use *data-dependent dict keys* that must survive verbatim:
- `totalRow.fns` → `{ "<column name>": "<fn>" }` (a column named `unit_price` would be corrupted
  to `unitPrice`).

**Change**: add a `RawDict` marker class (subclass of `dict`) in `serialization.py`. Both
serializers copy `RawDict` keys verbatim (still recursing into values). `add_table` wraps
`total_row["fns"]` automatically, so users only need `RawDict` for exotic passthrough props.

## Feature → API mapping

### 0.3

| JS feature | Python API |
|---|---|
| Filter grammar | New module `dl2_reports/filters.py`: `where(column, op, value)` + shortcuts `eq/neq/gt/gte/lt/lte/isin/notin/contains/starts_with/ends_with/between/is_null/not_null` and combinators `and_/or_/not_`. All return plain dicts; op names validated eagerly (`ValueError` on typo — the JS side only console-warns). Any visual helper accepts `filter=` (plain dicts also accepted). |
| Aggregates | New module `dl2_reports/aggregates.py`: `agg(column, fn, as_=None)` → `{column, fn, as}`, `aggregate(group_by, *aggs)` → `{groupBy, aggregates}`. Fn names validated. Any visual helper accepts `aggregate=`. |
| Derived datasets | `DL2Report.add_derived_dataset(name, source, filter=None, aggregate=None)` → dataset entry `{id, source, filter?, aggregate?}`. Compile-time `get_value()` on a derived dataset raises a clear "computed in the browser" error. Python-side check: `source` must be a known dataset name (chains allowed since earlier datasets register first; forward refs allowed with a warning? → **decision: validate at `compile()` not at add time** so declaration order doesn't matter — keep it simple: validate source exists at compile and raise). |
| Tabs visual | New `Tabs(ReportTreeComponent)` in `components/tabs.py`: `Layout.add_tabs(id=None, default_tab=None, title=None, **kwargs)` returns a `Tabs`; `tabs.add_tab(title, direction="column", **layout_kwargs)` returns a full `Layout` (so every `add_*` helper works inside a tab). Serializes as `{type:"tabs", elementType:"visual", id, tabs:[{title, layout:{...}}], defaultTab?, ...props}`. `CompileTimeConditional.add_tabs` override returns `None` when condition is False. |
| Layout props | No code needed (`wrap`, `align`, `justify`, `min_child_width`, `gap`, `flex` pass through; `min_child_width` → `minChildWidth`). Document them on `add_row`/`add_layout` docstrings + README, including the 0.3 spacing/`flex:0` breaking changes. |
| Table UX | Extend `add_table` with typed params: `sortable`, `default_sort`, `hidden_columns`, `allow_column_hiding`, `group_by`, `group_aggregates`, `groups_collapsed`, `enable_export`, `export_file_name`, `context_menu`, `max_height`, `sticky_header`. |
| Config validation | Runtime feature — nothing to emit. Docs mention `<meta name="dl2-validate" content="false">` via `report.set_meta`. |

### 0.4

| JS feature | Python API |
|---|---|
| Table totals | `add_table(total_row=..., total_column=...)`: `True` or dicts `{label, fns}` / `{label, columns}`; `fns` auto-wrapped in `RawDict`. |
| Row modals | `add_table(row_modal=, row_modal_id=, row_modal_columns=, row_modal_title=)`. Custom modals: existing `report.add_modal()` + cards using `{{ row.X }}` templates — docs + example. |
| Persistent state | `add_table(..., id=..., persist_state=...)` and same on `add_tabs`. `DL2Report(report_id=...)` ctor param (+ `set_report_id()`) emitting `<meta name="report-id">`. Helpers that accept `id` set the component's real `.id` (stable ids are what make persistence/links useful). |
| Link visual | New mixin `visuals/Link.py`: `add_link(target_id=None, href=None, label=None, link_style=None, **kwargs)`; raises unless exactly one navigation source (`target_id` or `href`) is given. |
| Anchors / hash links | Covered by stable `id` support above; docs only. |

## File-by-file change list

1. `dl2_reports/serialization.py` — add `RawDict`; honor it in `camel_case_dict`.
2. `dl2_reports/components/visual.py` — honor `RawDict` in `_serialize_object`; if `id` kwarg is
   passed, adopt it as `self.id` (instead of only overriding at serialization).
3. `dl2_reports/filters.py` — new.
4. `dl2_reports/aggregates.py` — new.
5. `dl2_reports/components/tabs.py` — new `Tabs` component.
6. `dl2_reports/components/layout.py` — `add_tabs` (+ lazy import), `add_link` mixin wiring,
   `CompileTimeConditional` gains `add_tabs`/`add_link` behavior, docstring updates for new
   layout props.
7. `dl2_reports/components/visuals/Link.py` — new mixin; register in `visuals/__init__.py`,
   `Layout`, `CompileTimeConditional`.
8. `dl2_reports/components/visuals/Table.py` — extended signature (0.3 UX + 0.4 totals/row modals
   + `id`/`persist_state`).
9. `dl2_reports/report.py` — `add_derived_dataset`, `report_id` ctor param + `set_report_id`,
   derived-aware `get_value` error, compile-time source check, `DL2_VERSION = "0.4.0"`,
   export `Tabs` on `DL2Report`.
10. `dl2_reports/__init__.py` — export `filters`, `aggregates`, `RawDict`.
11. Tests — new unit tests (`test_filters_aggregates.py`, `test_tabs.py`, `test_new_features.py`
    covering derived datasets / link / totals serialization / RawDict / persist ids);
    new golden scenarios (`tabs`, `filter_aggregate`, `table_features`, `link_nav`);
    regenerate all goldens (dl-version meta changes them all anyway).
12. `DOCUMENTATION.md` / `README.md` — new sections for every feature; note 0.3 breaking
    rendering defaults.
13. `versions.json` → `{0.4.0, 0.4.0}`; run `tools/update_versions.py`.

## Design decisions & risks

- **Plain dicts always accepted**: builders are conveniences, not gates. Passing raw dicts (already
  camelCased or snake_case) keeps forward compatibility.
- **Eager Python-side validation only where the JS silently no-ops** (filter ops, agg fns,
  link target/href, tabs non-empty at compile) — catches typos at build time where the browser
  would only console-warn.
- **Derived datasets are not materialized in pandas** at compile time (the filter grammar would
  have to be re-implemented; deferred as future work). `get_value` on them raises with guidance
  to compute via pandas instead.
- **Golden churn**: every golden regenerates (version meta). Diffs reviewed for the new
  scenarios; existing scenarios should differ only in the `dl-version` meta line.
- **ID semantics change (small)**: passing `id=` to a helper now sets the component's real id.
  Previously it was only a props override that shadowed the auto id at serialization — emitted
  JSON is identical, so no golden impact.
