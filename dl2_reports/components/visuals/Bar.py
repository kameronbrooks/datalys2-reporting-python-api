from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class BarVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> Optional[Visual]: ...

    def add_bar(
        self,
        dataset_id: str,
        x_column: str | int,
        y_columns: List[str],
        stacked: bool = False,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        show_legend: bool | None = None,
        show_labels: bool | None = None,
        horizontal: bool | None = None,
        threshold: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[Visual]:
        """Adds a clustered or stacked bar chart visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for X-axis categories.
            y_columns: Series columns for Y values.
            stacked: If True, uses stacked bars; otherwise clustered.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            show_legend: Whether to show the legend.
            show_labels: Whether to show value labels.
            horizontal: Whether to render bars horizontally (viewer-dependent).
            threshold: Optional ThresholdConfig for pass/fail coloring (clustered only).
            **kwargs: Additional common visual properties.

        Returns:
            The created bar visual.
        """
        type = "stackedBar" if stacked else "clusteredBar"
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_columns"] = y_columns
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        if threshold is not None:
            visual_kwargs["threshold"] = threshold
        if show_legend is not None:
            visual_kwargs["show_legend"] = show_legend
        if show_labels is not None:
            visual_kwargs["show_labels"] = show_labels
        if horizontal is not None:
            visual_kwargs["horizontal"] = horizontal
        return self.add_visual(type, dataset_id, **visual_kwargs)
