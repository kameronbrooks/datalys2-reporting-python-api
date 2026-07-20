from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class ScatterVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_scatter(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a scatter plot. Legacy helper — see :class:`dl2_reports.Scatter` for
        the typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Scatter

        return self.add_component(Scatter, *args, **kwargs)
