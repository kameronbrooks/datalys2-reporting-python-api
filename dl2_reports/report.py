from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional, Union

import base64
import datetime
import gzip
import html
import json
import os
import pandas as pd

from .components import Layout, Modal, Page, ReportTreeComponent, Tabs, Visual
from .filters import validate_filter
from .aggregates import validate_aggregate
from .formulas import and_merge, parse_datasource
from .serialization import camel_case_dict, make_dataset_serializable, convert_nan_to_none

DL2_VERSION = "0.4.1"

DEFAULT_CDN = f"https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest/dist"
JS_URI = f"/datalys2-reports.min.js"
CSS_URI = f"/dl2-style.css"

class DL2Report:
    # These are assigned at module import time to preserve the historical
    # API surface: DL2Report.Layout, DL2Report.Visual, etc.
    ReportTreeComponent: ClassVar[type[ReportTreeComponent]]
    Visual: ClassVar[type[Visual]]
    Layout: ClassVar[type[Layout]]
    Page: ClassVar[type[Page]]
    Modal: ClassVar[type[Modal]]
    Tabs: ClassVar[type[Tabs]]

    def __init__(
            self,
            title: str,
            description: str = "",
            author: str = "",
            compress_visuals: bool = True,
            cdn_url: Optional[str] = None,
            report_id: Optional[str] = None,
            ):
        """
        Initializes a new DL2Report.

        Args:
            title (str): The title of the report.
            description (str, optional): A brief description of the report. Defaults to "".
            author (str, optional): The author of the report. Defaults to "".
            compress_visuals (bool, optional): Whether to compress the report data. Defaults to True.
            cdn_url (Optional[str], optional): The base URL for the CDN. Defaults to None.
            report_id (Optional[str], optional): Stable identifier for the report, emitted as
                <meta name="report-id">. dl2 0.4+ namespaces persisted view state (table
                sort/columns/grouping, active tabs) by this id; without it the viewer falls
                back to the title, then the file path. Set it if the title may change.
        """
        base_url = os.environ.get("DL2_CDN_URL", cdn_url or DEFAULT_CDN).rstrip("/")
        css_url = f"{base_url}{CSS_URI}"
        js_url = f"{base_url}{JS_URI}"

        self.title = title
        self.description = description
        self.author = author
        self.pages: List[Page] = []
        self.modals: List[Modal] = []
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.compressed_datasets: Dict[str, str] = {}
        self.css_url = css_url
        self.js_url = js_url
        self.meta_tags: Dict[str, str] = {}
        self.compress_visuals = compress_visuals
        if report_id:
            self.set_report_id(report_id)

    # Compatibility: keep these helpers on DL2Report
    @staticmethod
    def _camel_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to convert dictionary keys to camelCase."""
        return camel_case_dict(d)

    @staticmethod
    def _make_dataset_serializable(dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Internal helper to make a dataset serializable."""
        return make_dataset_serializable(dataset)

    def get_report(self) -> DL2Report:
        """
        Returns the report instance itself.
        
        Returns:
            DL2Report: The current report instance.
        """
        return self
    
    def get_value(self, data_source_name: str, column_name: str, row_index: int = -1) -> Any:
        """
        Retrieves a value from a specific dataset.

        Args:
            data_source_name (str): The name of the dataset.
            column_name (str): The name of the column.
            row_index (int): The index of the row. Defaults to -1 (last row).

        Returns:
            Any: The value at the specified location.
        """
        dataset = self.datasets.get(data_source_name)
        if dataset is None:
            raise ValueError(f"Dataset '{data_source_name}' not found.")
        if "source" in dataset:
            raise ValueError(
                f"Dataset '{data_source_name}' is a derived dataset — it is computed in the "
                "browser at load time, so its values are not available at compile time. "
                "Compute the value with pandas from the source DataFrame instead."
            )
        if "url" in dataset:
            raise ValueError(
                f"Dataset '{data_source_name}' is a remote dataset — it is fetched in the "
                "browser at load time, so its values are not available at compile time. "
                "Fetch and inspect the data yourself if you need it while building."
            )
        # Use the stored DataFrame when available (data[] is emptied when compress=True)
        df = dataset.get("_df")
        if df is None:
            df = pd.DataFrame(dataset["data"])

        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in dataset '{data_source_name}'.")
        
        if row_index < 0:
            row_index += len(df)

        if row_index < 0 or row_index >= len(df):
            raise IndexError(f"Row index {row_index} out of range for dataset '{data_source_name}'.")
        
        return df.iloc[row_index][column_name]

    def add_df(
        self,
        name: str,
        df: pd.DataFrame,
        format: str = "records",
        compress: bool = False,
        timestamp_format: str = "iso",
        dtype_overrides: Optional[Dict[str, str]] = None,
    ) -> DL2Report:
        """
        Adds a pandas DataFrame as a dataset to the report.

        Date-like columns are declared with dtype ``"date"`` when every value is
        midnight UTC, and ``"datetime"`` when any value carries a time of day
        (dl2 0.5+ — the calendar visual renders ``"date"`` columns as all-day
        events and ``"datetime"`` columns as timed events on the hour grid).

        Args:
            name (str): The unique identifier for the dataset.
            df (pd.DataFrame): The pandas DataFrame containing the data.
            format (str, optional): The format to serialize the data ('records' or 'values'). Defaults to "records".
            compress (bool, optional): Whether to compress the dataset using Gzip. Defaults to False.
            timestamp_format (str, optional): The format for datetime columns ('iso' or 'epoch'). Defaults to "iso".
            dtype_overrides (dict, optional): Per-column dtype declarations that
                override the inference, e.g. ``{"Due": "datetime"}`` to force
                timed calendar events for a midnight-only column. Keys must be
                column names of ``df``.

        Returns:
            DL2Report: The report instance for method chaining.
        """
        # Make a deep copy of the DataFrame to avoid modifying the original
        df = df.copy(deep=True)

        columns = df.columns.tolist()

        if dtype_overrides:
            unknown = [col for col in dtype_overrides if col not in df.columns]
            if unknown:
                raise ValueError(
                    f"dtype_overrides references unknown column(s) {unknown} "
                    f"for dataset '{name}'."
                )
        
        # Track which columns are dates BEFORE conversion
        date_columns = set()
        
        # First pass: identify and potentially convert date columns
        for col in df.columns:
            # Check if already a datetime type
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_columns.add(col)
            # Check if object type that might contain dates
            elif df[col].dtype == 'object':
                # Try to infer if this might be a date column
                try:
                    # Sample a few non-null values to see if they're datetime-like
                    sample = df[col].dropna().head(10)
                    if len(sample) > 0:
                        pd.to_datetime(sample)
                        # If no error, convert the whole column
                        df[col] = pd.to_datetime(df[col])
                        date_columns.add(col)
                except (ValueError, TypeError):
                    # Not a date column, continue
                    pass
        
        # Capture dtypes BEFORE datetime conversion to serialization format
        dtypes: List[str] = []
        for col in df.columns:
            dtype = df[col].dtype

            if dtype_overrides and col in dtype_overrides:
                dtypes.append(dtype_overrides[col])
            elif pd.api.types.is_bool_dtype(dtype):
                dtypes.append("boolean")
            elif col in date_columns:
                # "datetime" when any value carries a time of day, else "date"
                # (dl2 0.5+ distinguishes all-day vs timed calendar events)
                values = pd.to_datetime(df[col]).dropna()
                has_time = bool((values != values.dt.normalize()).any())
                dtypes.append("datetime" if has_time else "date")
            elif pd.api.types.is_numeric_dtype(dtype):
                dtypes.append("number")
            else:
                dtypes.append("string")

        # Handle datetime formatting for serialization
        for col in date_columns:
            # Normalize to UTC so tz-aware and naive datetimes behave consistently.
            # Naive datetimes are treated as UTC.
            series_utc = pd.to_datetime(df[col])

            if timestamp_format == "iso":
                df[col] = series_utc.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            elif timestamp_format == "epoch":
                # pandas stores datetimes in ns; convert to whole seconds.
                df[col] = series_utc.astype("int64") // 1_000_000_000
            else:
                raise ValueError("Invalid timestamp_format. Use 'iso' or 'epoch'.")

        if format == "records":
            data = df.to_dict(orient="records")
        else:
            data = df.values.tolist()

        # Convert NaN to None for JSON serialization
        data = convert_nan_to_none(data)

        dataset_entry: Dict[str, Any] = {
            "id": name,
            "format": format,
            "columns": columns,
            "dtypes": dtypes,
            "data": data,
            "_df": df,  # Store original DataFrame for reference
        }

        if compress:
            # Convert data to JSON string, then gzip, then base64
            json_data = json.dumps(data)
            compressed = gzip.compress(json_data.encode("utf-8"))
            b64_data = base64.b64encode(compressed).decode("utf-8")

            script_id = f"compressed-data-{name}"
            self.compressed_datasets[script_id] = b64_data

            dataset_entry["compression"] = "gzip"
            dataset_entry["compressedData"] = script_id
            dataset_entry["data"] = []

            # Enable GC for compressed data
            self.set_meta("gc-compressed-data", "true")

        self.datasets[name] = dataset_entry
        return self

    def add_derived_dataset(
        self,
        name: str,
        source: str,
        filter: Optional[Dict[str, Any]] = None,
        aggregate: Optional[Dict[str, Any]] = None,
    ) -> DL2Report:
        """
        Adds a derived dataset (dl2 0.3+) computed from another dataset in the browser
        at load time — no extra data is embedded in the HTML.

        Chains are supported (a derived dataset may use another derived dataset as its
        source). Declaration order does not matter; sources are checked at compile().

        Args:
            name (str): The unique identifier for the derived dataset.
            source (str): The id of the dataset to derive from, or a pandas-style
                formula like ``"sales[Region == 'North']"`` (see
                :mod:`dl2_reports.formulas`); the formula's filter AND-combines
                with ``filter=``. Column projection (``[[...]]``) is not supported
                here — derived datasets only support filter + aggregate.
            filter (dict, optional): A filter expression (see :mod:`dl2_reports.filters`)
                applied to the source rows.
            aggregate (dict, optional): An aggregate spec (see :mod:`dl2_reports.aggregates`)
                applied after the filter. Note: without an ``as`` name, aggregate output
                columns are named ``"{fn}_{column}"`` (e.g. ``sum_amount``).

        Returns:
            DL2Report: The report instance for method chaining.
        """
        spec = parse_datasource(source)
        if spec.columns is not None:
            raise ValueError(
                f"Derived dataset '{name}': column projection ('[[...]]') is not supported "
                f"on derived dataset sources; derived datasets support only 'filter' and "
                f"'aggregate'."
            )
        source = spec.dataset_id
        filter = and_merge(spec.filter, filter)

        if filter is not None:
            validate_filter(filter)
        if aggregate is not None:
            validate_aggregate(aggregate)

        dataset_entry: Dict[str, Any] = {
            "id": name,
            "source": source,
        }
        if filter is not None:
            dataset_entry["filter"] = camel_case_dict(filter)
        if aggregate is not None:
            dataset_entry["aggregate"] = camel_case_dict(aggregate)

        self.datasets[name] = dataset_entry
        return self

    _REMOTE_RESPONSE_TYPES = ("json", "csv")
    _REMOTE_FORMATS = ("table", "records", "list", "record")

    def add_remote_dataset(
        self,
        name: str,
        url: str,
        response_type: Optional[str] = None,
        extract: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        refresh_interval: Union[int, float, None] = None,
        columns: Optional[List[str]] = None,
        dtypes: Optional[List[str]] = None,
        format: Optional[str] = None,
    ) -> DL2Report:
        """
        Adds a remote dataset (dl2 0.5+) fetched from a URL in the browser at load
        time — no data is embedded in the HTML. The report renders immediately;
        visuals bound to the dataset show a loading placeholder until the fetch
        settles. The endpoint must be CORS-accessible from wherever the report is
        opened.

        A JSON response may be a bare array of rows or a full
        ``{columns, dtypes, format, data}`` dataset object (response fields win
        over this declaration). A CSV response always parses into a records
        dataset with its header row as columns. Declared ``dtypes`` still drive
        date conversion — declare ``"date"``/``"datetime"`` columns so tables,
        charts, and calendars treat them as dates.

        Derived datasets (:meth:`add_derived_dataset`) may use a remote dataset
        as their source; derivation waits for the fetch and re-runs on every
        refresh.

        Warning:
            ``headers`` are embedded as plain text in the compiled HTML — anyone
            who can open the report can read them. Only use tokens that are safe
            to treat as public.

        Args:
            name (str): The unique identifier for the dataset.
            url (str): The URL to fetch the data from.
            response_type (str, optional): 'json' (viewer default) or 'csv'.
            extract (str, optional): Dot-path to the rows inside a JSON wrapper
                object, e.g. ``"result.rows"``. JSON only.
            headers (dict, optional): HTTP request headers (string values), e.g.
                ``{"Authorization": "Bearer ..."}``. See the warning above.
            refresh_interval (int | float, optional): Re-fetch every N seconds.
                Omit or 0 to fetch once. Refreshes swap data in place and a
                failed refresh keeps the last good data.
            columns (list, optional): Declared column names (required for JSON
                array-of-arrays responses; otherwise inferred from the response).
            dtypes (list, optional): Declared column dtypes, aligned with
                ``columns`` (e.g. ``["string", "number", "datetime"]``).
            format (str, optional): Declared data format ('records', 'table',
                'list', or 'record'; viewer default 'records').

        Returns:
            DL2Report: The report instance for method chaining.

        Raises:
            ValueError: On an empty url or option combinations the viewer would
                reject (mirrors the viewer's remote-dataset validation warnings).
        """
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"Remote dataset '{name}': url must be a non-empty string.")
        if response_type is not None and response_type not in self._REMOTE_RESPONSE_TYPES:
            raise ValueError(
                f"Remote dataset '{name}': response_type must be one of "
                f"{self._REMOTE_RESPONSE_TYPES}, got {response_type!r}."
            )
        if extract is not None and response_type == "csv":
            raise ValueError(
                f"Remote dataset '{name}': extract only applies to JSON responses."
            )
        if refresh_interval is not None:
            if isinstance(refresh_interval, bool) or not isinstance(refresh_interval, (int, float)):
                raise ValueError(
                    f"Remote dataset '{name}': refresh_interval must be a number of "
                    f"seconds, got {refresh_interval!r}."
                )
            if refresh_interval < 0:
                raise ValueError(
                    f"Remote dataset '{name}': refresh_interval must be a positive number "
                    f"of seconds (or 0 to fetch once), got {refresh_interval!r}."
                )
        if headers is not None:
            if not isinstance(headers, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in headers.items()
            ):
                raise ValueError(
                    f"Remote dataset '{name}': headers must be a dict of string keys "
                    f"and string values."
                )
        if format is not None and format not in self._REMOTE_FORMATS:
            raise ValueError(
                f"Remote dataset '{name}': format must be one of {self._REMOTE_FORMATS}, "
                f"got {format!r}."
            )
        if columns is not None and dtypes is not None and len(columns) != len(dtypes):
            raise ValueError(
                f"Remote dataset '{name}': columns ({len(columns)}) and dtypes "
                f"({len(dtypes)}) must have the same length."
            )

        # Keys are emitted verbatim (datasets bypass camelCasing at serialization,
        # so headers keys also survive untouched).
        dataset_entry: Dict[str, Any] = {"id": name, "url": url}
        if response_type is not None:
            dataset_entry["responseType"] = response_type
        if extract is not None:
            dataset_entry["extract"] = extract
        if headers is not None:
            dataset_entry["headers"] = headers
        if refresh_interval is not None:
            dataset_entry["refreshInterval"] = refresh_interval
        if format is not None:
            dataset_entry["format"] = format
        if columns is not None:
            dataset_entry["columns"] = columns
        if dtypes is not None:
            dataset_entry["dtypes"] = dtypes

        self.datasets[name] = dataset_entry
        return self

    def add_page(self, title: str, description: Optional[str] = None, last_updated: Optional[str] = None) -> Page:
        """
        Adds a new page to the report.

        Args:
            title (str): The title of the page.
            description (str, optional): A description for the page. Defaults to None.
            last_updated (str, optional): The last updated date for the page. Defaults to None.

        Returns:
            Page: The newly created Page instance.
        """
        page = Page(title, description=description, last_updated=last_updated)
        page.parent = self
        self.pages.append(page)
        return page

    def add_modal(self, id: str, title: str, description: Optional[str] = None) -> Modal:
        """
        Adds a modal dialog to the report.

        Args:
            id (str): A unique identifier for the modal.
            title (str): The title of the modal.
            description (str, optional): A description for the modal. Defaults to None.

        Returns:
            Modal: The newly created Modal instance.
        """
        modal = Modal(id, title, description)
        modal.parent = self
        self.modals.append(modal)
        return modal

    def set_meta(self, name: str, content: str) -> DL2Report:
        """
        Sets a metadata tag in the report's HTML head.

        Args:
            name (str): The name attribute of the meta tag.
            content (str): The content attribute of the meta tag.

        Returns:
            DL2Report: The report instance for method chaining.
        """
        self.meta_tags[name] = content
        return self

    def set_report_id(self, report_id: str) -> DL2Report:
        """
        Sets the report's stable identifier (<meta name="report-id">).

        dl2 0.4+ uses this to namespace persisted view state in localStorage. Without
        it, the viewer falls back to the report title, then the file path.

        Args:
            report_id (str): The stable report identifier.

        Returns:
            DL2Report: The report instance for method chaining.
        """
        return self.set_meta("report-id", report_id)

    def compile(self, strict: bool = False) -> str:
        """
        Compiles the report into a complete HTML string.

        Props not modeled by the known visual types are reported as warnings
        (the JS viewer silently ignores unknown props, so typos are otherwise
        invisible). Pass ``extra={...}`` on a component to pass unmodeled props
        through without a warning.

        Args:
            strict (bool, optional): If True, raise instead of warning when
                unknown props are found. Defaults to False.

        Returns:
            str: The full HTML content of the report.

        Raises:
            ValueError: If a derived dataset references an unknown source dataset,
                or (with strict=True) if unknown props are found.
        """
        from .lint import lint_report

        issues = lint_report(self)
        if issues:
            if strict:
                raise ValueError("Unknown props found:\n" + "\n".join(issues))
            import warnings as _warnings

            for issue in issues:
                _warnings.warn(f"[dl2] {issue}", UserWarning, stacklevel=2)

        for name, ds in self.datasets.items():
            source = ds.get("source")
            if source is not None and source not in self.datasets:
                raise ValueError(
                    f"Derived dataset '{name}' references unknown source dataset '{source}'."
                )

        report_data: Dict[str, Any] = {
            "pages": [p.to_dict() for p in self.pages],
            "datasets": {name: self._make_dataset_serializable(ds) for name, ds in self.datasets.items()},
        }
        if self.modals:
            report_data["modals"] = [m.to_dict() for m in self.modals]

        report_data_json = json.dumps(report_data, indent=4)

        meta_html = ""
        for name, content in self.meta_tags.items():
            meta_html += f'    <meta name="{name}" content="{content}">\n'

        # Generate compressed scripts for any compressed datasets
        compressed_scripts = ""
        for script_id, b64_data in self.compressed_datasets.items():
            compressed_scripts += f'    <script id="{script_id}" type="text/b64-gzip">{b64_data}</script>\n'

        # Determine the appropriate script type and content for the report data
        report_data_html = f'<script id="report-data" type="application/json">{report_data_json}</script>'
        if self.compress_visuals:
            try:
                compressed_report_data = gzip.compress(report_data_json.encode("utf-8"))
                b64_report_data = base64.b64encode(compressed_report_data).decode("utf-8")
                report_data_html = f'<script id="report-data" type="text/b64-gzip">{b64_report_data}</script>'
            except Exception as e:
                print(f"Error compressing report data: {e}")
                report_data_html = f'<script id="report-data" type="application/json">{report_data_json}</script>'

        compiled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <meta name="dl-version" content="{DL2_VERSION}">
    <meta name="description" content="{self.description}">
    <meta name="author" content="{self.author}">
    <meta name="last-updated" content="{datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')}">
{meta_html}
    <link rel="stylesheet" href="{self.css_url}">
