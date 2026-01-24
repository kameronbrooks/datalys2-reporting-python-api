from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class ScatterVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    def add_scatter(
        self,
        dataset_id: str,
        x_column: str | int,
        y_column: str | int,
        category_column: str | int | None = None,
        show_trendline: bool | None = None,
        show_correlation: bool | None = None,
        point_size: int | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds a scatter plot visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for numeric X values.
            y_column: Column for numeric Y values.
            category_column: Optional column for coloring points by category.
            show_trendline: Whether to show a trendline.
            show_correlation: Whether to show correlation stats.
            point_size: Point size.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created scatter visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_column"] = y_column
        if category_column is not None:
            visual_kwargs["category_column"] = category_column
        if show_trendline is not None:
            visual_kwargs["show_trendline"] = show_trendline
        if show_correlation is not None:
            visual_kwargs["show_correlation"] = show_correlation
        if point_size is not None:
            visual_kwargs["point_size"] = point_size
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("scatter", dataset_id, **visual_kwargs)
