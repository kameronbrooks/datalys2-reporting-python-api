"""Gauge (type: "gauge") — an animated speedometer for one value, with optional
colored range bands, legend, and number formatting."""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import DL2Report, Gauge, GaugeRange

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Gauge Showcase",
    description="Simple gauges and range-banded gauges.",
    compress_visuals=False,
)

metrics = pd.DataFrame({
    "CSAT":     [83.5],
    "CPULoad":  [0.62],
    "Pipeline": [1_240_000],
})
report.add_df("metrics", metrics)

page = report.add_page("Gauges")
row = page.add_row()

# Simple gauge: min/max scale, unit text.
row.add(Gauge(
    "metrics",
    value_column="CSAT",
    title="Customer Satisfaction",
    min_value=0,
    max_value=100,
    unit="%",
))

# Range bands with a legend; showPlus renders the last band as "90+".
row.add(Gauge(
    "metrics",
    value_column="CSAT",
    title="CSAT vs targets",
    min_value=0,
    max_value=100,
    ranges=[
        GaugeRange(from_=0,  to=50,  color="#ef4444", label="Poor"),
        GaugeRange(from_=50, to=75,  color="#f59e0b", label="Average"),
        GaugeRange(from_=75, to=90,  color="#22c55e", label="Good"),
        GaugeRange(from_=90, to=100, color="#15803d", label="Excellent", show_plus=True),
    ],
    show_legend=True,
    unit="%",
))

# Percent formatting reads a 0–1 ratio; currency works too.
row2 = page.add_row()
row2.add(Gauge(
    "metrics",
    value_column="CPULoad",
    title="CPU Load",
    min_value=0,
    max_value=1,
    format="percent",
    rounding_precision=0,
))
row2.add(Gauge(
    "metrics",
    value_column="Pipeline",
    title="Pipeline Value",
    min_value=0,
    max_value=2_000_000,
    format="currency",
    rounding_precision=0,
))

out_file = OUT / "14_gauge.html"
report.save(str(out_file))
print(f"wrote {out_file}")
