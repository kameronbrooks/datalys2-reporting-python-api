from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class BarVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_bar(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a clustered or stacked bar chart (``stacked=True`` for stacked).
        Legacy helper — see :class:`dl2_reports.Bar` for the typed parameter
        reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Bar

        return self.add_component(Bar, *args, **kwargs)
