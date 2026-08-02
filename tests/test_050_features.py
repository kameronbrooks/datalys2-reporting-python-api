"""
Tests for the non-calendar dl2 0.5.0 features: remote datasets, chart image
export props, and date/datetime dtype inference in add_df.
"""

import sys
import os
import datetime
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from dl2_reports import (
    Area,
    Bar,
    Boxplot,
    DL2Report,
    Gauge,
    Heatmap,
    Histogram,
    Line,
    Pie,
    Scatter,
)
from dl2_reports.components.base import ReportTreeComponent


class TestRemoteDatasets(unittest.TestCase):
    def _report(self):
        return DL2Report("Remote Test")

    def test_dataset_entry_shape(self):
        report = self._report()
        report.add_remote_dataset(
            "live",
            "https://example.com/data.json",
            response_type="json",
            extract="result.rows",
            headers={"Authorization": "Bearer x"},
            refresh_interval=30,
            columns=["Region", "Amount"],
            dtypes=["string", "number"],
            format="records",
        )
        self.assertEqual(report.datasets["live"], {
            "id": "live",
            "url": "https://example.com/data.json",
            "responseType": "json",
            "extract": "result.rows",
            "headers": {"Authorization": "Bearer x"},
            "refreshInterval": 30,
            "format": "records",
            "columns": ["Region", "Amount"],
            "dtypes": ["string", "number"],
        })

    def test_minimal_entry_omits_optionals(self):
        report = self._report()
        report.add_remote_dataset("live", "https://example.com/d.json")
        self.assertEqual(report.datasets["live"], {"id": "live", "url": "https://example.com/d.json"})

    def test_chaining(self):
        report = self._report()
        self.assertIs(report.add_remote_dataset("live", "https://a.com"), report)

    def test_url_required(self):
        for bad in ["", "   ", None, 42]:
            with self.assertRaises(ValueError):
                self._report().add_remote_dataset("live", bad)

    def test_bad_response_type(self):
        with self.assertRaises(ValueError):
            self._report().add_remote_dataset("live", "https://a.com", response_type="xml")

    def test_extract_with_csv(self):
        with self.assertRaises(ValueError):
            self._report().add_remote_dataset(
                "live", "https://a.com", response_type="csv", extract="a.b"
            )

    def test_extract_with_json_ok(self):
        report = self._report()
        report.add_remote_dataset("live", "https://a.com", response_type="json", extract="a.b")
        report.add_remote_dataset("live2", "https://a.com", extract="a.b")  # json is the default

    def test_bad_refresh_interval(self):
        for bad in [-1, -0.5, "60", True]:
            with self.assertRaises(ValueError):
                self._report().add_remote_dataset("live", "https://a.com", refresh_interval=bad)

    def test_zero_refresh_interval_ok(self):
        report = self._report()
        report.add_remote_dataset("live", "https://a.com", refresh_interval=0)
        self.assertEqual(report.datasets["live"]["refreshInterval"], 0)

    def test_bad_headers(self):
        for bad in [{"a": 1}, {1: "a"}, ["a"], "a"]:
            with self.assertRaises(ValueError):
                self._report().add_remote_dataset("live", "https://a.com", headers=bad)

    def test_bad_format(self):
        with self.assertRaises(ValueError):
            self._report().add_remote_dataset("live", "https://a.com", format="rows")

    def test_columns_dtypes_length_mismatch(self):
        with self.assertRaises(ValueError):
            self._report().add_remote_dataset(
                "live", "https://a.com", columns=["a", "b"], dtypes=["string"]
            )

    def test_get_value_raises(self):
        report = self._report()
        report.add_remote_dataset("live", "https://a.com")
        with self.assertRaises(ValueError) as ctx:
            report.get_value("live", "Amount")
        self.assertIn("remote dataset", str(ctx.exception))

    def test_derived_from_remote_compiles(self):
        report = DL2Report("Remote Test", compress_visuals=False)
        report.add_remote_dataset("live", "https://a.com")
        report.add_derived_dataset("filtered", "live")
        html = report.compile()
        self.assertIn('"source": "live"', html)

    def test_headers_keys_survive_verbatim(self):
        report = DL2Report("Remote Test", compress_visuals=False)
        report.add_remote_dataset(
            "live", "https://a.com", headers={"X-Api-Key": "abc", "snake_case_key": "v"}
        )
        html = report.compile()
        self.assertIn('"X-Api-Key"', html)
        self.assertIn('"snake_case_key"', html)


