"""Card (type: "card") — a text card. Needs no dataset.

Cards support:
  - plain text or markdown (content_type="md")
  - {{ ... }} template expressions evaluated in the browser, with helpers like
    count(), sum(), avg(), formatCurrency(), formatPercent()

Security note: template expressions execute JavaScript in the viewer's browser —
only embed them in trusted reports.
"""

from pathlib import Path

import pandas as pd

from dl2_reports import DL2Report, Card

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Card Showcase",
    description="Text, markdown, and computed template cards.",
    compress_visuals=False,
)

orders = pd.DataFrame({
    "Region": ["North", "South", "East", "West"],
    "Amount": [1200, 950, 1430, 1810],
})
report.add_df("orders", orders)

page = report.add_page("Cards")

# Plain text card.
page.add_row().add(Card(
    title="Plain text",
    text="A simple card. Give it a border/shadow like any visual.",
    border=True,
    shadow=True,
))

# Markdown card.
page.add_row().add(Card(
    title="Markdown",
    content_type="md",
    text=(
        "**Bold**, *italic*, `code`, and lists:\n\n"
        "- bullet one\n"
        "- bullet two\n\n"
        "| Col A | Col B |\n|---|---|\n| 1 | 2 |"
    ),
))

# Template expressions: evaluated in the browser against the report's datasets.
page.add_row().add(Card(
    title="Computed values",
    content_type="md",
    text=(
        "Orders: **{{ count('orders') }}**\n\n"
        "Total: **{{ formatCurrency(sum('orders', 'Amount'), '$', 0) }}**\n\n"
        "Average: **{{ formatCurrency(avg('orders', 'Amount'), '$', 0) }}**"
    ),
))

# Object form: the whole value is a single expression.
page.add_row().add(Card(
    title={"expr": "'Largest region total: ' + formatCurrency(max('orders', 'Amount'), '$', 0)"},
    text="The title above is computed with an `{ \"expr\": ... }` value.",
))

out_file = OUT / "03_card.html"
report.save(str(out_file))
print(f"wrote {out_file}")
