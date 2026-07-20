"""
Tests for the v2 typed component API (VisualComponent base, shapes, component classes).
Grows alongside the V2 migration plan commits.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from dl2_reports import DL2Report
from dl2_reports.components.base import ReportTreeComponent
from dl2_reports.components.component import COMMON_PROPS, VisualComponent, split_legacy_kwargs


class _Widget(VisualComponent):
    """Minimal concrete component for base-class tests."""
    TYPE = "widget"

    def __init__(self, dataset_id=None, value_column=None, rounding=None, extra=None, **common):
        super().__init__(
            dataset_id,
            dict(value_column=value_column, rounding=rounding),
            extra=extra,
            **common,
        )


def _make_report():
    report = DL2Report("Component Test")
    df = pd.DataFrame({"region": ["N", "S"], "amount": [1, 2]})
    report.add_df("sales", df, format="records", compress=False)
    return report


class TestVisualComponentBase(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1

    def test_specific_props_serialized(self):
        w = _Widget("sales", value_column="amount", rounding=2)
        d = w.to_dict()
        self.assertEqual(d["type"], "widget")
        self.assertEqual(d["datasetId"], "sales")
        self.assertEqual(d["valueColumn"], "amount")
        self.assertEqual(d["rounding"], 2)

    def test_none_props_dropped(self):
        d = _Widget("sales", value_column="amount").to_dict()
        self.assertNotIn("rounding", d)

    def test_common_props_accepted(self):
        d = _Widget("sales", value_column="amount", border=True, flex=2, modal_id="m").to_dict()
        self.assertEqual(d["border"], True)
        self.assertEqual(d["flex"], 2)
        self.assertEqual(d["modalId"], "m")

    def test_unknown_prop_raises_with_suggestion(self):
        with self.assertRaises(TypeError) as ctx:
            _Widget("sales", value_column="amount", modalid="m")
        self.assertIn("modalid", str(ctx.exception))
        self.assertIn("modal_id", str(ctx.exception))  # did-you-mean

    def test_extra_passthrough(self):
        d = _Widget("sales", value_column="amount", extra={"future_prop": 1}).to_dict()
        self.assertEqual(d["futureProp"], 1)

    def test_custom_id_adopted(self):
        w = _Widget("sales", value_column="amount", id="my-widget")
        self.assertEqual(w.id, "my-widget")
        self.assertEqual(w.to_dict()["id"], "my-widget")

    def test_is_a_visual(self):
        report = _make_report()
        row = report.add_page("P").add_row()
        w = row.add_component(_Widget, "sales", value_column="amount")
        self.assertIs(w.get_report(), report)
        self.assertIn(w, row.children)

    def test_known_props(self):
        props = _Widget.known_props()
        self.assertIn("value_column", props)
        self.assertIn("rounding", props)
        self.assertTrue(COMMON_PROPS <= props)


class TestSplitLegacyKwargs(unittest.TestCase):
    def test_unknown_kwargs_routed_to_extra(self):
        kwargs = split_legacy_kwargs(_Widget, {"value_column": "a", "custom_thing": 1})
        self.assertEqual(kwargs["value_column"], "a")
        self.assertEqual(kwargs["extra"], {"custom_thing": 1})

    def test_known_kwargs_untouched(self):
        kwargs = split_legacy_kwargs(_Widget, {"value_column": "a", "border": True})
        self.assertNotIn("extra", kwargs)

    def test_merges_with_explicit_extra(self):
        kwargs = split_legacy_kwargs(_Widget, {"extra": {"a": 1}, "custom": 2})
        self.assertEqual(kwargs["extra"], {"a": 1, "custom": 2})


class TestAddComponentConditional(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_condition_true_adds(self):
        w = self.row.on_condition(True).add_component(_Widget, "sales", value_column="amount")
        self.assertIsInstance(w, _Widget)
        self.assertEqual(len(self.row.children), 1)

    def test_condition_false_returns_none_and_consumes_no_id(self):
        result = self.row.on_condition(False).add_component(_Widget, "sales", value_column="amount")
        self.assertIsNone(result)
        self.assertEqual(len(self.row.children), 0)
        w = self.row.add_component(_Widget, "sales", value_column="amount")
        self.assertEqual(w.id, "elem-3")  # report page/row consumed 1-2; no gap from the False branch


if __name__ == "__main__":
    unittest.main()
