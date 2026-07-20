# dl2-reports Python API — Architecture Notes

*Written 2026-07-20 as groundwork for the 0.3/0.4 feature update. Describes the package as of
package version 0.2.15 (targets JS runtime dl2 0.2.12).*

## What this package is

`dl2_reports` is a **config builder**: it produces a single self-contained HTML file containing

1. a `<script id="report-data">` JSON payload (optionally gzip+base64 compressed, `type="text/b64-gzip"`),
2. optional per-dataset compressed `<script type="text/b64-gzip">` blobs,
3. `<link>`/`<script>` tags pointing to the datalys2-reporting JS bundle on a CDN
   (`https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest/dist`, overridable via
   `DL2_CDN_URL` env var or the `cdn_url` ctor arg).

All rendering/interactivity lives in the JS runtime. The Python side only needs to **emit the right
JSON props** — so "implementing" a JS feature here mostly means adding typed helper methods,
serialization support, docs, and tests.

## Module map

| File | Role |
|------|------|
| [dl2_reports/report.py](../dl2_reports/report.py) | `DL2Report`: datasets (`add_df`), pages, modals, meta tags, `compile()`/`save()`/`show()`, `get_value()`. `DL2_VERSION` constant is stamped into `<meta name="dl-version">`. |
| [dl2_reports/components/base.py](../dl2_reports/components/base.py) | `ReportTreeComponent`: global auto-increment ids `elem-N` (`BASE_ID` class counter — tests reset it), `parent` chain, `get_report()`. |
| [dl2_reports/components/page.py](../dl2_reports/components/page.py) | `Page`: `title/description/last_updated` + `rows: List[Layout]`, `add_row()`. |
| [dl2_reports/components/modal.py](../dl2_reports/components/modal.py) | `Modal`: `id/title/description` + rows. Serialized into top-level `modals` array. |
| [dl2_reports/components/layout.py](../dl2_reports/components/layout.py) | `Layout` (direction + children + free-form props) and `CompileTimeConditional` (`on_condition`). `Layout` mixes in every `*Visual` helper class so `row.add_kpi(...)` etc. work. |
| [dl2_reports/components/visual.py](../dl2_reports/components/visual.py) | `Visual`: generic `type` + `dataset_id` + `props` bag, `otherElements` annotations, `add_trend()` (numpy fit via `utilities/analytics`), `copy()`, `get_value()`. |
| [dl2_reports/components/visuals/*.py](../dl2_reports/components/visuals/) | One mixin per visual type: typed keyword args → `props` dict → `add_visual(type, dataset_id, **props)`. |
| [dl2_reports/serialization.py](../dl2_reports/serialization.py) | `snake_to_camel`, recursive `camel_case_dict`, `make_dataset_serializable` (strips `_df`), `convert_nan_to_none`. |

## Serialization rules (the contract with the JS runtime)

- Python kwargs are snake_case; `to_dict()` converts keys to camelCase recursively
  (dicts and lists of dicts included). Anything with a `to_dict()` is serialized via it.
- Visuals serialize as `{type, elementType: "visual", id, datasetId?, ...props}`.
- Layouts serialize as `{type: "layout", direction, children: [...], ...props}` — note: **no `id`**
  is emitted for layouts today, even though they have one (relevant for 0.4 anchors/persist-state).
- Datasets are a dict keyed by name: `{id, format, columns, dtypes, data, [compression,
  compressedData]}` plus a private `_df` (stripped at compile). Dtypes are inferred as
  boolean/date/number/string; dates serialized ISO-UTC or epoch.
- Report JSON: `{pages: [...], datasets: {...}, modals?: [...]}`.

## Conventions to preserve when adding features

- **Helper-method pattern**: each visual mixin exposes `add_<type>(...)` with explicit typed
  kwargs, only setting props that are not `None`, then delegates to `add_visual`. Passthrough
  `**kwargs` always allowed (forward-compat with viewer props).
- Everything unknown flows through untouched — the API never validates against the JS schema, so
  new JS props already "work" via kwargs; helpers/docs/tests are what we add.
- `CompileTimeConditional` inherits all visual mixins; new helpers on `Layout` that create
  children must respect it (it forwards via `add_visual`; helpers built on `add_visual` work
  automatically, but helpers that construct child components directly — like a tabs container —
  need explicit forwarding).
- Element ids are consumed in creation order; golden tests depend on deterministic ids
  (`ReportTreeComponent.BASE_ID = 1` reset before each scenario).

## Testing infrastructure

- Golden HTML tests: [tests/scenarios.py](../tests/scenarios.py) holds report-builder functions;
  [tests/generate_goldens.py](../tests/generate_goldens.py) writes `tests/data/expected/<name>_{compressed,uncompressed}.html`
  with `datetime.now` and `gzip.compress` (mtime) patched for determinism;
  [tests/test_html_output.py](../tests/test_html_output.py) re-runs scenarios and string-compares.
- Behavior tests: `tests/test_get_value.py`, `tests/test_on_condition.py`.
- Adding a scenario = add function + register in `scenarios` dict + run `generate_goldens.py`.

## Versioning / release

- [versions.json](../versions.json) holds `package_version` (PyPI) and `dl2_version` (JS runtime
  compatibility). [tools/update_versions.py](../tools/update_versions.py) propagates them into
  `pyproject.toml`, `report.py` (`DL2_VERSION`), README/DOCUMENTATION headers, and rewrites the
  `dl-version` meta in all golden files.
- `build_and_publish.ps1` builds and publishes the wheel.
- CDN URL uses `@latest`, so generated reports pick up new JS automatically; `dl-version` meta is
  informational.
