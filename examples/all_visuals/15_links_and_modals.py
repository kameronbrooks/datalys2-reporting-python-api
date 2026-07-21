"""Link (type: "link", dl2 0.4+) and modals.

Links navigate to any visual with an id — switching pages, activating tabs,
scrolling, and flashing the target — or open an external URL.

Modals are overlay views defined once on the report and opened three ways:
  1. modal_id on any visual → hover expand icon
  2. a dedicated ModalButton
  3. a table's row_modal_id → double-click a row (cards see {{ row.Col }})
"""

from pathlib import Path

import pandas as pd

from dl2_reports import KPI, Card, DL2Report, Link, ModalButton, Table

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Links & Modals Showcase",
    description="Navigation links and overlay modals.",
    compress_visuals=False,
)

orders = pd.DataFrame({
    "Region": ["North", "South", "East", "West"],
    "Rep":    ["Ann", "Ben", "Cara", "Dan"],
    "Amount": [310, 95, 420, 640],
})
report.add_df("orders", orders)

# --- Modals are defined on the report, then referenced by id. ----------------
detail = report.add_modal("region-breakdown", "Region Breakdown",
                          description="All orders, by region.")
detail.add_row().add(Table("orders", title="Orders"))

order_modal = report.add_modal("order-detail", "Order Details")
order_modal.add_row().add(Card(
    content_type="md",
    title="Order — {{ row.Region }}",
    text="**Rep:** {{ row.Rep }}\n\n**Amount:** {{ formatCurrency(row.Amount) }}",
))

# --- Page 1: links and modal triggers. ---------------------------------------
page = report.add_page("Overview")

# 1. modal_id on a visual: hover shows an expand icon that opens the modal.
#    The id also makes this KPI a navigation anchor for the return link below.
page.add_row().add(KPI(
    "orders",
    value_column="Amount",
    row_index=-1,
    title="Latest Order",
    format="currency",
    modal_id="region-breakdown",
    id="latest-kpi",
))

# 2. A dedicated modal trigger button.
page.add_row().add(ModalButton("region-breakdown", "View region breakdown"))

# 3. Row modal: double-click a row; the modal's cards read {{ row.* }}.
page.add_row().add(Table("orders", row_modal_id="order-detail",
                         title="Double-click a row"))

# Links: to a visual on another page (switches page + scrolls + flashes),
# and to an external URL (opens a new browser tab).
link_row = page.add_row()
link_row.add(Link(target_id="all-orders", label="Go to the data page",
                  link_style="button"))
link_row.add(Link(href="https://github.com/kameronbrooks/datalys2-reporting",
                  label="dl2 on GitHub"))

# --- Page 2: the link target. ------------------------------------------------
page2 = report.add_page("Data")
page2.add_row().add(Table("orders", id="all-orders", title="All Orders"))
page2.add_row().add(Link(target_id="latest-kpi", label="Back to overview"))

out_file = OUT / "15_links_and_modals.html"
report.save(str(out_file))
print(f"wrote {out_file}")
