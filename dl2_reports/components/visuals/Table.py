from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class TableVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_table(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a table visual. Legacy helper — see :class:`dl2_reports.Table` for the
        typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Table

        return self.add_component(Table, *args, **kwargs)
