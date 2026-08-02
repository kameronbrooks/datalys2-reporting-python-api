# Datasets & Compression

Datasets are registered once on the report with `add_df()` and referenced by
id from any number of visuals. The DataFrame is serialized into the HTML
(optionally gzip-compressed); a private copy is also kept in Python so
[`get_value()`](reading-values.md) and
[`add_trend()`](annotations.md) auto-coefficients work at build time.

## `report.add_df(name, df, format="records", compress=False, timestamp_format="iso", dtype_overrides=None)`

```python
import pandas as pd

report.add_df("salesData", pd.read_csv("sales.csv"), compress=True)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | (required) | Dataset id referenced by visuals. |
| `df` | `pd.DataFrame` | (required) | The data. Deep-copied — later mutations to your DataFrame don't affect the report. |
| `format` | `str` | `"records"` | `"records"` → list of `{col: value}` dicts. Any other value serializes as a list of row lists — use `"table"`, which the viewer understands. Records are self-describing; table format is smaller. |
| `compress` | `bool` | `False` | Gzip + base64 the data into a separate script tag. |
| `timestamp_format` | `str` | `"iso"` | Datetime serialization: `"iso"` (UTC ISO-8601 strings) or `"epoch"` (whole seconds). |
| `dtype_overrides` | `dict[str, str]` | `None` | *(dl2 0.5+)* Per-column dtype declarations that override inference, e.g. `dtype_overrides={"Due": "datetime"}`. Keys must be columns of the DataFrame (unknown keys raise `ValueError`). |

Returns the report, so calls chain.

## Dtypes

Column dtypes are inferred automatically and embedded so the viewer can
sort/filter/format type-aware: booleans → `boolean`, date-like columns →
`date` or `datetime` (see below), numerics → `number`, everything else →
`string`. Pass `dtype_overrides={...}` to override the inference per column.

### Dates

- Columns already `datetime64` are serialized as dates.
- **Object columns that look like dates are auto-converted**: a sample of
  values is parsed with `pd.to_datetime`, and if it succeeds the whole column
  is treated as a date column.
- Naive datetimes are treated as UTC; tz-aware datetimes are normalized to
  UTC.
- **`date` vs `datetime`** *(dl2 0.5+)*: a date-like column is declared
  `datetime` when any value has a nonzero time of day, `date` when every
  value is midnight UTC. (Previously all date-like columns were declared
  `date`.) This matters for the [calendar](../visuals/calendar.md) visual:
  `date` columns render as all-day events, `datetime` columns as timed
  events on the hour grid. Use `dtype_overrides` to force either, e.g.
  `report.add_df("events", df, dtype_overrides={"Due": "datetime"})`.

`NaN`/`NaT` values are serialized as `null`.

## Compression

**Always compress in production.** Large uncompressed datasets can fail to
load entirely; compression typically cuts file size 80–90% and the browser
decompresses on the fly with the native `DecompressionStream` API.

```python
report.add_df("salesData", large_df, compress=True)   # per-dataset
report = DL2Report(title="...", compress_visuals=True)  # report-config JSON (default True)
```

Two separate switches:

- `add_df(compress=True)` — compresses **that dataset's rows** into its own
  `<script type="text/b64-gzip">` tag, and sets the `gc-compressed-data` meta
  tag so the browser frees the base64 source strings after decompression.
- `DL2Report(compress_visuals=True)` (default) — compresses the whole
  **report-data config JSON** (pages, visuals, and any uncompressed
  datasets).

Leave data uncompressed only while debugging (to inspect raw JSON in the
HTML) or for tiny single-row KPI datasets.

## Formats and client-side features

[Filtering](filtering.md) and [aggregation](aggregation.md) operate on
`records` and `table` format datasets. The default (`records`) is always safe.

## Derived datasets

A dataset can also be **declared** rather than embedded — computed in the
browser from another dataset. See [Derived datasets](derived-datasets.md).
Or fetched from a URL at view time — see
[Remote datasets](remote-datasets.md) *(dl2 0.5+)*.

## Reading data back

`report.get_value(name, column, row_index=-1)` reads values from registered
datasets at build time — see [Reading values](reading-values.md). (Not
available for derived datasets, which exist only in the browser.)
