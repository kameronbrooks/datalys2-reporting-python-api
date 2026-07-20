from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class HeatmapVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_heatmap(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a heatmap visual. Legacy helper — see :class:`dl2_reports.Heatmap`
        for the typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Heatmap

        return self.add_component(Heatmap, *args, **kwargs)
