"""Calendar (type: "calendar", dl2 0.5+).

Month/week/day views with a toolbar, true spanning bars for multi-day events,
category coloring with a legend, timed events on an hour grid, and event
detail modals sharing the table's row-modal API. All calendar math is UTC.

dtype drives rendering: "date" columns become all-day events, "datetime"
columns become timed events on the hour grid (add_df infers this from the
values; dtype_overrides forces it).
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow running from a repo checkout without installing dl2-reports.
try:
    import dl2_reports  # noqa: F401
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd

from dl2_reports import Calendar, Card, DL2Report

OUT = Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

report = DL2Report(
    title="Calendar Showcase",
    description="Month, week, and day views over the same dataset.",
    compress_visuals=False,
)

# Anchor the demo data to the current month so the calendar opens on events.
# Naive UTC: add_df treats naive datetimes as UTC.
monday = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
monday -= timedelta(days=monday.weekday())

events = pd.DataFrame({
    "Start": [
        monday + timedelta(hours=9),                    # timed, 1h
        monday + timedelta(days=1, hours=13, minutes=30),  # timed, crosses lunch
        monday + timedelta(days=1),                     # spans 3 days (all-midnight -> still datetime column)
        monday + timedelta(days=3, hours=15),
        monday + timedelta(days=7),                     # next week
    ],
    "End": [
        monday + timedelta(hours=10),
        monday + timedelta(days=1, hours=15),
        monday + timedelta(days=3),
        monday + timedelta(days=3, hours=16),
        monday + timedelta(days=9),
    ],
    "Task": ["Standup", "Design review", "Offsite", "1:1", "Sprint 42"],
    "Team": ["Eng", "Design", "Sales", "Eng", "Eng"],
    "Owner": ["Ann", "Ben", "Cara", "Dan", "Ann"],
})
report.add_df("events", events)

holidays = pd.DataFrame({
    "Day": [monday + timedelta(days=4), monday + timedelta(days=11)],
    "Holiday": ["Team day", "Release day"],
})
# Force all-day rendering: the column is midnight-only so "date" is inferred
# anyway, but being explicit documents the intent.
report.add_df("holidays", holidays, dtype_overrides={"Day": "date"})

# Event details open in a custom modal (same API as table row modals).
detail = report.add_modal("event-detail", "Event Details")
detail.add_row().add(Card(
    content_type="md",
    title="{{ row.Task }}",
    text="**Team:** {{ row.Team }}\n\n**Owner:** {{ row.Owner }}",
))

page = report.add_page("Calendar")

# Spanning + timed events, colored by team, custom modal on double-click.
page.add_row().add(Calendar(
    "events",
    start_column="Start",
    end_column="End",
    title_column="Task",
    category_column="Team",
    legend_title="Teams",
    default_view="month",
    week_starts_on=1,
    row_modal_id="event-detail",
    id="team-calendar",           # id => the active view persists across reloads
))

# Single-date, all-day events on a compact work-week view.
page.add_row().add(Calendar(
    "holidays",
    date_column="Day",
    title_column="Holiday",
    show_weekends=False,
    default_view="week",
    day_start_hour=8,
    day_end_hour=18,
    time_format="24h",
    title="Company days",
))

out_file = OUT / "16_calendar.html"
report.save(str(out_file))
print(f"wrote {out_file}")
