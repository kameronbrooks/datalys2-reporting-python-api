from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class LinkVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> Optional["Visual"]: ...

    def add_link(
        self,
        target_id: Optional[str] = None,
        href: Optional[str] = None,
        label: Optional[str] = None,
        link_style: Optional[str] = None,
        **kwargs,
    ) -> Optional[Visual]:
        """Adds a link visual (dl2 0.4+) for in-report navigation or external URLs.

        Exactly one of ``target_id`` or ``href`` is required.

        Args:
            target_id: The id of a visual to navigate to. The viewer switches to the
                containing page, activates containing tabs (nested included), scrolls
                to the visual, and flashes it.
            href: An external URL to open in a new tab.
            label: Link text. Defaults (in the viewer) to the target id / href.
            link_style: 'link' (default) or 'button'.
            **kwargs: Additional common visual properties (padding, margin, flex, ...).

        Returns:
            The created link visual.

        Raises:
            ValueError: If neither or both of ``target_id`` and ``href`` are given.
        """
        if (target_id is None) == (href is None):
            raise ValueError("add_link requires exactly one of target_id or href.")

        visual_kwargs = dict(kwargs)
        if target_id is not None:
            visual_kwargs["target_id"] = target_id
        if href is not None:
            visual_kwargs["href"] = href
        if label is not None:
            visual_kwargs["label"] = label
        if link_style is not None:
            visual_kwargs["link_style"] = link_style
        return self.add_visual("link", None, **visual_kwargs)
