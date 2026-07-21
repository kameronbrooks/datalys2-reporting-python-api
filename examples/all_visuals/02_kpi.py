"""KPI (type: "kpi") — a single headline number with optional comparison value,
formatting, and warning/breach indicators."""

from pathlib import Path

import pandas as pd

from dl2_reports import DL2Report, KPI

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="KPI Showcase",
    description="Headline metrics with comparisons and breach indicators.",
    compress_visuals=False,
)

monthly = pd.DataFrame({
    "Month":        ["Apr", "May", "Jun"],
    "Revenue":      [47000, 56000, 61000],
    "ErrorRate":    [0.031, 0.024, 0.042],
    "AvgHandleSec": [432, 401, 388],
})
report.add_df("monthly", monthly)

page = report.add_page("KPIs")
row = page.add_row()

# Latest revenue vs the previous month (negative row indices count from the end).
row.add(KPI(
    "monthly",
    value_column="Revenue",
    row_index=-1,
    comparison_column="Revenue",
    comparison_row_index=-2,
    comparison_text="vs last month",
    title="Revenue",
    format="currency",
    rounding_precision=0,
    good_direction="higher",
))

# Percent metric where lower is better, with warning/breach thresholds.
row.add(KPI(
    "monthly",
    value_column="ErrorRate",
    row_index=-1,
    comparison_column="ErrorRate",
    comparison_row_index=-2,
    comparison_text="vs last month",
    title="Error Rate",
    format="percent",
    rounding_precision=1,
    good_direction="lower",
    warning_value=0.03,   # >= 3% shows a warning indicator
    breach_value=0.05,    # >= 5% shows a breach indicator
    description="Share of failed requests this month.",
))

# Duration formatting: 'hms' renders seconds as HH:MM:SS.
row.add(KPI(
    "monthly",
    value_column="AvgHandleSec",
    row_index=-1,
    title="Avg Handle Time",
    format="hms",
    good_direction="lower",
))

out_file = OUT / "02_kpi.html"
report.save(str(out_file))
print(f"wrote {out_file}")
