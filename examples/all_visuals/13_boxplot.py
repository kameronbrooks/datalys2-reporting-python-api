"""Box plot (type: "boxplot") — distribution quartiles. Two modes:

  - Data mode: give data_column (raw values) and the viewer computes the stats,
    with optional category_column grouping and outlier markers.
  - Pre-calculated mode: give min/q1/median/q3/max columns you computed yourself.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from dl2_reports import Boxplot, DL2Report

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Boxplot Showcase",
    description="Raw-data and pre-calculated box plots.",
    compress_visuals=False,
)

rng = np.random.default_rng(11)
depts, scores = [], []
for dept, center in [("Support", 72), ("Sales", 78), ("Engineering", 84)]:
    vals = rng.normal(center, 8, 40).round(1)
    scores.extend(vals)
    depts.extend([dept] * len(vals))
survey = pd.DataFrame({"Department": depts, "Score": scores})
report.add_df("survey", survey)

# Pre-calculated stats (e.g. computed in pandas ahead of time).
stats = pd.DataFrame({
    "Metric": ["Latency p50 batch", "Latency p50 online"],
    "Min":    [110, 45],
    "Q1":     [180, 62],
    "Median": [240, 75],
    "Q3":     [310, 96],
    "Max":    [520, 160],
    "Mean":   [252.4, 82.1],
})
report.add_df("latency", stats)

page = report.add_page("Boxplots")

# Data mode: grouped by category, horizontal, colored by a D3 scheme.
page.add_row().add(Boxplot(
    "survey",
    data_column="Score",
    category_column="Department",
    direction="horizontal",
    show_outliers=True,
    color="Tableau10",
    x_axis_label="Satisfaction score",
))

# Pre-calculated mode: quartile columns straight from the dataset.
page.add_row().add(Boxplot(
    "latency",
    category_column="Metric",
    min_column="Min",
    q1_column="Q1",
    median_column="Median",
    q3_column="Q3",
    max_column="Max",
    mean_column="Mean",
    y_axis_label="Milliseconds",
))

out_file = OUT / "13_boxplot.html"
report.save(str(out_file))
print(f"wrote {out_file}")
