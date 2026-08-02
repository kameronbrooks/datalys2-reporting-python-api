"""
Tests for the Calendar visual (dl2 0.5+): serialization, construction validation,
legacy helper parity, and migrate-tool support.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from dl2_reports import Calendar, DL2Report
from dl2_reports.components.base import ReportTreeComponent

try:
    import libcst  # noqa: F401
    HAS_LIBCST = True
except ImportError:
    HAS_LIBCST = False


def _make_report():
    report = DL2Report("Calendar Test", compress_visuals=False)
    df = pd.DataFrame({
        "Start": pd.to_datetime(["2026-03-02 09:00", "2026-03-03 13:30"]),
        "End": pd.to_datetime(["2026-03-02 10:00", "2026-03-05 14:00"]),
        "Task": ["Standup", "Offsite"],
        "Team": ["Eng", "Sales"],
    })
    report.add_df("events", df)
    return report


class TestCalendarSerialization(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1

    def test_type_and_dataset(self):
        d = Calendar("events", start_column="Start").to_dict()
        self.assertEqual(d["type"], "calendar")
        self.assertEqual(d["datasetId"], "events")

    def test_props_camel_cased(self):
        d = Calendar(
            "events",
            start_column="Start",
            end_column="End",
            title_column="Task",
            category_column="Team",
            title="Team calendar",
            description="All events",
            default_view="week",
            default_date="2026-03-01",
            week_starts_on=1,
            show_weekends=False,
            day_start_hour=8,
            day_end_hour=18,
            hour_height=32,
            max_events_per_day=2,
            time_format="24h",
            max_height=400,
            empty_label="Nothing scheduled.",
            color="tableau10",
            show_legend=True,
            legend_title="Teams",
            row_modal=True,
            row_modal_columns=["Task", "Team"],
            row_modal_title="Event details",
            context_menu=True,
            id="cal",
            persist_state=True,
        ).to_dict()
        expected = {
            "type": "calendar",
            "elementType": "visual",
            "id": "cal",
            "datasetId": "events",
            "startColumn": "Start",
            "endColumn": "End",
            "titleColumn": "Task",
            "categoryColumn": "Team",
            "title": "Team calendar",
            "description": "All events",
            "defaultView": "week",
            "defaultDate": "2026-03-01",
            "weekStartsOn": 1,
            "showWeekends": False,
            "dayStartHour": 8,
            "dayEndHour": 18,
            "hourHeight": 32,
            "maxEventsPerDay": 2,
            "timeFormat": "24h",
            "maxHeight": 400,
            "emptyLabel": "Nothing scheduled.",
            "color": "tableau10",
            "showLegend": True,
            "legendTitle": "Teams",
            "rowModal": True,
            "rowModalColumns": ["Task", "Team"],
            "rowModalTitle": "Event details",
            "contextMenu": True,
            "persistState": True,
        }
        self.assertEqual(d, expected)

    def test_none_props_dropped(self):
        d = Calendar("events", date_column="Start").to_dict()
        self.assertNotIn("defaultView", d)
        self.assertNotIn("endColumn", d)
        self.assertNotIn("rowModal", d)

    def test_row_modal_id(self):
        d = Calendar("events", date_column="Start", row_modal_id="event-modal").to_dict()
        self.assertEqual(d["rowModalId"], "event-modal")

    def test_common_props_accepted(self):
        d = Calendar("events", date_column="Start", flex=2, border=True).to_dict()
        self.assertEqual(d["flex"], 2)
        self.assertEqual(d["border"], True)

    def test_extra_passthrough(self):
        d = Calendar("events", date_column="Start", extra={"future_prop": 1}).to_dict()
        self.assertEqual(d["futureProp"], 1)

    def test_unknown_prop_raises(self):
        with self.assertRaises(TypeError):
            Calendar("events", date_column="Start", defaultview="week")


class TestCalendarValidation(unittest.TestCase):
    def test_requires_a_date_mapping(self):
        with self.assertRaises(ValueError):
            Calendar("events")

    def test_date_and_start_conflict(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", start_column="Start")

    def test_end_without_start(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", end_column="End")

    def test_bad_default_view(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", default_view="year")

    def test_bad_time_format(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", time_format="24")

    def test_bad_week_starts_on(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", week_starts_on=2)

    def test_day_start_hour_bounds(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", day_start_hour=24)
        Calendar("events", date_column="Start", day_start_hour=0)
        Calendar("events", date_column="Start", day_start_hour=23)

    def test_day_end_hour_bounds(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", day_end_hour=0)
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", day_end_hour=25)
        Calendar("events", date_column="Start", day_end_hour=24)

    def test_day_end_must_exceed_day_start(self):
        with self.assertRaises(ValueError):
            Calendar("events", date_column="Start", day_start_hour=10, day_end_hour=10)
        Calendar("events", date_column="Start", day_start_hour=10, day_end_hour=11)


class TestCalendarInReport(unittest.TestCase):
    def setUp(self):
        ReportTreeComponent.BASE_ID = 1

    def test_legacy_helper_parity(self):
        report = _make_report()
        row = report.add_page("P").add_row()
        legacy = row.add_calendar("events", start_column="Start", end_column="End", title_column="Task")
        typed = Calendar("events", start_column="Start", end_column="End", title_column="Task")
        legacy_d = {k: v for k, v in legacy.to_dict().items() if k != "id"}
        typed_d = {k: v for k, v in typed.to_dict().items() if k != "id"}
        self.assertEqual(legacy_d, typed_d)

    def test_on_condition_false_is_noop(self):
        report = _make_report()
        row = report.add_page("P").add_row()
        result = row.on_condition(False).add_calendar("events", date_column="Start")
        self.assertFalse(result)
        self.assertEqual(row.children, [])

    def test_compiles(self):
        report = _make_report()
        report.add_page("P").add_row().add(
            Calendar("events", start_column="Start", end_column="End", id="cal")
        )
        html = report.compile()
        self.assertIn("calendar", html)

    def test_lint_flags_unknown_kwargs(self):
        report = _make_report()
        row = report.add_page("P").add_row()
        row.add_calendar("events", date_column="Start", defaultview="week")
        with self.assertWarns(UserWarning):
            report.compile()


@unittest.skipUnless(HAS_LIBCST, "libcst not installed")
class TestCalendarMigrate(unittest.TestCase):
    def test_add_calendar_rewritten(self):
        from dl2_reports.migrate import transform_source

        src = 'row.add_calendar("events", start_column="Start", end_column="End")\n'
        out, changed = transform_source(src)
        self.assertTrue(changed)
        self.assertIn('row.add(Calendar("events", start_column="Start", end_column="End"))', out)


if __name__ == "__main__":
    unittest.main()
