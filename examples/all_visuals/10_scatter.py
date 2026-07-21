"""Scatter plot (type: "scatter") — numeric X/Y points, optional category
coloring, and a built-in regression trendline with correlation stats."""

from pathlib import Path

import numpy as np
import pandas as pd

from dl2_reports import DL2Report, Scatter

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Scatter Showcase",
    description="Point clouds, category coloring, and trendlines.",
    compress_visuals=False,
)

rng = np.random.default_rng(42)
n = 60
hours = rng.uniform(0.5, 8.0, n).round(1)
score = (55 + 5.2 * hours + rng.normal(0, 6, n)).round(1)
group = rng.choice(["Morning", "Evening"], n)
study = pd.DataFrame({"Hours": hours, "Score": score, "Session": group})
report.add_df("study", study)

page = report.add_page("Scatter")

# Built-in linear trendline + correlation stats (r, r², equation).
page.add_row().add(Scatter(
    "study",
    x_column="Hours",
    y_column="Score",
    show_trendline=True,
    show_correlation=True,
    point_size=5,
    x_axis_label="Hours studied",
    y_axis_label="Exam score",
))

# Color points by a category column.
page.add_row().add(Scatter(
    "study",
    x_column="Hours",
    y_column="Score",
    category_column="Session",
    point_size=6,
))

# .add_trend() can auto-fit from the data at build time (scatter has the
# numeric x_column/y_column it needs). Degree 2 fits a polynomial.
fitted = page.add_row().add(Scatter("study", x_column="Hours", y_column="Score"))
fitted.add_trend(color="red", line_style="dashed")          # linear, auto-fit
fitted.add_trend(coefficients=2, color="blue")              # quadratic, auto-fit

out_file = OUT / "10_scatter.html"
report.save(str(out_file))
print(f"wrote {out_file}")
