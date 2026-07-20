from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class CardVisual:

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_card(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a card visual. Legacy helper — see :class:`dl2_reports.Card` for the
        typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Card

        # Legacy parity: add_card always emitted contentType (null when unset).
        if len(args) < 3 and "content_type" not in kwargs:
            kwargs["content_type"] = None
        comp = self.add_component(Card, *args, **kwargs)
        if comp is not None and "content_type" not in comp.props:
            comp.props["content_type"] = None
        return comp
