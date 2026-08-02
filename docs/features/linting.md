# Linting & Validation

Two safety nets catch config mistakes that the JS viewer would otherwise
swallow silently: a **Python-side lint** at `compile()` and the **viewer's
own validation** at load time. Plus the strictest check of all — typed
component constructors rejecting unknown props immediately.

## 1. Construction-time (typed components)

Typed components raise `TypeError` on any unknown keyword, with a suggestion:

```python
Table("sales", pagesize=20)
# TypeError: Table got unknown prop(s): 'pagesize' (did you mean 'page_size'?).
#            Use extra={...} to pass unmodeled viewer props through explicitly.
```

Structured shapes (`Threshold`, `SortSpec`, `ColumnFormat`,
`ConditionalFormat`, …) and the `filters` / `aggregates` builders validate
their values the same way (`ValueError`).

## 2. Compile-time lint (`report.compile()`)

At `compile()` the report tree is walked and props the known visual types
don't model are reported as `[dl2]` `UserWarning`s with did-you-mean
suggestions — or raised with `compile(strict=True)`:

```python
report.compile()             # warnings, never blocking
report.compile(strict=True)  # ValueError listing all unknown props
```

What gets flagged:

- **Legacy helper calls** whose unknown kwargs were routed into the
  passthrough — `add_table(..., pagesize=20)`, the classic silent typo.
- **Generic `add_visual(type, ...)` calls** whose type matches a known
  component but whose props don't.
- **Layout kwargs** the viewer doesn't read (e.g. `colums=2`).

Not flagged:

- Explicit `extra={...}` on a typed component — an intentional opt-out.
- Unknown *visual types* in `add_visual` — custom types pass through.
- Spelling variants: comparison is camelCase-insensitive (`page_size` and
  `pageSize` are both accepted).

`compile()` also raises `ValueError` if a
[derived dataset](derived-datasets.md) references an unknown source.

## 3. Viewer validation *(dl2 0.3+)*

On load, the viewer validates the config and emits `[datalys2]` console
warnings — never blocking rendering — for:

- unknown visual types, missing datasets, bad column names
- invalid filter ops, empty layouts, malformed tabs
- duplicate visual ids, unknown `rowModalId` / link `targetId`
- *(0.4.1+)* unknown `columnFormats` columns/kinds, malformed
  `conditionalFormats` (bad `when`, unknown preset/target, unresolvable
  columns), and column checks for `statusColumn`/`warningColumn`
- *(0.5+)* **calendar** visuals: missing both date mappings
  (`dateColumn`/`startColumn`), both `dateColumn` and `startColumn` set,
  `endColumn` without `startColumn`, a date-mapping column whose dtype is
  neither `date` nor `datetime`, unknown `defaultView`, unparseable
  `defaultDate`, `dayStartHour` outside 0–23, `dayEndHour` outside 1–24 or
  ≤ `dayStartHour`
- *(0.5+)* **remote datasets**: empty/non-string `url`, both `url` and
  `source` declared (url wins), unknown `responseType` (expected `"json"` or
  `"csv"`), `extract` with a CSV response (ignored), `refreshInterval` not a
  positive number of seconds, `headers` not an object of string values, and
  remote-only props (`extract`, `responseType`, `headers`, `refreshInterval`)
  without a `url`

Most of the 0.5 checks are duplicated in Python as construction-time
`ValueError`s (Calendar mapping/hour/enum errors, `add_remote_dataset` option
errors), so they rarely reach the viewer. When remote datasets are present,
viewer validation runs after the fetches settle, so column checks see the
real response.

Opt out by adding `<meta name="dl2-validate" content="false">`:

```python
report.set_meta("dl2-validate", "false")
```

## Recommended workflow

1. Prefer typed components — most mistakes never get past the constructor.
2. Run `compile(strict=True)` in CI or before publishing.
3. Check the browser console once after big changes for viewer-side warnings
   (bad column names can only be caught there or by the viewer).

## Related

- [Generic visual & `extra=`](../visuals/generic-visual.md) — deliberate
  passthrough.
- [Migration](migration.md) — moving legacy calls to typed components.
