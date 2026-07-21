"""
Tests for dl2 0.3/0.4 feature support: filters, aggregates, derived datasets,
tabs, table UX/totals/row modals, link visual, persistent state, RawDict.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from dl2_reports import DL2Report, RawDict, aggregates as A, filters as F
from dl2_reports.components.base import ReportTreeComponent
from dl2_reports.components.tabs import Tabs
from dl2_reports.components.visual import Visual


def _make_report():
    report = DL2Report("Feature Test")
    df = pd.DataFrame({
        "region": ["North", "South", "West"],
        "amount": [100, 200, 300],
        "unit_price": [1.5, 2.5, 3.5],
    })
    report.add_df("sales", df, format="records", compress=False)
    return report


class TestFilterBuilders(unittest.TestCase):
    def test_leaf_condition(self):
        self.assertEqual(F.eq("region", "West"), {"column": "region", "op": "eq", "value": "West"})

    def test_between_uses_values(self):
        self.assertEqual(
            F.between("amount", 100, 200),
            {"column": "amount", "op": "between", "values": [100, 200]},
        )

    def test_isin(self):
        self.assertEqual(
            F.isin("region", ["North", "South"]),
            {"column": "region", "op": "in", "values": ["North", "South"]},
        )

    def test_null_ops_take_no_value(self):
        self.assertEqual(F.is_null("region"), {"column": "region", "op": "isNull"})
        self.assertEqual(F.not_null("region"), {"column": "region", "op": "notNull"})

    def test_composition(self):
        expr = F.and_(F.eq("region", "West"), F.or_(F.gt("amount", 10), F.not_(F.is_null("amount"))))
        self.assertEqual(sorted(expr), ["and"])
        self.assertEqual(len(expr["and"]), 2)
        self.assertIn("or", expr["and"][1])

    def test_invalid_op_raises(self):
        with self.assertRaises(ValueError):
            F.where("region", "equals", "West")

    def test_missing_value_raises(self):
        with self.assertRaises(ValueError):
            F.where("region", "eq")

    def test_validate_filter_rejects_bad_group(self):
        with self.assertRaises(ValueError):
            F.validate_filter({"and": []})
        with self.assertRaises(ValueError):
            F.validate_filter({"column": "x"})  # missing op

    def test_integer_column_index_allowed(self):
        self.assertEqual(F.eq(0, "West")["column"], 0)


class TestAggregateBuilders(unittest.TestCase):
    def test_agg_shape(self):
        self.assertEqual(A.agg("amount", "sum", as_="total"), {"column": "amount", "fn": "sum", "as": "total"})

    def test_aggregate_spec(self):
        spec = A.aggregate("region", A.agg("amount", "sum"))
        self.assertEqual(spec, {"groupBy": ["region"], "aggregates": [{"column": "amount", "fn": "sum"}]})

    def test_group_by_list(self):
        spec = A.aggregate(["region", "unit_price"], A.agg("amount", "avg"))
        self.assertEqual(spec["groupBy"], ["region", "unit_price"])

    def test_invalid_fn_raises(self):
        with self.assertRaises(ValueError):
            A.agg("amount", "median")

    def test_empty_spec_raises(self):
        with self.assertRaises(ValueError):
            A.aggregate([], A.agg("amount", "sum"))
        with self.assertRaises(ValueError):
            A.aggregate("region")

    def test_validate_accepts_snake_case_group_by(self):
        A.validate_aggregate({"group_by": ["region"], "aggregates": [{"column": "amount", "fn": "sum"}]})


class TestVisualFilterAggregate(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_filter_serialized_on_visual(self):
        visual = self.row.add_table("sales", filter=F.eq("region", "West"))
        d = visual.to_dict()
        self.assertEqual(d["filter"], {"column": "region", "op": "eq", "value": "West"})

    def test_aggregate_serialized_with_camel_group_by(self):
        visual = self.row.add_bar(
            dataset_id="sales", x_column="region", y_columns=["sum_amount"],
            aggregate=A.aggregate("region", A.agg("amount", "sum")),
        )
        d = visual.to_dict()
        self.assertEqual(d["aggregate"]["groupBy"], ["region"])
        self.assertEqual(d["aggregate"]["aggregates"][0]["fn"], "sum")

    def test_snake_case_aggregate_dict_converted(self):
        visual = self.row.add_visual(
            "table", "sales",
            aggregate={"group_by": ["region"], "aggregates": [{"column": "amount", "fn": "sum"}]},
        )
        self.assertEqual(visual.to_dict()["aggregate"]["groupBy"], ["region"])

    def test_invalid_filter_raises_at_build_time(self):
        with self.assertRaises(ValueError):
            self.row.add_table("sales", filter={"column": "region", "op": "equals", "value": "x"})

    def test_invalid_aggregate_raises_at_build_time(self):
        with self.assertRaises(ValueError):
            self.row.add_visual("table", "sales", aggregate={"groupBy": [], "aggregates": []})


class TestDerivedDatasets(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()

    def test_entry_shape(self):
        self.report.add_derived_dataset(
            "west", "sales",
            filter=F.eq("region", "West"),
            aggregate=A.aggregate("region", A.agg("amount", "sum", as_="total")),
        )
        entry = self.report.datasets["west"]
        self.assertEqual(entry["id"], "west")
        self.assertEqual(entry["source"], "sales")
        self.assertEqual(entry["filter"]["op"], "eq")
        self.assertEqual(entry["aggregate"]["groupBy"], ["region"])

    def test_compiles_into_datasets_dict(self):
        self.report.add_derived_dataset("west", "sales", filter=F.eq("region", "West"))
        self.report.add_page("P").add_row().add_table("west")
        self.report.compress_visuals = False
        html = self.report.compile()
        self.assertIn('"source": "sales"', html)

    def test_chained_derived_dataset_any_order(self):
        # Forward reference: derived-of-derived declared before its source exists
        self.report.add_derived_dataset("top_west", "west", filter=F.gt("amount", 10))
        self.report.add_derived_dataset("west", "sales", filter=F.eq("region", "West"))
        self.report.compile()  # should not raise

    def test_unknown_source_raises_at_compile(self):
        self.report.add_derived_dataset("bad", "nope")
        with self.assertRaises(ValueError):
            self.report.compile()

    def test_get_value_on_derived_raises(self):
        self.report.add_derived_dataset("west", "sales", filter=F.eq("region", "West"))
        with self.assertRaises(ValueError) as ctx:
            self.report.get_value("west", "amount")
        self.assertIn("derived", str(ctx.exception))


class TestTabs(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_serialization_shape(self):
        tabs = self.row.add_tabs(id="my-tabs", default_tab=1)
        tabs.add_tab("Chart").add_bar(dataset_id="sales", x_column="region", y_columns=["amount"])
        tabs.add_tab("Data", direction="grid", columns=2).add_table("sales")
        d = tabs.to_dict()
        self.assertEqual(d["type"], "tabs")
        self.assertEqual(d["elementType"], "visual")
        self.assertEqual(d["id"], "my-tabs")
        self.assertEqual(d["defaultTab"], 1)
        self.assertEqual([t["title"] for t in d["tabs"]], ["Chart", "Data"])
        self.assertEqual(d["tabs"][0]["layout"]["type"], "layout")
        self.assertEqual(d["tabs"][1]["layout"]["direction"], "grid")
        self.assertEqual(d["tabs"][1]["layout"]["columns"], 2)

    def test_tabs_are_layout_children(self):
        tabs = self.row.add_tabs()
        self.assertIn(tabs, self.row.children)
        self.assertIsInstance(tabs, Tabs)

    def test_nested_tabs(self):
        outer = self.row.add_tabs()
        inner = outer.add_tab("Outer").add_tabs(id="inner")
        inner.add_tab("Inner").add_card(title="Hi", text="There")
        d = outer.to_dict()
        nested = d["tabs"][0]["layout"]["children"][0]
        self.assertEqual(nested["type"], "tabs")
        self.assertEqual(nested["id"], "inner")

    def test_get_report_through_tabs(self):
        tabs = self.row.add_tabs()
        tab_layout = tabs.add_tab("T")
        visual = tab_layout.add_card(title="X", text="Y")
        self.assertIs(visual.get_report(), self.report)

    def test_persist_state_prop(self):
        tabs = self.row.add_tabs(id="t", persist_state=False)
        self.assertEqual(tabs.to_dict()["persistState"], False)

    def test_on_condition_true(self):
        tabs = self.row.on_condition(True).add_tabs(id="cond-tabs")
        self.assertIsInstance(tabs, Tabs)
        self.assertEqual(len(self.row.children), 1)

    def test_on_condition_false(self):
        result = self.row.on_condition(False).add_tabs(id="cond-tabs")
        self.assertFalse(bool(result))
        self.assertEqual(len(self.row.children), 0)

    def test_on_condition_false_add_layout(self):
        result = self.row.on_condition(False).add_layout("column")
        self.assertFalse(bool(result))
        self.assertEqual(len(self.row.children), 0)


class TestTableFeatures(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_new_props_camel_cased(self):
        visual = self.row.add_table(
            "sales",
            sortable=True,
            default_sort=[{"column": "amount", "direction": "desc"}],
            hidden_columns=["unit_price"],
            allow_column_hiding=False,
            group_by="region",
            group_aggregates=[A.agg("amount", "sum")],
            groups_collapsed=True,
            enable_export=False,
            export_file_name="sales.csv",
            context_menu=False,
            max_height=400,
            sticky_header=True,
        )
        d = visual.to_dict()
        self.assertEqual(d["defaultSort"], [{"column": "amount", "direction": "desc"}])
        self.assertEqual(d["hiddenColumns"], ["unit_price"])
        self.assertEqual(d["allowColumnHiding"], False)
        self.assertEqual(d["groupBy"], "region")
        self.assertEqual(d["groupAggregates"], [{"column": "amount", "fn": "sum"}])
        self.assertEqual(d["groupsCollapsed"], True)
        self.assertEqual(d["enableExport"], False)
        self.assertEqual(d["exportFileName"], "sales.csv")
        self.assertEqual(d["contextMenu"], False)
        self.assertEqual(d["maxHeight"], 400)
        self.assertEqual(d["stickyHeader"], True)

    def test_total_row_bool(self):
        d = self.row.add_table("sales", total_row=True).to_dict()
        self.assertEqual(d["totalRow"], True)

    def test_total_row_fns_column_names_preserved(self):
        """Column names used as fns keys must NOT be camelCased (unit_price stays unit_price)."""
        d = self.row.add_table(
            "sales",
            total_row={"label": "Totals", "fns": {"unit_price": "avg", "amount": "sum"}},
        ).to_dict()
        self.assertEqual(d["totalRow"]["label"], "Totals")
        self.assertEqual(d["totalRow"]["fns"], {"unit_price": "avg", "amount": "sum"})

    def test_total_column(self):
        d = self.row.add_table(
            "sales", total_column={"label": "Sum", "columns": ["amount", "unit_price"]}
        ).to_dict()
        self.assertEqual(d["totalColumn"], {"label": "Sum", "columns": ["amount", "unit_price"]})

    def test_row_modal_props(self):
        d = self.row.add_table(
            "sales",
            row_modal=True,
            row_modal_columns=["region", "amount"],
            row_modal_title="Row Details",
        ).to_dict()
        self.assertEqual(d["rowModal"], True)
        self.assertEqual(d["rowModalColumns"], ["region", "amount"])
        self.assertEqual(d["rowModalTitle"], "Row Details")

    def test_row_modal_id(self):
        d = self.row.add_table("sales", row_modal_id="detail-modal").to_dict()
        self.assertEqual(d["rowModalId"], "detail-modal")

    def test_stable_id_and_persist_state(self):
        visual = self.row.add_table("sales", id="main-table", persist_state=False)
        self.assertEqual(visual.id, "main-table")
        d = visual.to_dict()
        self.assertEqual(d["id"], "main-table")
        self.assertEqual(d["persistState"], False)


class TestLinkVisual(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_target_link(self):
        d = self.row.add_link(target_id="main-table", label="Jump to table").to_dict()
        self.assertEqual(d["type"], "link")
        self.assertEqual(d["targetId"], "main-table")
        self.assertEqual(d["label"], "Jump to table")
        self.assertNotIn("datasetId", d)

    def test_href_link_button_style(self):
        d = self.row.add_link(href="https://example.com", label="Docs", link_style="button").to_dict()
        self.assertEqual(d["href"], "https://example.com")
        self.assertEqual(d["linkStyle"], "button")

    def test_requires_exactly_one_target(self):
        with self.assertRaises(ValueError):
            self.row.add_link()
        with self.assertRaises(ValueError):
            self.row.add_link(target_id="a", href="https://example.com")

    def test_on_condition_forwarding(self):
        result = self.row.on_condition(False).add_link(target_id="x")
        self.assertFalse(bool(result))
        self.assertEqual(len(self.row.children), 0)


class TestRawDict(unittest.TestCase):
    def test_visual_serialization_preserves_raw_keys(self):
        ReportTreeComponent.BASE_ID = 1
        visual = Visual("table", "sales", custom_prop=RawDict({"my_col": {"nested_key": 1}}))
        d = visual.to_dict()
        self.assertIn("my_col", d["customProp"])
        # Values inside a RawDict are still serialized (plain dicts get camelCased)
        self.assertEqual(d["customProp"]["my_col"], {"nestedKey": 1})

    def test_camel_case_dict_preserves_raw_keys(self):
        from dl2_reports.serialization import camel_case_dict
        out = camel_case_dict({"outer_key": RawDict({"my_col": "sum"})})
        self.assertEqual(out, {"outerKey": {"my_col": "sum"}})


class TestReportId(unittest.TestCase):
    def test_ctor_report_id_sets_meta(self):
        ReportTreeComponent.BASE_ID = 1
        report = DL2Report("T", report_id="sales-report-v1")
        self.assertEqual(report.meta_tags["report-id"], "sales-report-v1")
        self.assertIn('<meta name="report-id" content="sales-report-v1">', report.compile())

    def test_set_report_id_chains(self):
        ReportTreeComponent.BASE_ID = 1
        report = DL2Report("T").set_report_id("abc")
        self.assertEqual(report.meta_tags["report-id"], "abc")


class TestChecklistFeatures(unittest.TestCase):
    """dl2 0.4.1: checklist parity with tables + checklist-specific UX props."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = DL2Report("Checklist Test")
        df = pd.DataFrame({
            "task": ["A", "B", "C"],
            "done": [True, False, False],
            "due_date": ["2026-07-01", "2026-07-25", "2026-08-01"],
        })
        self.report.add_df("tasks", df, format="records", compress=False)
        self.row = self.report.add_page("P").add_row()

    def test_parity_props_camel_cased(self):
        visual = self.row.add_checklist(
            "tasks",
            status_column="done",
            sortable=True,
            hidden_columns=["due_date"],
            allow_column_hiding=False,
            enable_export=False,
            export_file_name="tasks.csv",
            context_menu=False,
            max_height=400,
            sticky_header=True,
            row_modal=True,
            row_modal_columns=["task", "due_date"],
            row_modal_title="Task Details",
        )
        d = visual.to_dict()
        self.assertEqual(d["statusColumn"], "done")
        self.assertEqual(d["hiddenColumns"], ["due_date"])
        self.assertEqual(d["allowColumnHiding"], False)
        self.assertEqual(d["enableExport"], False)
        self.assertEqual(d["exportFileName"], "tasks.csv")
        self.assertEqual(d["contextMenu"], False)
        self.assertEqual(d["maxHeight"], 400)
        self.assertEqual(d["stickyHeader"], True)
        self.assertEqual(d["rowModal"], True)
        self.assertEqual(d["rowModalColumns"], ["task", "due_date"])
        self.assertEqual(d["rowModalTitle"], "Task Details")

    def test_checklist_specific_props(self):
        d = self.row.add_checklist(
            "tasks",
            status_column="done",
            show_status_filter=False,
            show_progress=False,
            hide_completed=True,
        ).to_dict()
        self.assertEqual(d["showStatusFilter"], False)
        self.assertEqual(d["showProgress"], False)
        self.assertEqual(d["hideCompleted"], True)

    def test_default_sort_special_status_column(self):
        from dl2_reports import SortSpec
        d = self.row.add_checklist(
            "tasks",
            status_column="done",
            default_sort=[SortSpec("status", "desc"), SortSpec("due_date")],
        ).to_dict()
        self.assertEqual(
            d["defaultSort"],
            [{"column": "status", "direction": "desc"}, {"column": "due_date", "direction": "asc"}],
        )

    def test_row_modal_id(self):
        d = self.row.add_checklist("tasks", status_column="done", row_modal_id="task-detail").to_dict()
        self.assertEqual(d["rowModalId"], "task-detail")

    def test_stable_id_and_persist_state(self):
        visual = self.row.add_checklist(
            "tasks", status_column="done", id="main-checklist", persist_state=False
        )
        self.assertEqual(visual.id, "main-checklist")
        d = visual.to_dict()
        self.assertEqual(d["id"], "main-checklist")
        self.assertEqual(d["persistState"], False)

    def test_typo_kwarg_raises(self):
        from dl2_reports import Checklist
        with self.assertRaises(TypeError):
            Checklist("tasks", status_column="done", show_progres=True)

    def test_new_props_pass_component_lint(self):
        from dl2_reports.lint import lint_report
        self.row.add_checklist(
            "tasks",
            status_column="done",
            hide_completed=True,
            max_height=300,
            column_formats={"due_date": "date"},
        )
        self.assertEqual(lint_report(self.report), [])


