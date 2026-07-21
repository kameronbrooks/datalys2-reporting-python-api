"""Heatmap (type: "heatmap") — a matrix of X × Y categories where cell color
encodes a value. Colors accept D3 interpolator names or a custom color list."""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import DL2Report, Heatmap

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Heatmap Showcase",
    description="Category matrices with color scales.",
    compress_visuals=False,
)

rows = []
sales_by_cell = {
    ("North", "Jan"): 42, ("North", "Feb"): 51, ("North", "Mar"): 63, ("North", "Apr"): 58,
    ("South", "Jan"): 35, ("South", "Feb"): 29, ("South", "Mar"): 44, ("South", "Apr"): 50,
    ("East",  "Jan"): 61, ("East",  "Feb"): 66, ("East",  "Mar"): 72, ("East",  "Apr"): 80,
    ("West",  "Jan"): 22, ("West",  "Feb"): 31, ("West",  "Mar"): 27, ("West",  "Apr"): 39,
}
for (region, month), sales in sales_by_cell.items():
    rows.append({"Region": region, "Month": month, "Sales": sales})
report.add_df("matrix", pd.DataFrame(rows))

page = report.add_page("Heatmap")

# D3 interpolator by name.
page.add_row().add(Heatmap(
    "matrix",
    x_column="Month",
    y_column="Region",
    value_column="Sales",
    color="Viridis",
    show_cell_labels=True,
    x_axis_label="Month",
    y_axis_label="Region",
))

# Custom two-color ramp with a pinned scale range.
page.add_row().add(Heatmap(
    "matrix",
    x_column="Month",
    y_column="Region",
    value_column="Sales",
    color=["#fee2e2", "#b91c1c"],
    min_value=0,
    max_value=100,
    show_cell_labels=True,
))

out_file = OUT / "12_heatmap.html"
report.save(str(out_file))
print(f"wrote {out_file}")
