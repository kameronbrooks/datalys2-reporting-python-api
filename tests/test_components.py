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


class TestAddAndAddRow(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.page = self.report.add_page("P")

    def test_add_returns_child(self):
        row = self.page.add_row()
        w = _Widget("sales", value_column="amount")
        self.assertIs(row.add(w), w)
        self.assertIs(w.parent, row)

    def test_add_rejects_non_component(self):
        row = self.page.add_row()
        with self.assertRaises(TypeError):
            row.add({"type": "kpi"})

    def test_add_row_accepts_components(self):
        w1 = _Widget("sales", value_column="amount")
        w2 = _Widget("sales", value_column="region")
        row = self.page.add_row(w1, w2, gap=16)
        self.assertEqual(row.children, [w1, w2])
        self.assertEqual(row.to_dict()["gap"], 16)

    def test_add_row_legacy_direction_positional(self):
        row = self.page.add_row("column")
        self.assertEqual(row.direction, "column")

    def test_add_row_direction_keyword_with_children(self):
        w = _Widget("sales", value_column="amount")
        row = self.page.add_row(w, direction="grid")
        self.assertEqual(row.direction, "grid")
        self.assertEqual(row.children, [w])

    def test_modal_add_row_accepts_components(self):
        modal = self.report.add_modal("m", "T")
        w = _Widget("sales", value_column="amount")
        row = modal.add_row(w)
        self.assertEqual(row.children, [w])

    def test_conditional_add(self):
        row = self.page.add_row()
        self.assertIsNone(row.on_condition(False).add(_Widget("sales", value_column="amount")))
        w = _Widget("sales", value_column="amount")
        self.assertIs(row.on_condition(True).add(w), w)
        self.assertEqual(row.children, [w])


class TestShapes(unittest.TestCase):
    def test_threshold_serialization(self):
        from dl2_reports import Threshold
        d = Threshold(value=80, mode="above", pass_color="#0f0", blend_width=8).to_dict()
        self.assertEqual(d, {"value": 80, "mode": "above", "passColor": "#0f0", "blendWidth": 8})

    def test_threshold_invalid_mode(self):
        from dl2_reports import Threshold
        with self.assertRaises(ValueError):
            Threshold(value=80, mode="over")

    def test_sort_spec(self):
        from dl2_reports import SortSpec
        self.assertEqual(SortSpec("Amount", "desc").to_dict(), {"column": "Amount", "direction": "desc"})
        with self.assertRaises(ValueError):
            SortSpec("Amount", "descending")

    def test_total_row_fns_keys_raw(self):
        from dl2_reports import TotalRow
        from dl2_reports.serialization import RawDict
        d = TotalRow(label="T", fns={"unit_price": "avg"}).to_dict()
        self.assertIsInstance(d["fns"], RawDict)
        self.assertEqual(dict(d["fns"]), {"unit_price": "avg"})
        with self.assertRaises(ValueError):
            TotalRow(fns={"a": "median"})

    def test_total_column(self):
        from dl2_reports import TotalColumn
        self.assertEqual(TotalColumn(columns=["a"]).to_dict(), {"columns": ["a"]})

    def test_gauge_range_from_keyword(self):
        from dl2_reports import GaugeRange
        d = GaugeRange(from_=0, to=50, color="red", show_plus=True).to_dict()
        self.assertEqual(d, {"from": 0, "to": 50, "color": "red", "showPlus": True})

    def test_aggregate_column_as_keyword(self):
        from dl2_reports import AggregateColumn
        self.assertEqual(
            AggregateColumn("Amount", "sum", as_="Total").to_dict(),
            {"column": "Amount", "fn": "sum", "as": "Total"},
        )
        with self.assertRaises(ValueError):
            AggregateColumn("Amount", "median")

    def test_shape_as_visual_prop_serializes(self):
        from dl2_reports import Threshold
        ReportTreeComponent.BASE_ID = 1
        report = _make_report()
        row = report.add_page("P").add_row()
        visual = row.add_line("sales", x_column="region", y_columns=["amount"],
                              threshold=Threshold(value=1.5, mode="below"))
        d = visual.to_dict()
        self.assertEqual(d["threshold"], {"value": 1.5, "mode": "below"})

    def test_total_row_shape_through_add_table(self):
        from dl2_reports import TotalRow
        ReportTreeComponent.BASE_ID = 1
        report = _make_report()
        row = report.add_page("P").add_row()
        visual = row.add_table("sales", total_row=TotalRow(label="T", fns={"unit_price": "sum"}))
        d = visual.to_dict()
        self.assertEqual(d["totalRow"], {"label": "T", "fns": {"unit_price": "sum"}})


class TestKPIAndCard(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_kpi_component_direct(self):
        from dl2_reports import KPI
        kpi = self.row.add(KPI("sales", value_column="amount", format="currency", row_index=0))
        d = kpi.to_dict()
        self.assertEqual(d["type"], "kpi")
        self.assertEqual(d["valueColumn"], "amount")
        self.assertEqual(d["format"], "currency")

    def test_kpi_typo_raises(self):
        from dl2_reports import KPI
        with self.assertRaises(TypeError) as ctx:
            KPI("sales", value_colum="amount")
        self.assertIn("value_column", str(ctx.exception))  # did-you-mean

    def test_kpi_get_value(self):
        from dl2_reports import KPI
        kpi = self.row.add(KPI("sales", value_column="amount", row_index=0))
        self.assertEqual(kpi.get_value(), 1)

    def test_legacy_add_kpi_same_output(self):
        """Legacy helper and direct component construction serialize identically."""
        ReportTreeComponent.BASE_ID = 1
        r1 = _make_report()
        v1 = r1.add_page("P").add_row().add_kpi(
            dataset_id="sales", value_column="amount", title="T", row_index=0, border=True
        )
        ReportTreeComponent.BASE_ID = 1
        from dl2_reports import KPI
        r2 = _make_report()
        v2 = r2.add_page("P").add_row().add(
            KPI("sales", value_column="amount", title="T", row_index=0, border=True)
        )
        self.assertEqual(v1.to_dict(), v2.to_dict())

    def test_legacy_add_kpi_unknown_kwarg_passes_through(self):
        v = self.row.add_kpi(dataset_id="sales", value_column="amount", some_future_prop=1)
        self.assertEqual(v.to_dict()["someFutureProp"], 1)

    def test_card_component(self):
        from dl2_reports import Card
        card = self.row.add(Card(title="Hi", text="There", content_type="md"))
        d = card.to_dict()
        self.assertEqual(d["type"], "card")
        self.assertEqual(d["contentType"], "md")
        self.assertNotIn("datasetId", d)

    def test_legacy_add_card_null_content_type_parity(self):
        v = self.row.add_card(title="Hi", text="There")
        self.assertIn("content_type", v.props)
        self.assertIsNone(v.props["content_type"])

    def test_kpi_chaining_on_condition(self):
        result = self.row.on_condition(False).add_kpi(dataset_id="sales", value_column="amount")
        self.assertIsNone(result)
        self.assertEqual(len(self.row.children), 0)


class TestTableComponent(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_full_surface(self):
        from dl2_reports import SortSpec, Table, TotalColumn, TotalRow
        t = self.row.add(Table(
            "sales",
            id="tbl",
            group_by="region",
            default_sort=[SortSpec("amount", "desc")],
            total_row=TotalRow(fns={"unit_price": "avg"}),
            total_column=TotalColumn(columns=["amount"]),
            row_modal_id="m",
            max_height=300,
            persist_state=False,
        ))
        d = t.to_dict()
        self.assertEqual(d["id"], "tbl")
        self.assertEqual(d["defaultSort"], [{"column": "amount", "direction": "desc"}])
        self.assertEqual(d["totalRow"], {"fns": {"unit_price": "avg"}})
        self.assertEqual(d["totalColumn"], {"columns": ["amount"]})
        self.assertEqual(d["rowModalId"], "m")
        self.assertEqual(d["persistState"], False)

    def test_dict_total_row_fns_protected(self):
        from dl2_reports import Table
        d = Table("sales", total_row={"fns": {"unit_price": "sum"}}).to_dict()
        self.assertEqual(d["totalRow"]["fns"], {"unit_price": "sum"})

    def test_typo_raises(self):
        from dl2_reports import Table
        with self.assertRaises(TypeError) as ctx:
            Table("sales", pagesize=20)
        self.assertIn("page_size", str(ctx.exception))

    def test_legacy_helper_parity(self):
        ReportTreeComponent.BASE_ID = 1
        r1 = _make_report()
        v1 = r1.add_page("P").add_row().add_table(
            "sales", title="T", page_size=5,
            total_row={"label": "Tot", "fns": {"unit_price": "avg"}},
            hidden_columns=["region"], custom_passthrough=1,
        )
        ReportTreeComponent.BASE_ID = 1
        from dl2_reports import Table
        r2 = _make_report()
        v2 = r2.add_page("P").add_row().add(Table(
            "sales", title="T", page_size=5,
            total_row={"label": "Tot", "fns": {"unit_price": "avg"}},
            hidden_columns=["region"], extra={"custom_passthrough": 1},
        ))
        self.assertEqual(v1.to_dict(), v2.to_dict())


class TestChartComponents(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_bar_stacked_type(self):
        from dl2_reports import Bar
        clustered = Bar("sales", x_column="region", y_columns=["amount"])
        stacked = Bar("sales", x_column="region", y_columns=["amount"], stacked=True)
        self.assertEqual(clustered.to_dict()["type"], "clusteredBar")
        self.assertEqual(stacked.to_dict()["type"], "stackedBar")
        self.assertNotIn("stacked", stacked.to_dict())

    def test_line_with_threshold_shape(self):
        from dl2_reports import Line, Threshold
        d = Line("sales", x_column="region", y_columns=["amount"],
                 threshold=Threshold(value=1, mode="above")).to_dict()
        self.assertEqual(d["threshold"], {"value": 1, "mode": "above"})

    def test_scatter_add_trend_chaining(self):
        from dl2_reports import Scatter
        v = self.row.add(Scatter("sales", x_column="amount", y_column="unit_price"))
        v.add_trend(coefficients=[0, 1])
        self.assertEqual(v.to_dict()["otherElements"][0]["visualElementType"], "trend")

    def test_area_legacy_threshold_object(self):
        from dl2_reports.components.visuals.Area import AreaVisual
        v = self.row.add_area("sales", x_column="region", y_columns=["amount"],
                              threshold=AreaVisual.Threshold(value=5))
        self.assertEqual(v.to_dict()["threshold"]["value"], 5)
        self.assertEqual(v.to_dict()["threshold"]["mode"], "above")

    def test_chart_helpers_parity(self):
        from dl2_reports import Pie
        ReportTreeComponent.BASE_ID = 1
        r1 = _make_report()
        v1 = r1.add_page("P").add_row().add_pie("sales", "region", "amount", inner_radius=40)
        ReportTreeComponent.BASE_ID = 1
        r2 = _make_report()
        v2 = r2.add_page("P").add_row().add(Pie("sales", "region", "amount", inner_radius=40))
        self.assertEqual(v1.to_dict(), v2.to_dict())

    def test_chart_typo_raises(self):
        from dl2_reports import Line
        with self.assertRaises(TypeError):
            Line("sales", x_column="region", y_colums=["amount"])


if __name__ == "__main__":
    unittest.main()
