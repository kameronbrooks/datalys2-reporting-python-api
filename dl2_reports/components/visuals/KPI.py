from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual  # Only imported for type checkers


class KPIVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    # Visual helpers
    def add_kpi(
        self,
        dataset_id: str,
        value_column: str | int,
        title: Optional[str] = None,
        comparison_column: str | int | None = None,
        comparison_row_index: int | None = None,
        comparison_text: str | None = None,
        row_index: int | None = None,
        format: str | None = None,
        rounding_precision: int | None = None,
        currency_symbol: str | None = None,
        good_direction: str | None = None,
        breach_value: float | int | None = None,
        warning_value: float | int | None = None,
        description: Optional[str] = None,
        width: int | None = None,
        height: int | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a KPI visual.

        Matches the KPI schema documented in `DOCUMENTATION.md`.

        Args:
            dataset_id: The dataset id.
            value_column: Column for the main KPI value.
            title: Optional KPI card title.
            comparison_column: Column for the comparison value.
            comparison_row_index: Row index to use for comparison (supports negative indices).
            comparison_text: The comparison text to show alongside the comparison value. Ex. ("Last Month", "Yesterday", etc.).
            row_index: Row index to display (supports negative indices).
            format: 'number', 'currency', 'percent', or 'date'.
            currency_symbol: Currency symbol (viewer default is '$').
            good_direction: Which direction is "good" ('higher' or 'lower').
            breach_value: Value that triggers a breach indicator.
            warning_value: Value that triggers a warning indicator.
            description: Optional description text.
            width: Optional width.
            height: Optional height.
            rounding_precision: Optional rounding precision for numeric values.
            **kwargs: Additional common visual properties.

        Returns:
            The created KPI visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["value_column"] = value_column

        if title is not None:
            visual_kwargs["title"] = title
        if description is not None:
            visual_kwargs["description"] = description
        if comparison_column is not None:
            visual_kwargs["comparison_column"] = comparison_column
        if comparison_row_index is not None:
            visual_kwargs["comparison_row_index"] = comparison_row_index
        if comparison_text is not None:
            visual_kwargs["comparison_text"] = comparison_text
        if row_index is not None:
            visual_kwargs["row_index"] = row_index
        if format is not None:
            visual_kwargs["format"] = format
        if currency_symbol is not None:
            visual_kwargs["currency_symbol"] = currency_symbol
        if good_direction is not None:
            visual_kwargs["good_direction"] = good_direction
        if breach_value is not None:
            visual_kwargs["breach_value"] = breach_value
        if warning_value is not None:
            visual_kwargs["warning_value"] = warning_value
        if width is not None:
            visual_kwargs["width"] = width
        if height is not None:
            visual_kwargs["height"] = height
        if rounding_precision is not None:
            visual_kwargs["rounding_precision"] = rounding_precision

        return self.add_visual("kpi", dataset_id, **visual_kwargs)
