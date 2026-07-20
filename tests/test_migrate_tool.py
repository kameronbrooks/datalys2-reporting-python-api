"""
Tests for dl2_reports.migrate — source-to-source transforms only.
Skipped entirely when libcst is not installed.
"""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import libcst  # noqa: F401
    HAS_LIBCST = True
except ImportError:
    HAS_LIBCST = False

if HAS_LIBCST:
    from dl2_reports.migrate import transform_notebook, transform_source


@unittest.skipUnless(HAS_LIBCST, "libcst not installed")
class TestHelperCallTransform(unittest.TestCase):
    def test_simple_helper(self):
        src = (
            "from dl2_reports import DL2Report\n"
            "row.add_kpi(\"sales\", value_column=\"Revenue\", format=\"currency\")\n"
        )
        out, changed = transform_source(src)
        self.assertTrue(changed)
        self.assertIn('row.add(KPI("sales", value_column="Revenue", format="currency"))', out)

    def test_chained_add_row(self):
        src = "page.add_row().add_table(\"sales\", page_size=5)\n"
        out, _ = transform_source(src)
        self.assertIn('page.add_row().add(Table("sales", page_size=5))', out)

    def test_chained_add_trend_preserved(self):
        src = "row.add_scatter(\"d\", x_column=\"a\", y_column=\"b\").add_trend(color=\"red\")\n"
        out, _ = transform_source(src)
        self.assertIn('row.add(Scatter("d", x_column="a", y_column="b")).add_trend(color="red")', out)

    def test_on_condition_receiver(self):
        src = "row.on_condition(flag).add_card(title=\"T\", text=\"X\")\n"
        out, _ = transform_source(src)
        self.assertIn('row.on_condition(flag).add(Card(title="T", text="X"))', out)

    def test_multiline_call_stays_multiline(self):
        src = (
            "row.add_table(\n"
            "    \"sales\",  # main dataset\n"
            "    page_size=10,\n"
            ")\n"
        )
        out, _ = transform_source(src)
        compile(out, "<migrated>", "exec")  # still valid Python
        self.assertIn("row.add(", out)
        self.assertIn('Table("sales"', out)
        self.assertIn("# main dataset", out)  # comments survive
        self.assertGreater(out.count("\n"), 3)  # stays multiline

    def test_unknown_methods_untouched(self):
        src = (
            "report.add_modal(\"m\", \"T\")\n"
            "row.add_visual(\"custom\", \"d\", foo=1)\n"
            "report.add_df(\"d\", df)\n"
        )
        out, changed = transform_source(src)
        self.assertFalse(changed)
        self.assertEqual(out, src)

    def test_add_tabs_untouched(self):
        src = "tabs = row.add_tabs(id=\"t\")\ntabs.add_tab(\"A\").add_table(\"d\")\n"
        out, _ = transform_source(src)
        self.assertIn('tabs = row.add_tabs(id="t")', out)
        self.assertIn('tabs.add_tab("A").add(Table("d"))', out)


@unittest.skipUnless(HAS_LIBCST, "libcst not installed")
class TestShapeTransforms(unittest.TestCase):
    def test_threshold_dict(self):
        src = "row.add_line(\"d\", x_column=\"x\", y_columns=[\"y\"], threshold={\"value\": 80, \"mode\": \"above\"})\n"
        out, _ = transform_source(src)
        self.assertIn('threshold=Threshold(value=80, mode="above")', out)
        self.assertIn("from dl2_reports import Line, Threshold", out)

    def test_total_row_keeps_fns_dict(self):
        src = "row.add_table(\"d\", total_row={\"label\": \"T\", \"fns\": {\"unit_price\": \"avg\"}})\n"
        out, _ = transform_source(src)
        self.assertIn('total_row=TotalRow(label="T", fns={"unit_price": "avg"})', out)

    def test_total_column(self):
        src = "row.add_table(\"d\", total_column={\"columns\": [\"a\", \"b\"]})\n"
        out, _ = transform_source(src)
        self.assertIn('total_column=TotalColumn(columns=["a", "b"])', out)

    def test_default_sort_list(self):
        src = "row.add_table(\"d\", default_sort=[{\"column\": \"Amount\", \"direction\": \"desc\"}])\n"
        out, _ = transform_source(src)
        self.assertIn('default_sort=[SortSpec(column="Amount", direction="desc")]', out)

    def test_gauge_ranges(self):
        src = "row.add_gauge(\"d\", value_column=\"v\", ranges=[{\"from\": 0, \"to\": 50, \"color\": \"red\"}])\n"
        out, _ = transform_source(src)
        # "from" is a Python keyword — this dict cannot become kwargs and must stay a dict
        self.assertIn('ranges=[{"from": 0, "to": 50, "color": "red"}]', out)

    def test_non_literal_dict_untouched(self):
        src = "row.add_line(\"d\", x_column=\"x\", y_columns=[\"y\"], threshold=my_threshold)\n"
        out, _ = transform_source(src)
        self.assertIn("threshold=my_threshold", out)

    def test_dict_with_variable_key_untouched(self):
        src = "row.add_line(\"d\", x_column=\"x\", y_columns=[\"y\"], threshold={key: 1})\n"
        out, _ = transform_source(src)
        self.assertIn("threshold={key: 1}", out)

    def test_total_row_true_untouched(self):
        src = "row.add_table(\"d\", total_row=True)\n"
        out, _ = transform_source(src)
        self.assertIn("total_row=True", out)


