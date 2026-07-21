"""Pie / Donut (type: "pie") — categorical share of a total. Set inner_radius
for a donut."""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import DL2Report, Pie

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

out_file = OUT / "06_pie.html"
report.save(str(out_file))
print(f"wrote {out_file}")
