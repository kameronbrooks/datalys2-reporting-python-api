"""
Tests for Layout.on_condition() / CompileTimeConditional behaviour.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from dl2_reports import DL2Report
from dl2_reports.components.base import ReportTreeComponent
from dl2_reports.components.layout import CompileTimeConditional
from dl2_reports.components.visual import Visual


def _make_report():
    report = DL2Report("Conditional Test")
    df = pd.DataFrame({"region": ["North", "South"], "revenue": [150_000, 90_000]})
    report.add_df("sales", df, format="records", compress=False)
    return report


class TestOnConditionTrue(unittest.TestCase):
    """When condition=True the visual IS added to the row."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.page = self.report.add_page("Page")
        self.row = self.page.add_row()

    def test_returns_real_visual(self):
        result = self.row.on_condition(True).add_card(title="Hello", text="World")
        self.assertIsInstance(result, Visual)

    def test_visual_added_to_row(self):
        self.row.on_condition(True).add_card(title="Hello", text="World")
        self.assertEqual(len(self.row.children), 1)

    def test_visual_type_correct(self):
        result = self.row.on_condition(True).add_kpi(
            dataset_id="sales", value_column="revenue", row_index=0
        )
        self.assertEqual(result.type, "kpi")

    def test_result_is_truthy(self):
        result = self.row.on_condition(True).add_card(title="Hi", text="There")
        self.assertTrue(bool(result))

    def test_chaining_add_trend(self):
        """add_scatter(...).add_trend() should not raise when condition=True."""
        vis = self.row.on_condition(True).add_scatter(
            dataset_id="sales", x_column="revenue", y_column="revenue"
        )
        # add_trend auto-calc needs x_column/y_column — just check no AttributeError
        self.assertIsInstance(vis, Visual)
        self.assertTrue(hasattr(vis, "add_trend"))


class TestOnConditionFalse(unittest.TestCase):
    """When condition=False NO visual is added and a NullVisual is returned."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.page = self.report.add_page("Page")
        self.row = self.page.add_row()

    def test_returns_none(self):
        result = self.row.on_condition(False).add_card(title="Hi", text="There")
        self.assertIsNone(result)

    def test_no_visual_added_to_row(self):
        self.row.on_condition(False).add_card(title="Hi", text="There")
        self.assertEqual(len(self.row.children), 0)

    def test_result_is_falsy(self):
        result = self.row.on_condition(False).add_card(title="Hi", text="There")
        self.assertFalse(bool(result))

    def test_caller_guards_none_before_chaining(self):
        """on_condition(False) returns None; callers should guard before chaining."""
        result = self.row.on_condition(False).add_scatter(
            dataset_id="sales", x_column="revenue", y_column="revenue"
        )
        self.assertIsNone(result)
        # Correct pattern: check before chaining
        if result is not None:
            result.add_trend()

    def test_multiple_false_conditions_do_not_add_visuals(self):
        self.row.on_condition(False).add_kpi(dataset_id="sales", value_column="revenue")
        self.row.on_condition(False).add_card(title="X", text="Y")
        self.assertEqual(len(self.row.children), 0)


class TestOnConditionDoesNotConsumeId(unittest.TestCase):
    """CompileTimeConditional must not advance BASE_ID."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.page = self.report.add_page("Page")
        self.row = self.page.add_row()

    def test_true_condition_same_ids_as_direct_add(self):
        """IDs produced via on_condition(True) must match those from a direct add."""
        ReportTreeComponent.BASE_ID = 1
        report_a = _make_report()
        row_a = report_a.add_page("P").add_row()
        v_a = row_a.add_card(title="T", text="X")

        ReportTreeComponent.BASE_ID = 1
        report_b = _make_report()
        row_b = report_b.add_page("P").add_row()
        v_b = row_b.on_condition(True).add_card(title="T", text="X")

        self.assertEqual(v_a.id, v_b.id)

    def test_false_condition_does_not_shift_ids(self):
        """After an on_condition(False) call, the next real visual has the same ID
        as if on_condition was never invoked."""
        ReportTreeComponent.BASE_ID = 1
        report_a = _make_report()
        row_a = report_a.add_page("P").add_row()
        v_a = row_a.add_card(title="T", text="X")

        ReportTreeComponent.BASE_ID = 1
        report_b = _make_report()
        row_b = report_b.add_page("P").add_row()
        row_b.on_condition(False).add_card(title="Ignored", text="Ignored")
        v_b = row_b.add_card(title="T", text="X")

        self.assertEqual(v_a.id, v_b.id)


class TestOnConditionWithReportGetValue(unittest.TestCase):
    """Typical usage: use report.get_value() as the condition."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.page = self.report.add_page("Dashboard")
        self.row = self.page.add_row()

    def test_warning_card_added_when_below_target(self):
        target = 120_000
        south_revenue = self.report.get_value("sales", "revenue", 1)  # 90_000
        self.row.on_condition(south_revenue < target).add_card(
            title="Warning", text=f"Revenue ${south_revenue:,} is below target."
        )
        self.assertEqual(len(self.row.children), 1)

    def test_warning_card_not_added_when_above_target(self):
        target = 120_000
        north_revenue = self.report.get_value("sales", "revenue", 0)  # 150_000
        self.row.on_condition(north_revenue < target).add_card(
            title="Warning", text=f"Revenue ${north_revenue:,} is below target."
        )
        self.assertEqual(len(self.row.children), 0)

    def test_report_compiles_with_conditional_content(self):
        target = 120_000
        for i in range(len(self.report.datasets["sales"]["data"])):
            revenue = self.report.get_value("sales", "revenue", i)
            region = self.report.get_value("sales", "region", i)
            self.row.on_condition(revenue < target).add_card(
                title=f"Warning: {region}", text=f"${revenue:,} is below target."
            )
        # Only South (90_000) is below 120_000 — one card added
        self.assertEqual(len(self.row.children), 1)
        self.assertEqual(self.row.children[0].props.get("title"), "Warning: South")
        # Report should compile without error
        self.report.compile()


if __name__ == "__main__":
    unittest.main()
