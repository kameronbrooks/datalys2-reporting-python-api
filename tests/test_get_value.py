"""
Tests for report.get_value() and Visual.get_value() with negative row indices.

Regression coverage for: get_value with row_index=-1 returning the second-to-last row
when the DataFrame has a non-default (e.g. 1-based) integer index.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from dl2_reports import DL2Report
from dl2_reports.components.base import ReportTreeComponent
from dl2_reports.components.visual import Visual


def _make_report_default_index():
    """DataFrame with default 0-based index (0, 1, 2)."""
    report = DL2Report("Test")
    df = pd.DataFrame({"value": [10, 20, 30]})
    report.add_df("data", df)
    return report


def _make_report_nondefault_index():
    """DataFrame with 1-based index (1, 2, 3) — the bug trigger."""
    report = DL2Report("Test")
    df = pd.DataFrame({"value": [10, 20, 30]}, index=[1, 2, 3])
    report.add_df("data", df)
    return report


def _make_report_gap_index():
    """DataFrame with a gap in the index (0, 5, 10)."""
    report = DL2Report("Test")
    df = pd.DataFrame({"value": [10, 20, 30]}, index=[0, 5, 10])
    report.add_df("data", df)
    return report


class TestReportGetValueNegativeIndex(unittest.TestCase):
    """Tests for report.get_value() with negative row_index."""

    # --- default 0-based index ---

    def test_minus_one_returns_last_row_default_index(self):
        report = _make_report_default_index()
        self.assertEqual(report.get_value("data", "value", -1), 30)

    def test_minus_two_returns_second_to_last_default_index(self):
        report = _make_report_default_index()
        self.assertEqual(report.get_value("data", "value", -2), 20)

    def test_minus_three_returns_first_row_default_index(self):
        report = _make_report_default_index()
        self.assertEqual(report.get_value("data", "value", -3), 10)

    # --- 1-based index (regression case) ---

    def test_minus_one_returns_last_row_nondefault_index(self):
        """Regression: row_index=-1 must return value=30, not value=20."""
        report = _make_report_nondefault_index()
        self.assertEqual(report.get_value("data", "value", -1), 30)

    def test_minus_two_returns_second_to_last_nondefault_index(self):
        report = _make_report_nondefault_index()
        self.assertEqual(report.get_value("data", "value", -2), 20)

    def test_minus_three_returns_first_row_nondefault_index(self):
        report = _make_report_nondefault_index()
        self.assertEqual(report.get_value("data", "value", -3), 10)

    # --- gap index ---

    def test_minus_one_returns_last_row_gap_index(self):
        """Regression: row_index=-1 must return value=30 even with gap index."""
        report = _make_report_gap_index()
        self.assertEqual(report.get_value("data", "value", -1), 30)

    def test_minus_two_returns_second_to_last_gap_index(self):
        report = _make_report_gap_index()
        self.assertEqual(report.get_value("data", "value", -2), 20)

    # --- positive index sanity checks ---

    def test_positive_index_zero_returns_first_row(self):
        report = _make_report_nondefault_index()
        self.assertEqual(report.get_value("data", "value", 0), 10)

    def test_positive_index_one_returns_second_row(self):
        report = _make_report_nondefault_index()
        self.assertEqual(report.get_value("data", "value", 1), 20)

    def test_positive_index_two_returns_last_row(self):
        report = _make_report_nondefault_index()
        self.assertEqual(report.get_value("data", "value", 2), 30)

    # --- out-of-range ---

    def test_out_of_range_positive_raises(self):
        report = _make_report_default_index()
        with self.assertRaises(IndexError):
            report.get_value("data", "value", 3)

    def test_out_of_range_negative_raises(self):
        report = _make_report_default_index()
        with self.assertRaises(IndexError):
            report.get_value("data", "value", -4)


class TestVisualGetValueNegativeIndex(unittest.TestCase):
    """Tests for Visual.get_value() with row_index=-1 in props."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1

    def _make_visual_report(self, index=None):
        report = DL2Report("Test")
        kwargs = {"value": [10, 20, 30]}
        df = pd.DataFrame(kwargs) if index is None else pd.DataFrame(kwargs, index=index)
        report.add_df("data", df)
        page = report.add_page("Page")
        row = page.add_row()
        return report, row

    def test_visual_get_value_minus_one_default_index(self):
        report, row = self._make_visual_report()
        vis = row.add_kpi(dataset_id="data", value_column="value", row_index=-1, title="T")
        self.assertEqual(vis.get_value(), 30)

    def test_visual_get_value_minus_one_nondefault_index(self):
        """Regression: Visual.get_value() with row_index=-1 and 1-based index."""
        report, row = self._make_visual_report(index=[1, 2, 3])
        vis = row.add_kpi(dataset_id="data", value_column="value", row_index=-1, title="T")
        self.assertEqual(vis.get_value(), 30)

    def test_visual_get_value_minus_one_gap_index(self):
        """Regression: Visual.get_value() with row_index=-1 and gap index."""
        report, row = self._make_visual_report(index=[0, 5, 10])
        vis = row.add_kpi(dataset_id="data", value_column="value", row_index=-1, title="T")
        self.assertEqual(vis.get_value(), 30)

    def test_visual_get_value_positive_index(self):
        report, row = self._make_visual_report(index=[1, 2, 3])
        vis = row.add_kpi(dataset_id="data", value_column="value", row_index=0, title="T")
        self.assertEqual(vis.get_value(), 10)


if __name__ == "__main__":
    unittest.main()
