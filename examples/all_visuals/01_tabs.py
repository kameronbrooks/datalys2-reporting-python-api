"""Tabs (type: "tabs", dl2 0.3+) — a container visual that shows one child view
at a time behind a tab strip.

Shows both ways to build tabs:
  1. Incrementally with row.add_tabs() / tabs.add_tab() — each tab is a full
     Layout, so every add_* helper (or .add(Component)) works inside it.
  2. Declaratively with the typed Tabs/Tab shapes (v2 style).

Also demonstrates nested tab groups, default_tab, active-tab persistence (give
the group an id), and a Link that navigates into a tab.

Note: tabs need the dl2 viewer build that includes the Tabs component (added to
the published bundle on 2026-07-20). If tabs show an "unknown visual" error,
hard-refresh (Ctrl+F5) so the browser drops its cached copy of the CDN bundle.
"""

from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import DL2Report, Card, Line, Pie, Tab, Table, Tabs

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Tabs Showcase",
    description="Every way to build tab groups with the Python API.",
    author="dl2 examples",
    report_id="example-tabs",       # stable id so persisted tab state survives title changes
    compress_visuals=False,         # readable HTML for learning; keep the default (True) in production
)

sales = pd.DataFrame({
    "Month":   ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Revenue": [4200, 4800, 5100, 4700, 5600, 6100],
    "Units":   [42, 45, 51, 44, 55, 60],
})
share = pd.DataFrame({
    "Segment": ["Enterprise", "SMB", "Consumer"],
    "Revenue": [14200, 9800, 6500],
})
report.add_df("sales", sales)
report.add_df("share", share)

page = report.add_page("Tabs", description="Tab groups in every flavor.")

# --- 1. Incremental style: add_tabs() returns a Tabs container; add_tab()
#        returns the tab's content Layout. ------------------------------------
row = page.add_row()
tabs = row.add_tabs(id="sales-views", title="Sales Views", default_tab=0)

tabs.add_tab("Chart").add(
    Line("sales", x_column="Month", y_columns=["Revenue"], smooth=True,
         y_axis_label="Revenue ($)")
)
# Tab content is a Layout — pass layout kwargs like direction/gap.
data_tab = tabs.add_tab("Data", direction="column", gap=8)
data_tab.add(Card(title="Raw numbers", text="The same dataset the chart uses."))
data_tab.add(Table("sales", id="sales-table", page_size=6))

# --- 2. Declarative style: typed Tabs/Tab shapes, all at once. ---------------
row2 = page.add_row()
row2.add(Tabs(id="breakdown", title="Breakdown", tabs=[
    Tab("By Segment", children=[
        Pie("share", category_column="Segment", value_column="Revenue",
            inner_radius=60, show_legend=True),
    ]),
    Tab("Notes", children=[
        Card(title="About this view",
             text="Tabs built declaratively with `Tabs(tabs=[Tab(...), ...])`."),
    ]),
]))

# --- 3. Nested tabs: a tab's layout can contain another tab group. -----------
row3 = page.add_row()
outer = row3.add_tabs(id="outer-tabs", title="Nested Tabs")
outer.add_tab("Overview").add(Card(
    title="Outer tab",
    text="The second tab of this group contains a nested tab group.",
))
inner = outer.add_tab("Details").add_tabs(id="inner-tabs")
inner.add_tab("Units").add(Line("sales", x_column="Month", y_columns=["Units"]))
inner.add_tab("Revenue").add(Line("sales", x_column="Month", y_columns=["Revenue"]))

# --- 4. Links navigate into tabs: targeting a visual inside a tab activates
#        that tab (nested groups included) and scrolls to it. -----------------
link_row = page.add_row()
link_row.add_link(target_id="sales-table", label="Jump to the data table",
                  link_style="button")

out_file = OUT / "01_tabs.html"
report.save(str(out_file))
print(f"wrote {out_file}")