class TestChartExportProps(unittest.TestCase):
    CHARTS = [
        (Line, dict(x_column="X", y_columns=["Y"])),
        (Area, dict(x_column="X", y_columns=["Y"])),
        (Bar, dict(x_column="X", y_columns=["Y"])),
        (Bar, dict(x_column="X", y_columns=["Y"], stacked=True)),
        (Pie, dict(category_column="C", value_column="V")),
        (Scatter, dict(x_column="X", y_column="Y")),
        (Histogram, dict(column="X")),
        (Heatmap, dict(x_column="X", y_column="Y", value_column="V")),
        (Boxplot, dict(data_column="X")),
        (Gauge, dict(value_column="V")),
    ]

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1

    def test_export_props_serialized_on_every_chart(self):
        for cls, kwargs in self.CHARTS:
            with self.subTest(chart=cls.__name__, kwargs=kwargs):
                d = cls(
                    "data",
                    enable_export=False,
                    export_file_name="my-chart",
                    context_menu=False,
                    **kwargs,
                ).to_dict()
                self.assertEqual(d["enableExport"], False)
                self.assertEqual(d["exportFileName"], "my-chart")
                self.assertEqual(d["contextMenu"], False)

    def test_export_props_absent_by_default(self):
        for cls, kwargs in self.CHARTS:
            with self.subTest(chart=cls.__name__):
                d = cls("data", **kwargs).to_dict()
                self.assertNotIn("enableExport", d)
                self.assertNotIn("exportFileName", d)
                self.assertNotIn("contextMenu", d)

    def test_bar_types_preserved(self):
        clustered = Bar("data", x_column="X", y_columns=["Y"], enable_export=True)
        stacked = Bar("data", x_column="X", y_columns=["Y"], stacked=True, enable_export=True)
        self.assertEqual(clustered.to_dict()["type"], "clusteredBar")
        self.assertEqual(stacked.to_dict()["type"], "stackedBar")

    def test_legacy_helper_accepts_export_props(self):
        report = DL2Report("Export Test")
        report.add_df("data", pd.DataFrame({"X": ["a"], "Y": [1]}))
        row = report.add_page("P").add_row()
        line = row.add_line("data", x_column="X", y_columns=["Y"], export_file_name="trend")
        self.assertEqual(line.to_dict()["exportFileName"], "trend")
        # modeled props are not routed to extra, so the lint stays quiet
        self.assertEqual(getattr(line, "_legacy_extra_keys", []), [])


class TestDtypeInference(unittest.TestCase):
    def _dtypes(self, df, **kwargs):
        report = DL2Report("Dtype Test")
        report.add_df("d", df, **kwargs)
        return dict(zip(report.datasets["d"]["columns"], report.datasets["d"]["dtypes"]))

    def test_midnight_only_column_is_date(self):
        df = pd.DataFrame({"Day": [datetime.date(2026, 3, 1), datetime.date(2026, 3, 2)]})
        self.assertEqual(self._dtypes(df)["Day"], "date")

    def test_timed_column_is_datetime(self):
        df = pd.DataFrame({
            "At": [datetime.datetime(2026, 3, 1, 9, 30), datetime.datetime(2026, 3, 2, 0, 0)]
        })
        self.assertEqual(self._dtypes(df)["At"], "datetime")

    def test_all_midnight_datetimes_are_date(self):
        df = pd.DataFrame({
            "At": [datetime.datetime(2026, 3, 1, 0, 0), datetime.datetime(2026, 3, 2, 0, 0)]
        })
        self.assertEqual(self._dtypes(df)["At"], "date")

    def test_nat_values_ignored(self):
        df = pd.DataFrame({"At": pd.to_datetime([None, "2026-03-01 09:00"])})
        self.assertEqual(self._dtypes(df)["At"], "datetime")

    def test_other_dtypes_unchanged(self):
        df = pd.DataFrame({"S": ["a"], "N": [1.5], "B": [True]})
        dtypes = self._dtypes(df)
        self.assertEqual(dtypes, {"S": "string", "N": "number", "B": "boolean"})

    def test_dtype_overrides_win(self):
        df = pd.DataFrame({
            "Day": [datetime.date(2026, 3, 1)],
            "N": [1],
        })
        dtypes = self._dtypes(df, dtype_overrides={"Day": "datetime", "N": "string"})
        self.assertEqual(dtypes["Day"], "datetime")
        self.assertEqual(dtypes["N"], "string")

    def test_dtype_overrides_unknown_column_raises(self):
        df = pd.DataFrame({"N": [1]})
        with self.assertRaises(ValueError):
            self._dtypes(df, dtype_overrides={"Nope": "date"})


if __name__ == "__main__":
    unittest.main()
