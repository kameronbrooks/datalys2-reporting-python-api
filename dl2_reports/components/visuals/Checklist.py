from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class ChecklistVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_checklist(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a checklist visual. Legacy helper — see :class:`dl2_reports.Checklist`
        for the typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Checklist

        return self.add_component(Checklist, *args, **kwargs)
