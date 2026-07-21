"""Line chart (type: "line") — series over a category or time axis, with
optional smoothing, threshold coloring, and annotation elements (reference
lines, markers, labels, trend lines)."""

from pathlib import Path

import pandas as pd

from dl2_reports import DL2Report, Line, Threshold

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Line Showcase",
    description="Multi-series lines, thresholds, and annotations.",
    compress_visuals=False,
)

traffic = pd.DataFrame({
    "Month":   ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Web":     [3200, 3600, 3400, 4100, 4600, 5200],
    "Mobile":  [2100, 2500, 3100, 3300, 3900, 4700],
    "Partner": [900, 850, 1100, 1000, 1250, 1400],
})
report.add_df("traffic", traffic)

page = report.add_page("Lines")

# Multi-series with legend and custom colors.
page.add_row().add(Line(
    "traffic",
    x_column="Month",
    y_columns=["Web", "Mobile", "Partner"],
    smooth=True,
    show_legend=True,
    colors=["#2563eb", "#16a34a", "#f59e0b"],
    y_axis_label="Sessions",
))

# Threshold: color the line green/red around a target, with a reference line.
page.add_row().add(Line(
    "traffic",
    x_column="Month",
    y_columns=["Web"],
    threshold=Threshold(value=4000, mode="above", show_line=True, blend_width=8),
    y_axis_label="Web sessions",
))

# Annotations: reference lines, a marker, and an explicit-coefficient trend.
annotated = page.add_row().add(Line(
    "traffic",
    x_column="Month",
    y_columns=["Mobile"],
    show_labels=True,
))
annotated.add_element("yAxis", value=3000, label="Target", color="green", line_style="dashed")
annotated.add_element("xAxis", value="Apr", label="Campaign launch", color="#888")
annotated.add_element("marker", value=3900, size=8, shape="triangle", color="red")
# On categorical X axes trend coefficients use the 0-based category index:
# y = 2100 + 500 * index.
annotated.add_trend(coefficients=[2100, 500], color="#9333ea", line_style="dotted")

out_file = OUT / "08_line.html"
report.save(str(out_file))
print(f"wrote {out_file}")
