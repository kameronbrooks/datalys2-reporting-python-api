"""Checklist (type: "checklist") — a read-only task list driven by the dataset:
a status column marks completion, an optional date column drives due-soon /
overdue warnings. Since dl2 0.4.1 it has full table UX plus status filter
chips and a completion progress bar."""

from datetime import date, timedelta
from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import Checklist, ConditionalFormat, DL2Report, filters as F

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Checklist Showcase",
    description="Task status, due-date warnings, chips, and progress.",
    compress_visuals=False,
)

today = date.today()
tasks = pd.DataFrame({
    "Task": [
        "Draft Q3 forecast", "Renew TLS certificates", "Onboard new vendor",
        "Archive 2024 records", "Update runbooks", "Security review",
    ],
    "Owner":    ["Ann", "Ben", "Cara", "Dan", "Elle", "Finn"],
    "Priority": ["High", "High", "Medium", "Low", "Medium", "High"],
    "Done":     [True, False, False, True, False, False],
    "Due": [
        str(today - timedelta(days=10)),  # done, past due date — fine
        str(today - timedelta(days=2)),   # overdue
        str(today + timedelta(days=2)),   # due soon (within warning_threshold)
        str(today + timedelta(days=20)),
        str(today + timedelta(days=4)),   # due soon
        str(today + timedelta(days=15)),  # pending
    ],
})
report.add_df("tasks", tasks)

page = report.add_page("Checklist")

page.add_row().add(Checklist(
    "tasks",
    id="ops-checklist",            # stable id → chips/sort/columns persist in the browser
    status_column="Done",          # truthy = complete
    warning_column="Due",          # date column checked for overdue / due-soon
    warning_threshold=5,           # days before the due date that count as "due soon"
    column_formats={"Due": "date"},
    conditional_formats=[
        ConditionalFormat(when=F.eq("Priority", "High"), columns=["Priority"], style="warning"),
    ],
    row_modal=True,                # double-click a task for details (leads with status)
    export_file_name="tasks.csv",  # exports include a derived Status column
))

# Start with completed tasks hidden (the Complete chip toggled off).
page.add_row().add(Checklist(
    "tasks",
    title="Open work only",
    status_column="Done",
    warning_column="Due",
    hide_completed=True,
    show_progress=False,
))

out_file = OUT / "05_checklist.html"
report.save(str(out_file))
print(f"wrote {out_file}")
