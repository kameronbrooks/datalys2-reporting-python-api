from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class KPIVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_kpi(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a KPI visual. Legacy helper — see :class:`dl2_reports.KPI` for the
        typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import KPI

        return self.add_component(KPI, *args, **kwargs)
