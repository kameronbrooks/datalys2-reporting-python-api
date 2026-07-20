# V2 API Migration Plan — typed components ("dataclass paradigm")

*Written 2026-07-20. Target release: **0.5.0**. Prereq: 0.4.0 published (all dl2 0.3/0.4
features supported through the existing helper API).*

## Goal

Replace the kwargs-bag pattern with **typed component objects** while keeping the existing
helper API working unchanged. Motivations (see discussion in project history):

- Typos in props currently serialize silently and are ignored by the viewer — no autocomplete,
  no static check, no warning. This is the single biggest usability problem for both humans
  and LLMs.
- Helper mixins are pure boilerplate (`if x is not None: kwargs[...] = x`) that drifts from docs.
- Structured props (`threshold`, `total_row`, `default_sort`, …) are untyped dicts.
- Mixin inheritance + `Optional` returns confuse type checkers and readers.

## Target API (what 0.5.0 looks like)

```python
from dl2_reports import DL2Report, KPI, Table, Line, Tabs, Threshold, TotalRow, SortSpec, F, A

report = DL2Report("Sales", report_id="sales-v1")
report.add_df("sales", df)

page = report.add_page("Overview")
page.add_row(
    KPI("sales", value_column="Revenue", format="currency", row_index=-1),
    Line("sales", x_column="Month", y_columns=["Revenue"],
         threshold=Threshold(value=5000, mode="above")),
)
row = page.add_row()
row.add(Table("sales",
              id="orders-table",
              group_by="Region",
              default_sort=[SortSpec("Amount", "desc")],
              total_row=TotalRow(fns={"Units": "sum", "Amount": "avg"}),
              filter=F.gte("Amount", 200)))
```

### Design rules

1. **One dataclass per visual type** (stdlib `@dataclass`, no new runtime dependency).
   Field order mirrors the old helper signatures, so positional arguments migrate 1:1.
   Fields are the single source of truth: serialization (snake→camel), docs tables, and the
   known-props registry are all derived from them.
2. **Sub-shape dataclasses**: `Threshold`, `SortSpec`, `TotalRow`, `TotalColumn`, `GaugeRange`,
   `Tab`, `AggregateColumn`. Plain dicts remain accepted everywhere (coerced on serialization).
3. **`layout.add(component) -> component`** is the one generic entry point; it returns the
   added component so chaining (`.add_trend()`) keeps working. `page.add_row(*children,
   **layout_kwargs)` accepts components directly.
