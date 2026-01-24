from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class CardVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    def add_card(self, 
            title: str | None, 
            text: str,
            content_type: str | None = None,
            **kwargs) -> Visual:
        """Adds a card visual.

        Args:
            title: Optional title (supports template syntax in the viewer).
            text: Main card text (supports template syntax in the viewer).
            content_type: Optional content type for the card (e.g., "text", "html", "md").

        Returns:
            The created card visual.
        """
        visual_kwargs = dict(kwargs)
        if title is not None:
            visual_kwargs["title"] = title

        visual_kwargs["text"] = text
        visual_kwargs["content_type"] = content_type
        return self.add_visual("card", None, **visual_kwargs)
