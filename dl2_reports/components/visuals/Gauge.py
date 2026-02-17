from __future__ import annotations
from typing import Optional, List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class GaugeVisual:

    class Range:
        def __init__(self, 
                     from_value: Optional[float] = None, 
                     to_value: Optional[float] = None, 
                     color: Optional[str] = None, 
                     label: Optional[str] = None
            ):
            self.from_value = from_value
            self.to_value = to_value
            self.color = color
            self.label = label

        def to_dict(self) -> Dict[str, Any]:
            d = {}
            if self.from_value is not None:
                d["from"] = self.from_value
            if self.to_value is not None:
                d["to"] = self.to_value
            if self.color is not None:
                d["color"] = self.color
            if self.label is not None:
                d["label"] = self.label
            return d

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    def add_gauge(
        self,
        dataset_id: str,
        value_column: str | int = 0,
        row_index: int | None = None,
        min_value: float | int | None = None,
        max_value: float | int | None = None,
        title: Optional[str] = None,
        thickness: int | None = None,
        start_angle: float | None = None,
        end_angle: float | None = None,
        ranges: Optional[List[Dict[str, Any]] | List[GaugeVisual.Range]] = None,
        track_color: Optional[str] = None,
        value_color: Optional[str] = None,
        needle_color: Optional[str] = None,
        show_needle: bool | None = None,
        show_value: bool | None = None,
        show_min_max: bool | None = None,
        format: str | None = None,
        rounding_precision: int | None = None,
        currency_symbol: str | None = None,
        unit: Optional[str] = None,
        colors: str | List[str] | None = None,
        show_legend: bool | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a gauge/speedometer visual.

        Displays a gauge visualization with an animated needle, optional range bands, 
        and value display. The gauge animates smoothly when first rendered.

        Args:
            dataset_id: The dataset id.
            value_column: Column containing the gauge value (default: 0).
            row_index: Row index to read the value from (default: 0).
            min_value: Minimum value for the gauge scale (default: 0).
            max_value: Maximum value for the gauge scale (default: 100).
            title: Optional title displayed above the gauge.
            thickness: Arc thickness in pixels (default: 24).
            start_angle: Start angle in radians (default: -π/2, i.e., -90°).
            end_angle: End angle in radians (default: π/2, i.e., 90°).
            ranges: Optional array of range bands with colors. Each range dict should contain:
                - from: Start value of the range
                - to: End value of the range
                - color: Optional color for this range segment
                - label: Optional label for this range (shown in tooltip)
            track_color: Background track color when no ranges are defined.
            value_color: Color for the value arc when no ranges are defined.
            needle_color: Color of the needle (default: var(--dl2-text-main)).
            show_needle: Whether to show the needle (default: true).
            show_value: Whether to show the center value (default: true).
            show_min_max: Whether to show min/max labels (default: true).
            format: Display format for the value ('number', 'currency', or 'percent').
            rounding_precision: Decimal precision for the value (default: 1).
            currency_symbol: Currency symbol when format is 'currency' (default: '$').
            unit: Optional unit text displayed below the value.
            colors: Color palette for ranges (D3 scheme or array).
            show_legend: Whether to show the legend for ranges (default: false).
            **kwargs: Additional common visual properties.

        Returns:
            The created gauge visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["value_column"] = value_column
        
        if row_index is not None:
            visual_kwargs["row_index"] = row_index
        if min_value is not None:
            visual_kwargs["min_value"] = min_value
        if max_value is not None:
            visual_kwargs["max_value"] = max_value
        if title is not None:
            visual_kwargs["title"] = title
        if thickness is not None:
            visual_kwargs["thickness"] = thickness
        if start_angle is not None:
            visual_kwargs["start_angle"] = start_angle
        if end_angle is not None:
            visual_kwargs["end_angle"] = end_angle
        if ranges is not None:
            visual_kwargs["ranges"] = ranges
        if track_color is not None:
            visual_kwargs["track_color"] = track_color
        if value_color is not None:
            visual_kwargs["value_color"] = value_color
        if needle_color is not None:
            visual_kwargs["needle_color"] = needle_color
        if show_needle is not None:
            visual_kwargs["show_needle"] = show_needle
        if show_value is not None:
            visual_kwargs["show_value"] = show_value
        if show_min_max is not None:
            visual_kwargs["show_min_max"] = show_min_max
        if format is not None:
            visual_kwargs["format"] = format
        if rounding_precision is not None:
            visual_kwargs["rounding_precision"] = rounding_precision
        if currency_symbol is not None:
            visual_kwargs["currency_symbol"] = currency_symbol
        if unit is not None:
            visual_kwargs["unit"] = unit
        if colors is not None:
            visual_kwargs["colors"] = colors
        if show_legend is not None:
            visual_kwargs["show_legend"] = show_legend
        
        return self.add_visual("gauge", dataset_id, **visual_kwargs)