@unittest.skipUnless(HAS_LIBCST, "libcst not installed")
class TestImportManagement(unittest.TestCase):
    def test_extends_existing_import(self):
        src = (
            "from dl2_reports import DL2Report\n"
            "row.add_kpi(\"d\", value_column=\"v\")\n"
        )
        out, _ = transform_source(src)
        self.assertIn("from dl2_reports import DL2Report, KPI", out)

    def test_no_duplicate_names(self):
        src = (
            "from dl2_reports import DL2Report, KPI\n"
            "row.add_kpi(\"d\", value_column=\"v\")\n"
        )
        out, _ = transform_source(src)
        self.assertEqual(out.count("KPI"), 2)  # once in import, once in code

    def test_inserts_import_when_missing(self):
        src = (
            "import pandas as pd\n"
            "\n"
            "row.add_table(\"d\")\n"
        )
        out, _ = transform_source(src)
        lines = out.splitlines()
        self.assertEqual(lines[0], "import pandas as pd")
        self.assertEqual(lines[1], "from dl2_reports import Table")

    def test_multiple_classes_sorted(self):
        src = (
            "from dl2_reports import DL2Report\n"
            "row.add_table(\"d\")\n"
            "row.add_kpi(\"d\", value_column=\"v\")\n"
        )
        out, _ = transform_source(src)
        self.assertIn("from dl2_reports import DL2Report, KPI, Table", out)

    def test_no_changes_no_import_touch(self):
        src = "from dl2_reports import DL2Report\nreport = DL2Report(\"T\")\n"
        out, changed = transform_source(src)
        self.assertFalse(changed)
        self.assertEqual(out, src)


@unittest.skipUnless(HAS_LIBCST, "libcst not installed")
class TestNotebookTransform(unittest.TestCase):
    def _nb(self, *cell_sources, cell_type="code"):
        return json.dumps({
            "cells": [
                {"cell_type": cell_type, "metadata": {}, "outputs": [], "execution_count": None,
                 "source": s.splitlines(keepends=True)}
                for s in cell_sources
            ],
            "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
        })

    def test_code_cell_transformed(self):
        raw = self._nb("from dl2_reports import DL2Report\nrow.add_kpi(\"d\", value_column=\"v\")\n")
        out, changed, warnings = transform_notebook(raw)
        self.assertTrue(changed)
        self.assertEqual(warnings, [])
        nb = json.loads(out)
        joined = "".join(nb["cells"][0]["source"])
        self.assertIn('row.add(KPI("d", value_column="v"))', joined)

    def test_magic_cell_skipped_with_warning(self):
        raw = self._nb("%load_ext autoreload\nrow.add_kpi(\"d\", value_column=\"v\")\n")
        out, changed, warnings = transform_notebook(raw)
        self.assertFalse(changed)
        self.assertEqual(len(warnings), 1)

    def test_markdown_cell_untouched(self):
        raw = self._nb("row.add_kpi is documented here", cell_type="markdown")
        out, changed, _ = transform_notebook(raw)
        self.assertFalse(changed)
        self.assertEqual(out, raw)


if __name__ == "__main__":
    unittest.main()
