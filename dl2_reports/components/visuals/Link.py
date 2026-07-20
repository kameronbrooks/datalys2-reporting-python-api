from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class LinkVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_link(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a link visual (dl2 0.4+). Legacy helper — see :class:`dl2_reports.Link`
        for the typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Link

        return self.add_component(Link, *args, **kwargs)
