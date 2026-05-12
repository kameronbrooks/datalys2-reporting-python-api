from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class HistogramVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> Optional["Visual"]: ...

    def add_histogram(
        self,
        dataset_id: str,
        column: str | int,
        bins: int | None = None,
        color: Optional[str] = None,
        show_labels: bool | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Optional[Visual]:
        """Adds a histogram visual.

        Args:
            dataset_id: The dataset id.
            column: Numeric column to bin.
            bins: Number of bins.
            color: Bar color.
            show_labels: Whether to show count labels.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created histogram visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["column"] = column
        if bins is not None:
            visual_kwargs["bins"] = bins
        if color is not None:
            visual_kwargs["color"] = color
        if show_labels is not None:
            visual_kwargs["show_labels"] = show_labels
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("histogram", dataset_id, **visual_kwargs)
