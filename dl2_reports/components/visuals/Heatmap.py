from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class HeatmapVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> Optional["Visual"]: ...

    def add_heatmap(
        self,
        dataset_id: str,
        x_column: str | int,
        y_column: str | int,
        value_column: str | int,
        show_cell_labels: bool | None = None,
        min_value: float | int | None = None,
        max_value: float | int | None = None,
        color: str | List[str] | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Optional[Visual]:
        """Adds a heatmap visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for X categories.
            y_column: Column for Y categories.
            value_column: Column for cell values.
            show_cell_labels: Whether to show values inside cells.
            min_value: Optional minimum for the color scale.
            max_value: Optional maximum for the color scale.
            color: D3 interpolator name (e.g., 'Viridis') or custom colors.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created heatmap visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_column"] = y_column
        visual_kwargs["value_column"] = value_column
        if show_cell_labels is not None:
            visual_kwargs["show_cell_labels"] = show_cell_labels
        if min_value is not None:
            visual_kwargs["min_value"] = min_value
        if max_value is not None:
            visual_kwargs["max_value"] = max_value
        if color is not None:
            visual_kwargs["color"] = color
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("heatmap", dataset_id, **visual_kwargs)
