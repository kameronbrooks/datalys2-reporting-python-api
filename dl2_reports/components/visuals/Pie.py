from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class PieVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_pie(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a pie/donut chart. Legacy helper — see :class:`dl2_reports.Pie` for
        the typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Pie

        return self.add_component(Pie, *args, **kwargs)
