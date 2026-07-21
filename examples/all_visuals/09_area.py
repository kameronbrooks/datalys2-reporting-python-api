"""Area chart (type: "area") — a line chart with a filled area. Supports all
line features plus fill opacity, and the same threshold coloring."""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import Area, DL2Report, Threshold

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Area Showcase",
    description="Filled line charts with markers and thresholds.",
    compress_visuals=False,
)

temps = pd.DataFrame({
    "Day":  ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "High": [71, 74, 78, 83, 79, 68, 72],
    "Low":  [55, 58, 61, 66, 63, 52, 54],
})
report.add_df("temps", temps)

page = report.add_page("Areas")

# Two overlapping series with soft fills.
page.add_row().add(Area(
    "temps",
    x_column="Day",
    y_columns=["High", "Low"],
    smooth=True,
    fill_opacity=0.25,
    show_legend=True,
    show_markers=True,
    y_axis_label="°F",
))

# Threshold: values at or below 75 pass (green), above fail (red).
page.add_row().add(Area(
    "temps",
    x_column="Day",
    y_columns=["High"],
    smooth=True,
    fill_opacity=0.4,
    threshold=Threshold(value=75, mode="below", show_line=True, apply_to="both"),
    y_axis_label="High (°F)",
))

# Fill only — hide the stroke and markers.
page.add_row().add(Area(
    "temps",
    x_column="Day",
    y_columns=["Low"],
    show_line=False,
    show_markers=False,
    fill_opacity=0.6,
))

out_file = OUT / "09_area.html"
report.save(str(out_file))
print(f"wrote {out_file}")
