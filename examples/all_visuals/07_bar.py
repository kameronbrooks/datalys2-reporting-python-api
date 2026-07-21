"""Bar charts — clustered (type: "clusteredBar") and stacked (type: "stackedBar").

The typed Bar component covers both: stacked=False (default) clusters series
side by side, stacked=True stacks them. Clustered bars also support threshold
pass/fail coloring."""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import Bar, DL2Report, Threshold

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Bar Showcase",
    description="Clustered, stacked, and threshold-colored bars.",
    compress_visuals=False,
)

sales = pd.DataFrame({
    "Quarter":     ["Q1", "Q2", "Q3", "Q4"],
    "Electronics": [4200, 4800, 5300, 6100],
    "Clothing":    [3100, 2900, 3600, 4400],
    "Home":        [1900, 2400, 2100, 2800],
})
report.add_df("sales", sales)

page = report.add_page("Bars")

# Clustered: series side by side.
page.add_row().add(Bar(
    "sales",
    x_column="Quarter",
    y_columns=["Electronics", "Clothing", "Home"],
    show_legend=True,
    show_labels=True,
    x_axis_label="Quarter",
    y_axis_label="Revenue ($)",
))

# Stacked: the same series stacked into one bar per category.
page.add_row().add(Bar(
    "sales",
    x_column="Quarter",
    y_columns=["Electronics", "Clothing", "Home"],
    stacked=True,
    show_legend=True,
))

# Threshold coloring (clustered only): each bar is colored by pass/fail.
page.add_row().add(Bar(
    "sales",
    x_column="Quarter",
    y_columns=["Electronics"],
    threshold=Threshold(value=5000, mode="above", show_line=True),
    y_axis_label="Electronics revenue ($)",
))

out_file = OUT / "07_bar.html"
report.save(str(out_file))
print(f"wrote {out_file}")
