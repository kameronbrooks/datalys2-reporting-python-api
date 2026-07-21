"""Histogram (type: "histogram") — the distribution of one numeric column,
binned client-side."""

from pathlib import Path

import numpy as np
import pandas as pd

from dl2_reports import DL2Report, Histogram

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Histogram Showcase",
    description="Binned distributions.",
    compress_visuals=False,
)

rng = np.random.default_rng(7)
times = pd.DataFrame({"ResponseMs": rng.lognormal(5.3, 0.35, 400).round(0)})
report.add_df("times", times)

page = report.add_page("Histogram")

page.add_row().add(Histogram(
    "times",
    column="ResponseMs",
    bins=15,
    show_labels=True,
    color="#6366f1",
    x_axis_label="Response time (ms)",
    y_axis_label="Requests",
))

# Fewer bins, default color.
page.add_row().add(Histogram("times", column="ResponseMs", bins=6))

out_file = OUT / "11_histogram.html"
report.save(str(out_file))
print(f"wrote {out_file}")
