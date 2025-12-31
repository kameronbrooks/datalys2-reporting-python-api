from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional

import base64
import datetime
import gzip
import html
import json

import pandas as pd

from .components import Layout, Modal, Page, ReportTreeComponent, Visual
from .serialization import camel_case_dict, make_dataset_serializable


class DL2Report:
    # These are assigned at module import time to preserve the historical
    # API surface: DL2Report.Layout, DL2Report.Visual, etc.
    ReportTreeComponent: ClassVar[type[ReportTreeComponent]]
    Visual: ClassVar[type[Visual]]
    Layout: ClassVar[type[Layout]]
    Page: ClassVar[type[Page]]
    Modal: ClassVar[type[Modal]]

    def __init__(self, title: str, description: str = "", author: str = ""):
        """Initializes a new DL2Report."""

        self.title = title
        self.description = description
        self.author = author
        self.pages: List[Page] = []
        self.modals: List[Modal] = []
        self.datasets: Dict[str, Dict[str, Any]] = {}
        self.compressed_datasets: Dict[str, str] = {}
        self.css_url = "https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest/dist/dl2-style.css"
        self.js_url = "https://cdn.jsdelivr.net/gh/kameronbrooks/datalys2-reporting@latest/dist/datalys2-reports.min.js"
        self.meta_tags: Dict[str, str] = {}

    # Compatibility: keep these helpers on DL2Report
    @staticmethod
    def _camel_case_dict(d: Dict[str, Any]) -> Dict[str, Any]:
        return camel_case_dict(d)

    @staticmethod
    def _make_dataset_serializable(dataset: Dict[str, Any]) -> Dict[str, Any]:
        return make_dataset_serializable(dataset)

    def get_report(self) -> DL2Report:
        return self

    def add_df(
        self,
        name: str,
        df: pd.DataFrame,
        format: str = "records",
        compress: bool = False,
        timestamp_format: str = "iso",
    ) -> DL2Report:
        columns = df.columns.tolist()
        dtypes: List[str] = []
        for dtype in df.dtypes:
            if pd.api.types.is_numeric_dtype(dtype):
                dtypes.append("number")
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                dtypes.append("date")
            else:
                dtypes.append("string")

        # Handle datetime formatting
        for col in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                continue

            # Normalize to UTC so tz-aware and naive datetimes behave consistently.
            # Naive datetimes are treated as UTC.
            series_utc = pd.to_datetime(df[col], utc=True)

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

    def add_page(self, title: str, description: Optional[str] = None) -> Page:
        page = Page(title, description)
        page.parent = self
        self.pages.append(page)
        return page

    def add_modal(self, id: str, title: str, description: Optional[str] = None) -> Modal:
        modal = Modal(id, title, description)
        modal.parent = self
        self.modals.append(modal)
        return modal

    def set_meta(self, name: str, content: str) -> DL2Report:
        self.meta_tags[name] = content
        return self

    def compile(self) -> str:
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

        compressed_scripts = ""
        for script_id, b64_data in self.compressed_datasets.items():
            compressed_scripts += f'    <script id="{script_id}" type="text/b64-gzip">{b64_data}</script>\n'

        compiled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <meta name="dl-version" content="0.2.2">
    <meta name="description" content="{self.description}">
    <meta name="author" content="{self.author}">
    <meta name="last-updated" content="{datetime.datetime.now().isoformat()}">
{meta_html}
    <link rel="stylesheet" href="{self.css_url}">
</head>
<body>
{compressed_scripts}
    <div id="root"></div>
    <script id="report-data" type="application/json">
{report_data_json}
    </script>
    <script src="{self.js_url}"></script>
</body>
</html>"""
        return compiled_html

    def save(self, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.compile())

    def show(self, height: int = 800):
        try:
            from IPython.display import IFrame

            b64_html = base64.b64encode(self.compile().encode("utf-8")).decode("utf-8")
            data_uri = f"data:text/html;base64,{b64_html}"
            return IFrame(data_uri, width="100%", height=height)
        except ImportError:
            print("IPython not found. Save the report to an HTML file to view it.")

    def _repr_html_(self):
        escaped_html = html.escape(self.compile())
        return f'<iframe srcdoc="{escaped_html}" width="100%" height="800px" style="border:none;"></iframe>'


# Preserve the public API surface area: allow users to access these as DL2Report.Layout, etc.
DL2Report.ReportTreeComponent = ReportTreeComponent
DL2Report.Visual = Visual
DL2Report.Layout = Layout
DL2Report.Page = Page
DL2Report.Modal = Modal
