"""Pie / Donut (type: "pie") — categorical share of a total. Set inner_radius
for a donut.

Also shows aggregate= (dl2 0.3+): a pie over a RAW dataset, grouped and
summed client-side in the browser — no pre-grouped dataset needed."""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import DL2Report, Pie, aggregates as A

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Pie Showcase",
    description="Pie and donut charts.",
    compress_visuals=False,
)

share = pd.DataFrame({
    "Browser": ["Chrome", "Safari", "Edge", "Firefox", "Other"],
    "Users":   [6120, 2480, 980, 640, 380],
})
report.add_df("share", share)

page = report.add_page("Pie")
row = page.add_row()

row.add(Pie(
    "share",
    category_column="Browser",
    value_column="Users",
    show_legend=True,
))

# Donut: same chart with an inner radius.
row.add(Pie(
    "share",
    category_column="Browser",
    value_column="Users",
    inner_radius=70,
    show_legend=True,
))

# --- Pies over a RAW dataset (no pre-grouping) -------------------------------
# Any visual accepts aggregate= (dl2 0.3+): the browser groups and aggregates
# its own view of the dataset, so one raw dataset can feed many visuals.
orders = pd.DataFrame({
    "Region": ["North", "South", "North", "West", "East", "West", "South", "West"],
    "Amount": [120, 80, 200, 150, 90, 210, 60, 75],
})
report.add_df("orders", orders)

row2 = page.add_row()

# Sum Amount per Region. category_column is the groupBy column; value_column is
# the aggregate's OUTPUT column — named by as_, or "{fn}_{column}" by default
# (this one would be "sum_Amount" without as_="Total").
row2.add(Pie(
    "orders",
    category_column="Region",
    value_column="Total",
    aggregate=A.aggregate("Region", A.agg("Amount", "sum", as_="Total")),
    show_legend=True,
))

# Slice size = number of rows per group ("count" ignores its column argument).
row2.add(Pie(
    "orders",
    category_column="Region",
    value_column="Orders",
    aggregate=A.aggregate("Region", A.agg("Region", "count", as_="Orders")),
    inner_radius=70,
    show_legend=True,
))

# Filter + aggregate compose: the filter runs first, then the grouping.
# (A formula datasource works too: Pie("orders[Amount >= 100]", ...).)
row2.add(Pie(
    "orders",
    category_column="Region",
    value_column="Total",
    filter={"column": "Amount", "op": "gte", "value": 100},
    aggregate=A.aggregate("Region", A.agg("Amount", "sum", as_="Total")),
    show_legend=True,
))

out_file = OUT / "06_pie.html"
report.save(str(out_file))
print(f"wrote {out_file}")
