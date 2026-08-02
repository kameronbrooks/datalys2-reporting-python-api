# Remote datasets *(dl2 0.5+)*

`DL2Report.add_remote_dataset()` declares a dataset fetched from a URL in the
browser at load time — no rows are embedded in the HTML. The report renders
immediately; visuals bound to the dataset show a loading placeholder and fill
in when the fetch settles. A failed fetch shows an inline error in exactly
those visuals (plus one console warning); the rest of the report is unaffected.

```python
report.add_remote_dataset(
    "live_sales",
    "https://example.com/api/sales.json",
    extract="result.rows",              # rows nested in a JSON wrapper
    headers={"Authorization": "Bearer public-token"},
    refresh_interval=60,                # re-fetch every 60 seconds
    columns=["Region", "Amount"],
    dtypes=["string", "number"],
)

page.add_row().add(Table("live_sales", title="Live sales"))
```

> **Security:** `headers` are embedded as **plain text** in the compiled HTML —
> anyone who can open the report can read them. Only use tokens that are safe
> to treat as public. The endpoint must be CORS-accessible from wherever the
> report is opened.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | **Required.** Dataset id. |
| `url` | `str` | **Required.** URL to fetch. |
| `response_type` | `str` | `'json'` (viewer default) or `'csv'`. |
| `extract` | `str` | Dot-path to the rows inside a JSON wrapper object, e.g. `"result.rows"`. JSON only. |
| `headers` | `dict[str, str]` | HTTP request headers (see the warning above). Keys are emitted verbatim. |
| `refresh_interval` | `int \| float` | Re-fetch every N seconds. Omit or `0` to fetch once. |
| `columns` | `list[str]` | Declared column names (required for JSON array-of-arrays responses). |
| `dtypes` | `list[str]` | Declared dtypes aligned with `columns` — declare `"date"`/`"datetime"` columns so date conversion happens. |
| `format` | `str` | Declared data format (`'records'`, `'table'`, `'list'`, `'record'`; viewer default `'records'`). |

## Response handling

- **JSON** — a bare array of rows works directly: array-of-objects becomes a
  records dataset (columns from the first row), array-of-arrays needs declared
  `columns`. A full `{columns, dtypes, format, data}` dataset object also
  works, and its fields **win over** the declaration.
- **CSV** — always parses into a records dataset with the header row as
  columns; numeric-looking cells are auto-typed, and declared `dtypes` still
  drive date conversion.

## Refresh

With `refresh_interval`, the viewer re-fetches every N seconds and swaps data
in place — no flicker, no lost view state (sort, calendar view, ...). A failed
refresh keeps the last good data.

## Interactions

- **Derived datasets** — `add_derived_dataset(..., source="live_sales")` works
  with a remote source: derivation waits for the fetch and re-runs on every
  refresh.
- **`get_value()`** raises `ValueError` for remote datasets — the data only
  exists in the browser, not at compile time.
- **Viewer validation** runs after the fetches settle when remote datasets are
  present, so column checks see the real response
  (see [Linting](linting.md)).

## Validation

`add_remote_dataset` raises `ValueError` for the mistakes the viewer would
warn about: an empty `url`, an unknown `response_type`, `extract` with
`response_type="csv"`, a negative or non-numeric `refresh_interval`,
non-string `headers` values, an unknown `format`, and mismatched
`columns`/`dtypes` lengths.

## Related

- [Datasets & compression](datasets.md) — embedded datasets via `add_df`.
- [Derived datasets](derived-datasets.md) — browser-side filter/aggregate.
- [Linting](linting.md) — viewer-side validation warnings.
