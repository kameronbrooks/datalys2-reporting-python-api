from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class AreaVisual:


    class Threshold:
        def __init__(self, 
                     value: float | int, 
                     pass_color: Optional[str] = None, 
                     fail_color: Optional[str] = None,
                     mode: str = "above",
                     show_line: bool = True,
                     line_style: str = "dashed",
                     blend_width: int = 5,
                     apply_to: str = "both"
            ):
            self.value = value
            self.pass_color = pass_color
            self.fail_color = fail_color
            self.mode = mode
            self.show_line = show_line
            self.line_style = line_style
            self.blend_width = blend_width
            self.apply_to = apply_to

        def to_dict(self) -> Dict[str, Any]:
            # Construct dictionary with snake_case keys which will be 
            # automatically converted to camelCase during serialization
            d: Dict[str, Any] = {
                "value": self.value,
                "mode": self.mode,
                "show_line": self.show_line,
                "line_style": self.line_style,
                "blend_width": self.blend_width,
                "apply_to": self.apply_to
            }
            if self.pass_color is not None:
                d["pass_color"] = self.pass_color
            if self.fail_color is not None:
                d["fail_color"] = self.fail_color
            return d

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    def add_area(
        self,
        dataset_id: str,
        x_column: str | int,
        y_columns: List[str] | str,
        smooth: bool | None = None,
        show_line: bool | None = None,
        show_markers: bool | None = None,
        fill_opacity: float | None = None,
        show_legend: bool | None = None,
        show_labels: bool | None = None,
        min_y: float | int | None = None,
        max_y: float | int | None = None,
        colors: Optional[List[str]] = None,
        threshold: Optional[Dict[str, Any] | AreaVisual.Threshold] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        **kwargs,
    ) -> Visual:
        """Adds an area chart visual.

        Args:
            dataset_id: The dataset id.
            x_column: Column for X values (time or category).
            y_columns: Column(s) for Y series.
            smooth: Whether to render smooth curves.
            show_line: Show line stroke on top of fill (default: true).
            show_markers: Show interactive marker points (default: true).
            fill_opacity: Area fill opacity 0-1 (default: 0.3).
            show_legend: Whether to show the legend.
            show_labels: Whether to show value labels.
            min_y: Optional minimum Y.
            max_y: Optional maximum Y.
            colors: Optional list of series colors.
            threshold: Optional configuration for pass/fail coloring. Can be a dictionary or AreaVisual.Threshold object.
            x_axis_label: Optional X-axis label.
            y_axis_label: Optional Y-axis label.
            **kwargs: Additional common visual properties.

        Returns:
            The created area visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["x_column"] = x_column
        visual_kwargs["y_columns"] = y_columns

        if smooth is not None:
            visual_kwargs["smooth"] = smooth
        if show_line is not None:
            visual_kwargs["show_line"] = show_line
        if show_markers is not None:
            visual_kwargs["show_markers"] = show_markers
        if fill_opacity is not None:
            visual_kwargs["fill_opacity"] = fill_opacity 
        if show_legend is not None:
            visual_kwargs["show_legend"] = show_legend
        if show_labels is not None:
            visual_kwargs["show_labels"] = show_labels
        if min_y is not None:
            visual_kwargs["min_y"] = min_y
        if max_y is not None:
            visual_kwargs["max_y"] = max_y
        if colors is not None:
            visual_kwargs["colors"] = colors
        
        if threshold is not None:
            if isinstance(threshold, AreaVisual.Threshold):
                visual_kwargs["threshold"] = threshold.to_dict()
            else:
                visual_kwargs["threshold"] = threshold
        
        if x_axis_label is not None:
            visual_kwargs["x_axis_label"] = x_axis_label
        if y_axis_label is not None:
            visual_kwargs["y_axis_label"] = y_axis_label

        return self.add_visual("area", dataset_id, **visual_kwargs)
