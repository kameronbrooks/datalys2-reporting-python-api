from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class BoxplotVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    def add_boxplot(
        self,
        dataset_id: str,
        data_column: str | int | None = None,
        category_column: str | int | None = None,
        min_column: str | int | None = None,
        q1_column: str | int | None = None,
        median_column: str | int | None = None,
        q3_column: str | int | None = None,
        max_column: str | int | None = None,
        mean_column: str | int | None = None,
        direction: str | None = None,
        show_outliers: bool | None = None,
        color: str | List[str] | None = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds a box plot visual.

        Supports two modes:
        - Data mode: provide `data_column` (and optional `category_column`).
        - Pre-calculated mode: provide min/q1/median/q3/max (and optional mean).

        Args:
            dataset_id: The dataset id.
            data_column: Raw values column (data mode).
            category_column: Grouping/label column.
            min_column/q1_column/median_column/q3_column/max_column/mean_column: Pre-calc columns.
            direction: 'vertical' or 'horizontal'.
            show_outliers: Whether to show outliers.
            color: Fill color or scheme.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created boxplot visual.
        """
        visual_kwargs = dict(kwargs)
        if data_column is not None:
            visual_kwargs["data_column"] = data_column
        if category_column is not None:
            visual_kwargs["category_column"] = category_column
        if min_column is not None:
            visual_kwargs["min_column"] = min_column
        if q1_column is not None:
            visual_kwargs["q1_column"] = q1_column
        if median_column is not None:
            visual_kwargs["median_column"] = median_column
        if q3_column is not None:
            visual_kwargs["q3_column"] = q3_column
        if max_column is not None:
            visual_kwargs["max_column"] = max_column
        if mean_column is not None:
            visual_kwargs["mean_column"] = mean_column
        if direction is not None:
            visual_kwargs["direction"] = direction
        if show_outliers is not None:
            visual_kwargs["show_outliers"] = show_outliers
        if color is not None:
            visual_kwargs["color"] = color
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label
        return self.add_visual("boxplot", dataset_id, **visual_kwargs)