class TestColumnFormats(unittest.TestCase):
    """dl2 0.4.1: per-column display formats on tables and checklists."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_column_name_keys_not_camel_cased(self):
        from dl2_reports import ColumnFormat
        d = self.row.add_table(
            "sales",
            column_formats={
                "unit_price": ColumnFormat("currency", digits=0),
                "Due Date": "date",
            },
        ).to_dict()
        self.assertEqual(
            d["columnFormats"],
            {"unit_price": {"format": "currency", "digits": 0}, "Due Date": "date"},
        )

    def test_checklist_column_formats(self):
        d = self.row.add_checklist(
            "sales",
            status_column="region",
            column_formats={"unit_price": {"format": "percent", "digits": 1}},
        ).to_dict()
        self.assertEqual(d["columnFormats"], {"unit_price": {"format": "percent", "digits": 1}})

    def test_prewrapped_rawdict_not_double_wrapped(self):
        from dl2_reports.components.visual_components import _protect_column_formats
        wrapped = RawDict({"unit_price": "currency"})
        self.assertIs(_protect_column_formats(wrapped), wrapped)
        self.assertIsNone(_protect_column_formats(None))

    def test_currency_symbol(self):
        from dl2_reports import ColumnFormat
        d = self.row.add_table(
            "sales", column_formats={"amount": ColumnFormat("currency", symbol="€")}
        ).to_dict()
        self.assertEqual(d["columnFormats"]["amount"], {"format": "currency", "symbol": "€"})

    def test_invalid_format_kind_raises(self):
        from dl2_reports import ColumnFormat
        with self.assertRaises(ValueError):
            ColumnFormat("money")


class TestConditionalFormats(unittest.TestCase):
    """dl2 0.4.1: conditional highlight rules on tables and checklists."""

    def setUp(self):
        ReportTreeComponent.BASE_ID = 1
        self.report = _make_report()
        self.row = self.report.add_page("P").add_row()

    def test_rule_serialized(self):
        from dl2_reports import ConditionalFormat
        d = self.row.add_table(
            "sales",
            conditional_formats=[
                ConditionalFormat(when=F.gt("amount", 200), style="error"),
                ConditionalFormat(when=F.eq("region", "West"), target="row", style="muted"),
            ],
        ).to_dict()
        self.assertEqual(
            d["conditionalFormats"],
            [
                {"when": {"column": "amount", "op": "gt", "value": 200}, "style": "error"},
                {"when": {"column": "region", "op": "eq", "value": "West"}, "target": "row", "style": "muted"},
            ],
        )

    def test_css_keys_camel_cased(self):
        from dl2_reports import ConditionalFormat
        d = self.row.add_table(
            "sales",
            conditional_formats=[
                ConditionalFormat(
                    when=F.gt("amount", 100),
                    css={"background_color": "#fee2e2", "fontWeight": 600},
                )
            ],
        ).to_dict()
        self.assertEqual(
            d["conditionalFormats"][0]["css"],
            {"backgroundColor": "#fee2e2", "fontWeight": 600},
        )

    def test_plain_dict_rules_pass_through(self):
        d = self.row.add_table(
            "sales",
            conditional_formats=[{"when": {"column": "amount", "op": "gt", "value": 1}, "style": "success"}],
        ).to_dict()
        self.assertEqual(d["conditionalFormats"][0]["style"], "success")

    def test_missing_when_raises(self):
        from dl2_reports import ConditionalFormat
        with self.assertRaises(ValueError):
            ConditionalFormat(style="success")

    def test_invalid_when_op_raises(self):
        from dl2_reports import ConditionalFormat
        with self.assertRaises(ValueError):
            ConditionalFormat(when={"column": "amount", "op": "equals", "value": 1}, style="success")

    def test_invalid_target_raises(self):
        from dl2_reports import ConditionalFormat
        with self.assertRaises(ValueError):
            ConditionalFormat(when=F.gt("amount", 1), target="column", style="success")

    def test_invalid_style_raises(self):
        from dl2_reports import ConditionalFormat
        with self.assertRaises(ValueError):
            ConditionalFormat(when=F.gt("amount", 1), style="danger")

    def test_style_or_css_required(self):
        from dl2_reports import ConditionalFormat
        with self.assertRaises(ValueError):
            ConditionalFormat(when=F.gt("amount", 1))

    def test_compound_when_needs_columns_for_cell_target(self):
        from dl2_reports import ConditionalFormat
        compound = F.and_(F.gt("amount", 1), F.eq("region", "West"))
        with self.assertRaises(ValueError):
            ConditionalFormat(when=compound, style="warning")
        # OK with explicit columns or a row target
        ConditionalFormat(when=compound, columns=["amount"], style="warning")
        ConditionalFormat(when=compound, target="row", style="warning")


if __name__ == "__main__":
    unittest.main()
