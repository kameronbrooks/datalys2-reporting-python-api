"""Typed visual component classes — the v2 API surface.

Each class mirrors a viewer visual type with an explicit, typed constructor.
Positional parameter order matches the legacy ``add_*`` helper of the same visual,
so migrated call sites work unchanged. All components additionally accept the
common visual props (``id``, ``padding``, ``margin``, ``border``, ``shadow``,
``flex``, ``width``, ``height``, ``modal_id``, ``filter``, ``aggregate``,
``persist_state``) and an ``extra={...}`` passthrough dict; anything else raises
``TypeError`` at construction time.

Add components to the tree with ``row.add(component)`` or ``page.add_row(*components)``.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from .component import VisualComponent

Column = Union[str, int]


class KPI(VisualComponent):
    """A KPI card (``type: "kpi"``): headline value with optional comparison and
    breach/warning status."""

    TYPE = "kpi"

    def __init__(
        self,
        dataset_id: str,
        value_column: Column = None,
        title: Optional[str] = None,
        comparison_column: Optional[Column] = None,
        comparison_row_index: Optional[int] = None,
        comparison_text: Optional[str] = None,
        row_index: Optional[int] = None,
        format: Optional[str] = None,
        rounding_precision: Optional[int] = None,
        currency_symbol: Optional[str] = None,
        good_direction: Optional[str] = None,
        breach_value: Optional[float] = None,
        warning_value: Optional[float] = None,
        description: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            value_column: Column for the main KPI value.
            title: Optional KPI card title.
            comparison_column: Column for the comparison value.
            comparison_row_index: Row index for the comparison (negative indices ok).
            comparison_text: Text shown beside the comparison (e.g. "Last Month").
            row_index: Row index to display (negative indices ok).
            format: 'number', 'currency', 'percent', 'date', or 'hms'.
            rounding_precision: Rounding precision for numeric values.
            currency_symbol: Currency symbol (viewer default '$').
            good_direction: 'higher' or 'lower'.
            breach_value: Value that triggers a breach indicator.
            warning_value: Value that triggers a warning indicator.
            description: Optional description text.
            extra: Passthrough props not modeled by this class.
            **common: Common visual props (id, padding, border, flex, modal_id, ...).
        """
        super().__init__(
            dataset_id,
            dict(
                value_column=value_column,
                title=title,
                comparison_column=comparison_column,
                comparison_row_index=comparison_row_index,
                comparison_text=comparison_text,
                row_index=row_index,
                format=format,
                rounding_precision=rounding_precision,
                currency_symbol=currency_symbol,
                good_direction=good_direction,
                breach_value=breach_value,
                warning_value=warning_value,
                description=description,
            ),
            extra=extra,
            **common,
        )


class Card(VisualComponent):
    """A text card (``type: "card"``). ``title``/``text`` support the viewer's
    ``{{ ... }}`` template syntax (including ``row`` inside row modals)."""

    TYPE = "card"

    def __init__(
        self,
        title: Optional[str] = None,
        text: Optional[str] = None,
        content_type: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            title: Optional title (template syntax supported).
            text: Main card text (template syntax supported).
            content_type: 'text' (default in viewer), 'html', or 'md'.
            extra: Passthrough props not modeled by this class.
            **common: Common visual props.
        """
        super().__init__(
            None,
            dict(title=title, text=text, content_type=content_type),
            extra=extra,
            **common,
        )