</head>
<body>
{compressed_scripts}
    <div id="root"></div>
    {report_data_html}
    <script src="{self.js_url}"></script>
</body>
</html>"""
        return compiled_html

    def save(self, filename: str):
        """
        Saves the compiled report to a file.

        Args:
            filename (str): The path where the HTML report should be saved.
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.compile())

    def show(self, height: int = 800):
        """
        Displays the report in a Jupyter Notebook environment.

        Args:
            height (int, optional): The height of the iframe in pixels. Defaults to 800.

        Returns:
            IPython.display.IFrame: An IFrame containing the report, if IPython is available.
        """
        try:
            from IPython.display import IFrame

            b64_html = base64.b64encode(self.compile().encode("utf-8")).decode("utf-8")
            data_uri = f"data:text/html;base64,{b64_html}"
            return IFrame(data_uri, width="100%", height=height)
        except ImportError:
            print("IPython not found. Save the report to an HTML file to view it.")

    def _repr_html_(self):
        """
        Returns the HTML representation of the report for Jupyter Notebook display.

        Returns:
            str: An HTML iframe string containing the report.
        """
        escaped_html = html.escape(self.compile())
        return f'<iframe srcdoc="{escaped_html}" width="100%" height="800px" style="border:none;"></iframe>'


# Preserve the public API surface area: allow users to access these as DL2Report.Layout, etc.
DL2Report.ReportTreeComponent = ReportTreeComponent
DL2Report.Visual = Visual
DL2Report.Layout = Layout
DL2Report.Page = Page
DL2Report.Modal = Modal
DL2Report.Tabs = Tabs
