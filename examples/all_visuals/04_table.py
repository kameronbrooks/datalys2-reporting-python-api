"""Table (type: "table") — sortable, filterable, groupable data table with
export, totals, per-column formatting, conditional highlighting, and row
detail modals."""

from pathlib import Path

import pandas as pd

from dl2_reports import (
    AggregateColumn,
    ColumnFormat,
    ConditionalFormat,
    DL2Report,
    SortSpec,
    Table,
    TotalRow,
    filters as F,
)

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Table Showcase",
    description="Grouping, totals, formatting, and row modals.",
    compress_visuals=False,
)

orders = pd.DataFrame({
    "Region":  ["North", "South", "East", "West", "North", "South", "East", "West"],
    "Rep":     ["Ann", "Ben", "Cara", "Dan", "Elle", "Finn", "Gia", "Hank"],
    "Units":   [12, 7, 15, 22, 9, 14, 5, 18],
    "Amount":  [310, 95, 420, 640, 180, 260, 75, 505],
    "Growth":  [0.12, -0.04, 0.31, 0.18, 0.02, 0.09, -0.11, 0.25],
    "Closed":  ["2026-06-02", "2026-06-05", "2026-06-11", "2026-06-14",
                "2026-06-18", "2026-06-21", "2026-06-25", "2026-06-30"],
})
report.add_df("orders", orders)

page = report.add_page("Tables")

# The kitchen sink: grouping with per-group aggregates, a grand-total row,
# column formats, conditional highlighting, initial sort, and a row modal.
page.add_row().add(Table(
    "orders",
    id="orders-table",                       # stable id → view state persists in the browser
    title="Orders by Region",
    page_size=10,
    table_style="alternating",
    group_by="Region",
    group_aggregates=[
        AggregateColumn("Amount", "sum", as_="Total"),
        AggregateColumn("Units", "sum"),     # output name defaults to "sum_Units"
    ],
    default_sort=[SortSpec("Amount", "desc")],
    total_row=TotalRow(label="All regions", fns={"Units": "sum", "Amount": "sum"}),
    column_formats={
        "Amount": ColumnFormat("currency", digits=0),
        "Growth": ColumnFormat("percent", digits=1),   # raw values are ratios (0.12 → 12.0%)
        "Closed": "date",                              # shorthand kind string
    },
    conditional_formats=[
        ConditionalFormat(when=F.gte("Amount", 400), style="success"),
        ConditionalFormat(when=F.lt("Growth", 0), columns=["Growth"], style="error"),
    ],
    row_modal=True,                          # double-click a row for a detail modal
    max_height=420,
    export_file_name="orders.csv",
))

# A minimal read-only table: opt out of the interactive extras.
page.add_row().add(Table(
    "orders",
    title="Static view",
    columns=["Region", "Rep", "Amount"],
    sortable=False,
    show_search=False,
    enable_export=False,
    allow_column_hiding=False,
    context_menu=False,
    page_size=4,
))

# Formula datasource (0.7.0+): filter + project columns pandas-style.
page.add_row().add(Table(
    "orders[Amount > 250][['Region', 'Rep', 'Amount']]",
    title="Big orders (formula datasource)",
))

out_file = OUT / "04_table.html"
report.save(str(out_file))
print(f"wrote {out_file}")
