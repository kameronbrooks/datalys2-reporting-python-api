from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class PieVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> Optional["Visual"]: ...

    def add_pie(
        self,
        dataset_id: str,
        category_column: str | int,
        value_column: str | int,
        inner_radius: int | None = None,
        show_legend: bool | None = None,
        **kwargs,
    ) -> Optional[Visual]:
        """Adds a pie/donut chart visual.

        Args:
            dataset_id: The dataset id.
            category_column: Column for slice labels.
            value_column: Column for slice values.
            inner_radius: Inner radius for donut styling.
            show_legend: Whether to show the legend.
            **kwargs: Additional common visual properties.

        Returns:
            The created pie visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["category_column"] = category_column
        visual_kwargs["value_column"] = value_column
        if inner_radius is not None:
            visual_kwargs["inner_radius"] = inner_radius
        if show_legend is not None:
            visual_kwargs["show_legend"] = show_legend
        return self.add_visual("pie", dataset_id, **visual_kwargs)
