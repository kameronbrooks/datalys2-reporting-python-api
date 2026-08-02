from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class CalendarVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_calendar(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a calendar visual (dl2 0.5+). Legacy helper — see
        :class:`dl2_reports.Calendar` for the typed parameter reference; unknown
        kwargs pass through for compatibility."""
        from ..visual_components import Calendar

        return self.add_component(Calendar, *args, **kwargs)
