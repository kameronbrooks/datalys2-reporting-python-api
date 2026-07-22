# Report Configuration

Constructing, configuring, compiling, and saving a `DL2Report`.

## `DL2Report(...)`

```python
from dl2_reports import DL2Report

report = DL2Report(
    title="Sales Report",
    description="Weekly sales overview",
    author="Data Team",
    compress_visuals=True,          # default
    report_id="sales-weekly",       # stable id for view-state persistence
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `title` | `str` | (required) | Report title (browser tab + header). |
| `description` | `str` | `""` | Header description. |
| `author` | `str` | `""` | Author name shown in the header. |
| `compress_visuals` | `bool` | `True` | Gzip-compress the report-config JSON (see [Datasets & compression](datasets.md#compression)). |
| `cdn_url` | `str` | jsDelivr | Base URL for the viewer JS/CSS. The `DL2_CDN_URL` environment variable overrides both this and the default. |
| `report_id` | `str` | `None` | Stable identifier emitted as `<meta name="report-id">` — namespaces [persisted view state](persistent-view-state.md). Set it if the title may change. |

## Metadata

The compiled `<head>` automatically includes `title`, `description`, `author`,
`dl-version` (the targeted viewer version), and `last-updated` (set to the
compile time). Add or override meta tags with:

```python
report.set_meta("dl2-validate", "false")     # disable viewer validation warnings
report.set_report_id("sales-weekly")         # same as the report_id kwarg
```

Meta tags the viewer reads:

| Meta name | Purpose |
|-----------|---------|
| `report-id` | *(dl2 0.4+)* Namespace for persisted view state. |
| `dl2-validate` | *(dl2 0.3+)* `"false"` disables config validation warnings ([Linting](linting.md)). |
| `gc-compressed-data` | Free compressed source strings after decompression (set automatically by `add_df(compress=True)`). |

## Viewer assets (CDN)

The report loads `datalys2-reports.min.js` and `dl2-style.css` from
`https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest/dist` by
default. Point elsewhere (a pinned version, or a self-hosted copy for offline
use) with `cdn_url=` or the `DL2_CDN_URL` environment variable.

## Compile / save / show

| Method | Description |
|--------|-------------|
| `report.compile(strict=False)` | Returns the full HTML string. Lints props ([details](linting.md)); `strict=True` raises on unknown props. Also validates that derived-dataset sources exist. |
| `report.save(filename)` | Writes `compile()` output to disk (UTF-8). |
| `report.show(height=800)` | Renders in Jupyter via an IFrame — see [Jupyter support](jupyter.md). |

## Structure-building methods

| Method | Returns | Description |
|--------|---------|-------------|
| `report.add_df(name, df, ...)` | `DL2Report` | Register a dataset — [Datasets](datasets.md). |
| `report.add_derived_dataset(name, source, ...)` | `DL2Report` | Browser-computed dataset — [Derived datasets](derived-datasets.md). |
| `report.add_page(title, description=None, last_updated=None)` | `Page` | Add a page (a tab in the report). |
| `report.add_modal(id, title, description=None)` | `Modal` | Add a global modal — [Modals](modals.md). |
| `report.get_value(name, column, row_index=-1)` | value | Read a dataset value — [Reading values](reading-values.md). |

All components in the tree expose `.get_report()` to walk back to the root:

```python
visual = layout.add_visual("line", "my_data")
report = visual.get_report()
```