4. **`extra: dict` field** on every component replaces `**kwargs` as the forward-compat escape
   hatch — explicit, not the default path. Unknown constructor kwargs raise `TypeError`
   (that's the whole point).
5. **Old helpers stay** as thin wrappers that construct the dataclass and call `add()`.
   Byte-identical JSON output is enforced by the golden tests at every commit.
6. **Compile-time lint**: `compile()` warns (never errors, unless `strict=True`) on props not in
   the registry, with a did-you-mean suggestion; mirrors the JS validator's philosophy.
7. **`py.typed`** ships so IDEs/type-checkers/LLMs see the full surface.

## Commit sequence

Each commit leaves the test suite green and golden output byte-identical unless stated.
Version stays 0.4.x-dev until the release commit.

| # | Commit | Contents |
|---|--------|----------|
| 1 | `chore: ship py.typed and tighten type hints` | Add `py.typed`, fix `Optional` annotations, package-data config in pyproject. |
| 2 | `feat(core): Component base with declarative prop serialization` | New `components/component.py`: dataclass base with `to_props()` (snake→camel, RawDict-aware, sub-shape coercion), `extra` field, per-class prop registry. Not yet user-facing. |
| 3 | `feat(core): typed sub-shape dataclasses` | `Threshold`, `SortSpec`, `TotalRow`, `TotalColumn`, `GaugeRange`, `Tab`, `AggregateColumn` in `dl2_reports/shapes.py` + serialization + unit tests. Dicts still accepted. |
| 4 | `feat(api): layout.add() and component-accepting add_row()` | `Layout.add(component)`, `Page.add_row(*children, **kwargs)`, `Modal.add_row(*children)`; `CompileTimeConditional.add()`. Tests. |
| 5 | `feat(visuals): KPI and Card component classes (pilot)` | First two dataclasses; old `add_kpi`/`add_card` delegate to them. Golden-diff must be empty. Establishes the pattern (field order = helper order). |
| 6 | `feat(visuals): Table component class` | Largest surface; includes totals/row-modal/persist fields typed via shapes. `add_table` delegates. |
| 7 | `feat(visuals): chart components (Pie, Bar, Line, Area, Scatter)` | Incl. `Threshold` field typing; helpers delegate. |
| 8 | `feat(visuals): remaining components (Checklist, Histogram, Heatmap, Gauge, Boxplot, Link, ModalButton)` | Helpers delegate. |
| 9 | `feat(visuals): Tabs alignment` | `Tabs` accepts `Tab(...)` entries and component children; `add_tabs` unchanged. |
| 10 | `feat(lint): known-prop registry + compile() warnings` | Registry derived from dataclass fields; `compile(strict=False)` warns on unknown props with did-you-mean; `strict=True` raises. Opt-out documented. |
| 11 | `feat(api): NullComponent for on_condition()` | `on_condition(False).add_*` returns a chain-safe no-op instead of `None` (behavior-compatible: still not in tree, still falsy). Fixes `Optional` chaining. |
| 12 | `feat(tooling): package the migration tool` | Move `tools/migrate_to_v2.py` → `dl2_reports/migrate.py`, add `python -m dl2_reports.migrate` entry, `[migrate]` optional extra for libcst. |
| 13 | `docs: v2 API documentation and migrated examples` | README/DOCUMENTATION rewritten around components (helpers documented as legacy-supported); regenerate example notebooks via the migration tool (dogfood). |
| 14 | `release: 0.5.0` | versions.json → 0.5.0, `update_versions.py`, goldens re-stamped, CHANGELOG section, build + publish. |

Suggested follow-up (0.5.x): deprecation *notice* (docs only, no warnings) for the helper API;
decide in 0.6 whether helpers ever emit `DeprecationWarning` — no removal planned.

## Migration tool

`tools/migrate_to_v2.py` (this repo, shipped in-package at commit 12). Rewrites existing user
scripts/notebooks from the helper API to the component API. Built on **libcst** so comments and
formatting are preserved; the old API keeps working, so running it is optional and can be done
file-by-file.

- `python tools/migrate_to_v2.py report_script.py` — dry run, prints a unified diff
- `python tools/migrate_to_v2.py report_script.py --write` — apply in place
- Accepts multiple paths and directories (recurses `*.py` and `*.ipynb`; notebook code cells
  are transformed individually, cells that don't parse — e.g. `%magics` — are skipped).

Transforms:
1. `x.add_kpi(...)` → `x.add(KPI(...))` for every visual helper (chains preserved:
   `row.add_scatter(...).add_trend()` → `row.add(Scatter(...)).add_trend()`).
2. Known literal-dict props → typed shapes: `threshold={...}` → `threshold=Threshold(...)`,
   `total_row={...}` → `TotalRow(...)` (its `fns` dict is kept as a dict — keys are column
   names), `total_column={...}` → `TotalColumn(...)`, `default_sort=[{...}]` → `[SortSpec(...)]`,
   `ranges=[{...}]` → `[GaugeRange(...)]`. Non-literal values are left untouched.
3. Import management: extends (or inserts) `from dl2_reports import ...` with exactly the
   names the file now uses.

Known limitations (documented in `--help`):
- `add_visual("type", ...)` generic calls are left unchanged (still supported).
- `group_aggregates`/`aggregates` dicts are left as dicts (`as` is a Python keyword; the
  `A.agg(...)` builder is the typed path).
- Dynamic patterns (helpers called via variables, `**kwargs` splats) are left unchanged.

## Risk & rollback

- Every commit is independently revertable; helper API never breaks, so users are never forced
  to migrate.
- Golden tests are the safety net: commits 5–9 must produce byte-identical HTML.
- The lint (commit 10) is warn-by-default precisely so existing passthrough props (a feature)
  don't become errors.
