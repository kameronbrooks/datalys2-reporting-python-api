"""
Tests for pandas-style datasource formulas (dl2_reports.formulas) — parser unit
tests plus integration through visuals and derived datasets.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dl2_reports import DatasourceSpec, parse_datasource, filters as F


class TestParseDatasourcePassthrough(unittest.TestCase):
    def test_plain_identifier(self):
        self.assertEqual(parse_datasource("sales"), DatasourceSpec("sales", None, None))

    def test_camel_case_identifier(self):
        self.assertEqual(parse_datasource("salesData"), DatasourceSpec("salesData", None, None))

    def test_none(self):
        self.assertEqual(parse_datasource(None), DatasourceSpec(None, None, None))

    def test_non_string(self):
        self.assertEqual(parse_datasource(5), DatasourceSpec(5, None, None))

    def test_legacy_dashed_id_untouched(self):
        self.assertEqual(parse_datasource("my-data"), DatasourceSpec("my-data", None, None))

    def test_legacy_spaced_id_untouched(self):
        self.assertEqual(parse_datasource("sales data"), DatasourceSpec("sales data", None, None))


class TestParseDatasourceFilters(unittest.TestCase):
    def _filter(self, source):
        spec = parse_datasource(source)
        self.assertEqual(spec.dataset_id, "sales")
        self.assertIsNone(spec.columns)
        F.validate_filter(spec.filter)
        return spec.filter

    def test_all_comparison_ops(self):
        cases = {
            "sales[amount == 5]": {"column": "amount", "op": "eq", "value": 5},
            "sales[amount != 5]": {"column": "amount", "op": "neq", "value": 5},
            "sales[amount > 5]": {"column": "amount", "op": "gt", "value": 5},
            "sales[amount >= 5]": {"column": "amount", "op": "gte", "value": 5},
            "sales[amount < 5]": {"column": "amount", "op": "lt", "value": 5},
            "sales[amount <= 5]": {"column": "amount", "op": "lte", "value": 5},
        }
        for source, expected in cases.items():
            self.assertEqual(self._filter(source), expected, source)

    def test_flipped_operands(self):
        self.assertEqual(self._filter("sales[200 < amount]"), {"column": "amount", "op": "gt", "value": 200})
        self.assertEqual(self._filter("sales[200 >= amount]"), {"column": "amount", "op": "lte", "value": 200})
        self.assertEqual(self._filter("sales['West' == region]"), {"column": "region", "op": "eq", "value": "West"})

    def test_value_types(self):
        self.assertEqual(self._filter("sales[region == 'West']")["value"], "West")
        self.assertEqual(self._filter("sales[ratio > 0.5]")["value"], 0.5)
        self.assertEqual(self._filter("sales[active == True]")["value"], True)
        self.assertEqual(self._filter("sales[delta > -3]")["value"], -3)
        self.assertEqual(self._filter("sales[amount == 0]")["value"], 0)

    def test_none_forms(self):
        null = {"column": "amount", "op": "isNull"}
        not_null = {"column": "amount", "op": "notNull"}
        self.assertEqual(self._filter("sales[amount == None]"), null)
        self.assertEqual(self._filter("sales[amount is None]"), null)
        self.assertEqual(self._filter("sales[None == amount]"), null)
        self.assertEqual(self._filter("sales[amount != None]"), not_null)
        self.assertEqual(self._filter("sales[amount is not None]"), not_null)

    def test_in_and_not_in(self):
        expected = {"column": "region", "op": "in", "values": ["S", "W"]}
        self.assertEqual(self._filter("sales[region in ['S', 'W']]"), expected)
        self.assertEqual(self._filter("sales[region in ('S', 'W')]"), expected)
        self.assertEqual(
            self._filter("sales[region not in ['S', 'W']]"),
            {"column": "region", "op": "nin", "values": ["S", "W"]},
        )

    def test_between_chain(self):
        self.assertEqual(
            self._filter("sales[100 <= amount <= 200]"),
            {"column": "amount", "op": "between", "values": [100, 200]},
        )

    def test_strict_chain_expands_to_and(self):
        self.assertEqual(
            self._filter("sales[100 < amount < 200]"),
            {"and": [
                {"column": "amount", "op": "gt", "value": 100},
                {"column": "amount", "op": "lt", "value": 200},
            ]},
        )

    def test_bool_ops(self):
        f = self._filter("sales[amount > 1 and region == 'W' and active == True]")
        self.assertEqual(len(f["and"]), 3)
        f = self._filter("sales[amount > 1 or region == 'W']")
        self.assertEqual(len(f["or"]), 2)
        f = self._filter("sales[not (amount > 1)]")
        self.assertEqual(f["not"], {"column": "amount", "op": "gt", "value": 1})

    def test_pandas_bitwise_ops(self):
        f = self._filter("sales[(amount > 1) & (region == 'W') & (active == True)]")
        self.assertEqual(len(f["and"]), 3)
        f = self._filter("sales[(amount > 1) | (region == 'W')]")
        self.assertEqual(len(f["or"]), 2)
        f = self._filter("sales[~(amount > 1)]")
        self.assertEqual(f["not"], {"column": "amount", "op": "gt", "value": 1})

    def test_methods(self):
        cases = {
            "sales[region.contains('or')]": {"column": "region", "op": "contains", "value": "or"},
            "sales[region.str.contains('or')]": {"column": "region", "op": "contains", "value": "or"},
            "sales[region.startswith('N')]": {"column": "region", "op": "startsWith", "value": "N"},
            "sales[region.endswith('th')]": {"column": "region", "op": "endsWith", "value": "th"},
            "sales[region.isin(['N', 'S'])]": {"column": "region", "op": "in", "values": ["N", "S"]},
            "sales[amount.between(1, 9)]": {"column": "amount", "op": "between", "values": [1, 9]},
            "sales[amount.isnull()]": {"column": "amount", "op": "isNull"},
            "sales[amount.isna()]": {"column": "amount", "op": "isNull"},
            "sales[amount.notnull()]": {"column": "amount", "op": "notNull"},
            "sales[amount.notna()]": {"column": "amount", "op": "notNull"},
        }
        for source, expected in cases.items():
            self.assertEqual(self._filter(source), expected, source)

    def test_subscript_column_ref_for_non_identifier_names(self):
        self.assertEqual(
            self._filter("sales[sales['Due Date'] > '2024-01-01']"),
            {"column": "Due Date", "op": "gt", "value": "2024-01-01"},
        )

    def test_attribute_column_ref(self):
        self.assertEqual(
            self._filter("sales[sales.amount > 200]"),
            {"column": "amount", "op": "gt", "value": 200},
        )

    def test_chained_subscripts_and_combine(self):
        self.assertEqual(
            self._filter("sales[amount > 1][region == 'W']"),
            {"and": [
                {"column": "amount", "op": "gt", "value": 1},
                {"column": "region", "op": "eq", "value": "W"},
            ]},
        )


class TestParseDatasourceProjection(unittest.TestCase):
    def test_quoted_columns(self):
        spec = parse_datasource("sales[['Region', 'Amount']]")
        self.assertEqual(spec, DatasourceSpec("sales", None, ["Region", "Amount"]))

    def test_bare_name_columns(self):
        spec = parse_datasource("sales[[Region, Amount]]")
        self.assertEqual(spec.columns, ["Region", "Amount"])

    def test_single_column(self):
        self.assertEqual(parse_datasource("sales[['Region']]").columns, ["Region"])

    def test_projection_then_filter(self):
        spec = parse_datasource("sales[['Region', 'Amount']][Amount > 100]")
        self.assertEqual(spec.columns, ["Region", "Amount"])
        self.assertEqual(spec.filter, {"column": "Amount", "op": "gt", "value": 100})

    def test_filter_then_projection(self):
        spec = parse_datasource("sales[Amount > 100][['Region', 'Amount']]")
        self.assertEqual(spec.columns, ["Region", "Amount"])
        self.assertEqual(spec.filter, {"column": "Amount", "op": "gt", "value": 100})

    def test_double_projection_raises(self):
        with self.assertRaises(ValueError):
            parse_datasource("sales[['a']][['b']]")

    def test_single_bracket_string_raises_with_hint(self):
        with self.assertRaises(ValueError) as ctx:
            parse_datasource("sales['Region']")
        self.assertIn("[['Region']]", str(ctx.exception))

    def test_empty_projection_raises(self):
        with self.assertRaises(ValueError):
            parse_datasource("sales[[]]")


class TestParseDatasourceErrors(unittest.TestCase):
    def _raises(self, source, fragment=None):
        with self.assertRaises(ValueError) as ctx:
            parse_datasource(source)
        self.assertIn("Invalid datasource formula", str(ctx.exception))
        if fragment:
            self.assertIn(fragment, str(ctx.exception))

    def test_unterminated(self):
        self._raises("sales[amount >")

    def test_arbitrary_call(self):
        self._raises("sales[foo(amount)]")

    def test_arithmetic(self):
        self._raises("sales[amount + 5 > 10]")

    def test_fstring_value(self):
        self._raises("sales[region == f'{x}']")

    def test_comprehension(self):
        self._raises("sales[[c for c in cols]]")

    def test_column_vs_column(self):
        self._raises("sales[amount > cost]", "column-to-column")

    def test_constant_vs_constant(self):
        self._raises("sales[1 > 2]", "needs a column")

    def test_non_name_root(self):
        self._raises("foo.bar[a > 1]")
        self._raises("sales()[a > 1]")

    def test_wrong_dataset_in_column_subscript(self):
        self._raises("sales[other['x'] > 1]", "dataset name")

    def test_method_kwargs(self):
        self._raises("sales[region.str.contains('W', na=False)]", "keyword")

    def test_in_with_non_container(self):
        self._raises("sales[region in x]")

    def test_integer_subscript(self):
        self._raises("sales[0]")

    def test_bare_name_condition(self):
        self._raises("sales[amount]")

    def test_precedence_trap_raises(self):
        # & binds tighter than comparisons: this parses as amount > (100 & region) == 'W'
        # and must raise rather than silently mis-filter.
        self._raises("sales[amount > 100 & region == 'W']")

    def test_unknown_method(self):
        self._raises("sales[region.matches('W')]", "Valid methods")

    def test_variable_value(self):
        self._raises("sales[amount > threshold_var]", "column-to-column")


class TestVisualFormulaIntegration(unittest.TestCase):
    def setUp(self):
        import pandas as pd
        from dl2_reports import DL2Report
        from dl2_reports.components.base import ReportTreeComponent

        ReportTreeComponent.BASE_ID = 1
        self.report = DL2Report("Formula Test", compress_visuals=False)
        df = pd.DataFrame({
            "region": ["North", "South", "West"],
            "amount": [100, 200, 300],
            "unit_price": [1.5, 2.5, 3.5],
        })
        self.report.add_df("sales", df, format="records", compress=False)
        self.row = self.report.add_page("P").add_row()

    def test_typed_component_formula(self):
        from dl2_reports import Table
        d = self.row.add(Table("sales[amount > 200]")).to_dict()
        self.assertEqual(d["datasetId"], "sales")
        self.assertEqual(d["filter"], {"column": "amount", "op": "gt", "value": 200})

    def test_formula_and_explicit_filter_combine(self):
        from dl2_reports import Table
        d = self.row.add(Table("sales[amount > 200]", filter=F.eq("region", "West"))).to_dict()
        self.assertEqual(d["filter"], {"and": [
            {"column": "amount", "op": "gt", "value": 200},
            {"column": "region", "op": "eq", "value": "West"},
        ]})

    def test_projection_sets_columns(self):
        from dl2_reports import Table
        d = self.row.add(Table("sales[['region', 'amount']]")).to_dict()
        self.assertEqual(d["datasetId"], "sales")
        self.assertEqual(d["columns"], ["region", "amount"])

    def test_projection_with_explicit_columns_raises(self):
        from dl2_reports import Table
        with self.assertRaises(ValueError) as ctx:
            Table("sales[['region']]", columns=["amount"])
        self.assertIn("Ambiguous", str(ctx.exception))

    def test_projection_on_chart_raises(self):
        from dl2_reports import Bar
        with self.assertRaises(ValueError) as ctx:
            Bar("sales[['region']]", x_column="region", y_columns=["amount"])
        self.assertIn("table-like", str(ctx.exception))

    def test_filter_on_chart_allowed(self):
        from dl2_reports import Bar
        d = self.row.add(Bar("sales[amount > 100]", x_column="region", y_columns=["amount"])).to_dict()
        self.assertEqual(d["datasetId"], "sales")
        self.assertEqual(d["filter"], {"column": "amount", "op": "gt", "value": 100})

    def test_projection_on_unknown_custom_type_allowed(self):
        d = self.row.add_visual("customviz", "sales[['region']]").to_dict()
        self.assertEqual(d["columns"], ["region"])

    def test_legacy_helper_formula(self):
        d = self.row.add_table("sales[region == 'West']").to_dict()
        self.assertEqual(d["datasetId"], "sales")
        self.assertEqual(d["filter"], {"column": "region", "op": "eq", "value": "West"})

    def test_generic_add_visual_formula(self):
        d = self.row.add_visual("kpi", "sales[amount > 100]", value_column="amount", row_index=0).to_dict()
        self.assertEqual(d["datasetId"], "sales")
        self.assertEqual(d["filter"], {"column": "amount", "op": "gt", "value": 100})

    def test_checklist_projection(self):
        d = self.row.add_checklist("sales[['region', 'amount']]", status_column="region").to_dict()
        self.assertEqual(d["columns"], ["region", "amount"])

    def test_copy_round_trips(self):
        from dl2_reports import Table
        original = self.row.add(Table("sales[amount > 200]"))
        copy = original.copy()
        self.assertEqual(copy.dataset_id, "sales")
        self.assertEqual(copy.to_dict()["filter"], original.to_dict()["filter"])

    def test_compile_strict_clean_and_resolved(self):
        from dl2_reports import Table
        self.row.add(Table("sales[amount > 200][['region', 'amount']]"))
        html = self.report.compile(strict=True)
        self.assertIn('"datasetId": "sales"', html)
        self.assertNotIn("amount > 200", html)

    def test_plain_id_backward_compat(self):
        from dl2_reports.components.visual import Visual
        v = Visual("table", "sales")
        self.assertEqual(v.dataset_id, "sales")
        self.assertNotIn("filter", v.props)
        self.assertNotIn("columns", v.props)


class TestDerivedDatasetFormulas(unittest.TestCase):
    def setUp(self):
        import pandas as pd
        from dl2_reports import DL2Report
        from dl2_reports.components.base import ReportTreeComponent

        ReportTreeComponent.BASE_ID = 1
        self.report = DL2Report("Derived Formula Test")
        df = pd.DataFrame({"region": ["N", "W"], "amount": [1, 2]})
        self.report.add_df("sales", df, format="records", compress=False)

    def test_formula_source_resolved_and_filter_stored(self):
        self.report.add_derived_dataset("west", "sales[region == 'West']")
        entry = self.report.datasets["west"]
        self.assertEqual(entry["source"], "sales")
        self.assertEqual(entry["filter"], {"column": "region", "op": "eq", "value": "West"})

    def test_formula_and_param_filter_combine(self):
        self.report.add_derived_dataset(
            "big_west", "sales[region == 'West']", filter=F.gt("amount", 1)
        )
        self.assertEqual(self.report.datasets["big_west"]["filter"], {"and": [
            {"column": "region", "op": "eq", "value": "West"},
            {"column": "amount", "op": "gt", "value": 1},
        ]})

    def test_aggregate_passthrough(self):
        from dl2_reports import aggregates as A
        self.report.add_derived_dataset(
            "by_region", "sales[amount > 0]",
            aggregate=A.aggregate("region", A.agg("amount", "sum")),
        )
        entry = self.report.datasets["by_region"]
        self.assertEqual(entry["source"], "sales")
        self.assertIn("aggregate", entry)

    def test_projection_source_raises(self):
        with self.assertRaises(ValueError) as ctx:
            self.report.add_derived_dataset("proj", "sales[['region']]")
        self.assertIn("not supported", str(ctx.exception))

    def test_derived_from_derived_formula(self):
        self.report.add_derived_dataset("west", "sales[region == 'West']")
        self.report.add_derived_dataset("big_west", "west[amount > 1]")
        self.assertEqual(self.report.datasets["big_west"]["source"], "west")
        self.report.add_page("P").add_row().add_table("big_west")
        self.report.compile()  # source chain resolves

    def test_unknown_source_still_caught_at_compile(self):
        self.report.add_derived_dataset("bad", "nope[amount > 1]")
        with self.assertRaises(ValueError) as ctx:
            self.report.compile()
        self.assertIn("unknown source", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
