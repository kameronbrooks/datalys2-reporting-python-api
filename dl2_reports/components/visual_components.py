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
        width: Optional[int] = None,
        height: Optional[int] = None,
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
        # dict insertion order matches the legacy helper's prop-set order (JSON
        # key order in existing reports depends on it)
        super().__init__(
            dataset_id,
            dict(
                value_column=value_column,
                title=title,
                description=description,
                comparison_column=comparison_column,
                comparison_row_index=comparison_row_index,
                comparison_text=comparison_text,
                row_index=row_index,
                format=format,
                currency_symbol=currency_symbol,
                good_direction=good_direction,
                breach_value=breach_value,
                warning_value=warning_value,
                width=width,
                height=height,
                rounding_precision=rounding_precision,
            ),
            extra=extra,
            **common,
        )


class Table(VisualComponent):
    """A data table (``type: "table"``) with sorting, grouping, export, totals,
    row detail modals, and persistent view state (dl2 0.3/0.4)."""

    TYPE = "table"

    def __init__(
        self,
        dataset_id: str,
        title: Optional[str] = None,
        columns: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        table_style: Optional[str] = None,
        show_search: Optional[bool] = None,
        sortable: Optional[bool] = None,
        default_sort: Optional[List[Any]] = None,
        hidden_columns: Optional[List[str]] = None,
        allow_column_hiding: Optional[bool] = None,
        group_by: Optional[str] = None,
        group_aggregates: Optional[List[Any]] = None,
        groups_collapsed: Optional[bool] = None,
        enable_export: Optional[bool] = None,
        export_file_name: Optional[str] = None,
        context_menu: Optional[bool] = None,
        max_height: Optional[int] = None,
        sticky_header: Optional[bool] = None,
        total_row: Union[bool, Dict[str, Any], Any, None] = None,
        total_column: Union[bool, Dict[str, Any], Any, None] = None,
        row_modal: Optional[bool] = None,
        row_modal_id: Optional[str] = None,
        row_modal_columns: Optional[List[str]] = None,
        row_modal_title: Optional[str] = None,
        id: Optional[str] = None,
        persist_state: Optional[bool] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            title: Optional table title.
            columns: Columns to display (default: all).
            page_size: Rows per page (groups per page while grouped).
            table_style: 'plain', 'bordered', or 'alternating'.
            show_search: Whether to show the search box.
            sortable: Type-aware sorting; Shift+click multi-sort (viewer default True).
            default_sort: Initial sort — list of :class:`~dl2_reports.SortSpec` or
                ``{"column", "direction"}`` dicts.
            hidden_columns: Columns hidden initially.
            allow_column_hiding: Runtime Columns menu (viewer default True).
            group_by: Initial grouping column (collapsible groups).
            group_aggregates: Per-group aggregates — :class:`~dl2_reports.AggregateColumn`,
                ``aggregates.agg(...)``, or dicts.
            groups_collapsed: Whether groups start collapsed.
            enable_export: CSV export / clipboard copy (viewer default True).
            export_file_name: File name for CSV export.
            context_menu: Right-click context menus (viewer default True).
            max_height: Max body height in px (scrollable body + sticky header).
            sticky_header: Viewer default True when max_height is set.
            total_row: ``True``, :class:`~dl2_reports.TotalRow`, or
                ``{"label", "fns"}`` dict (0.4+). Column names used as ``fns`` keys
                are preserved verbatim.
            total_column: ``True``, :class:`~dl2_reports.TotalColumn`, or
                ``{"label", "columns"}`` dict (0.4+).
            row_modal: Built-in row detail modal on double-click (0.4+).
            row_modal_id: Open a custom modal instead; cards inside can use
                ``{{ row.Col }}`` templates (0.4+).
            row_modal_columns: Columns listed in the built-in detail modal.
            row_modal_title: Title of the built-in detail modal.
            extra: Passthrough props not modeled by this class.
            **common: Common visual props (id enables persistence/link targeting;
                persist_state opts out).
        """
        if isinstance(total_row, dict):
            total_row = _protect_total_fns(total_row)
        super().__init__(
            dataset_id,
            dict(
                title=title,
                columns=columns,
                page_size=page_size,
                table_style=table_style,
                show_search=show_search,
                sortable=sortable,
                default_sort=default_sort,
                hidden_columns=hidden_columns,
                allow_column_hiding=allow_column_hiding,
                group_by=group_by,
                group_aggregates=group_aggregates,
                groups_collapsed=groups_collapsed,
                enable_export=enable_export,
                export_file_name=export_file_name,
                context_menu=context_menu,
                max_height=max_height,
                sticky_header=sticky_header,
                total_row=total_row,
                total_column=total_column,
                row_modal=row_modal,
                row_modal_id=row_modal_id,
                row_modal_columns=row_modal_columns,
                row_modal_title=row_modal_title,
                id=id,
                persist_state=persist_state,
            ),
            extra=extra,
            **common,
        )


def _protect_total_fns(total_row: Dict[str, Any]) -> Dict[str, Any]:
    """Wraps totalRow's per-column ``fns`` mapping in RawDict so column names used
    as dict keys survive serialization verbatim."""
    from ..serialization import RawDict

    if isinstance(total_row.get("fns"), dict):
        protected = dict(total_row)
        protected["fns"] = RawDict(total_row["fns"])
        return protected
    return total_row


class Pie(VisualComponent):
    """A pie/donut chart (``type: "pie"``)."""

    TYPE = "pie"

    def __init__(
        self,
        dataset_id: str,
        category_column: Column = None,
        value_column: Column = None,
        inner_radius: Optional[int] = None,
        show_legend: Optional[bool] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            category_column: Column for slice labels.
            value_column: Column for slice values.
            inner_radius: Inner radius for donut styling.
            show_legend: Whether to show the legend.
        """
        super().__init__(
            dataset_id,
            dict(
                category_column=category_column,
                value_column=value_column,
                inner_radius=inner_radius,
                show_legend=show_legend,
            ),
            extra=extra,
            **common,
        )


class Bar(VisualComponent):
    """A clustered or stacked bar chart (``type: "clusteredBar"`` / ``"stackedBar"``,
    controlled by ``stacked=``)."""

    TYPE = "clusteredBar"

    def __init__(
        self,
        dataset_id: str,
        x_column: Column = None,
        y_columns: Optional[List[str]] = None,
        stacked: bool = False,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        show_legend: Optional[bool] = None,
        show_labels: Optional[bool] = None,
        horizontal: Optional[bool] = None,
        threshold: Optional[Any] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            x_column: Column for X-axis categories.
            y_columns: Series columns for Y values.
            stacked: If True, uses stacked bars; otherwise clustered.
            x_axis_label / y_axis_label: Axis labels.
            show_legend / show_labels: Legend / value-label toggles.
            horizontal: Whether to render bars horizontally (viewer-dependent).
            threshold: :class:`~dl2_reports.Threshold` or dict (clustered only).
        """
        self.TYPE = "stackedBar" if stacked else "clusteredBar"
        super().__init__(
            dataset_id,
            dict(
                x_column=x_column,
                y_columns=y_columns,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
                threshold=threshold,
                show_legend=show_legend,
                show_labels=show_labels,
                horizontal=horizontal,
            ),
            extra=extra,
            **common,
        )


class Line(VisualComponent):
    """A line chart (``type: "line"``)."""

    TYPE = "line"

    def __init__(
        self,
        dataset_id: str,
        x_column: Column = None,
        y_columns: Union[List[str], str, None] = None,
        smooth: Optional[bool] = None,
        show_legend: Optional[bool] = None,
        show_labels: Optional[bool] = None,
        min_y: Optional[float] = None,
        max_y: Optional[float] = None,
        colors: Optional[List[str]] = None,
        threshold: Optional[Any] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            x_column: Column for X values (time or category).
            y_columns: Column(s) for Y series.
            smooth: Whether to render smooth curves.
            show_legend / show_labels: Legend / value-label toggles.
            min_y / max_y: Optional Y-axis bounds.
            colors: Optional list of series colors.
            threshold: :class:`~dl2_reports.Threshold` or dict.
            x_axis_label / y_axis_label: Axis labels.
        """
        super().__init__(
            dataset_id,
            dict(
                x_column=x_column,
                y_columns=y_columns,
                smooth=smooth,
                show_legend=show_legend,
                show_labels=show_labels,
                min_y=min_y,
                max_y=max_y,
                colors=colors,
                threshold=threshold,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
            ),
            extra=extra,
            **common,
        )


class Area(VisualComponent):
    """An area chart (``type: "area"``) — line chart features plus fill options."""

    TYPE = "area"

    def __init__(
        self,
        dataset_id: str,
        x_column: Column = None,
        y_columns: Union[List[str], str, None] = None,
        smooth: Optional[bool] = None,
        show_line: Optional[bool] = None,
        show_markers: Optional[bool] = None,
        fill_opacity: Optional[float] = None,
        show_legend: Optional[bool] = None,
        show_labels: Optional[bool] = None,
        min_y: Optional[float] = None,
        max_y: Optional[float] = None,
        colors: Optional[List[str]] = None,
        threshold: Optional[Any] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            x_column: Column for X values.
            y_columns: Column(s) for Y series.
            smooth: Whether to render smooth curves.
            show_line: Show line stroke on top of the fill (viewer default True).
            show_markers: Show interactive marker points (viewer default True).
            fill_opacity: Area fill opacity 0-1 (viewer default 0.3).
            show_legend / show_labels: Legend / value-label toggles.
            min_y / max_y: Optional Y-axis bounds.
            colors: Optional list of series colors.
            threshold: :class:`~dl2_reports.Threshold` or dict.
            x_axis_label / y_axis_label: Axis labels.
        """
        if threshold is not None and hasattr(threshold, "to_dict"):
            threshold = threshold.to_dict()
        super().__init__(
            dataset_id,
            dict(
                x_column=x_column,
                y_columns=y_columns,
                smooth=smooth,
                show_line=show_line,
                show_markers=show_markers,
                fill_opacity=fill_opacity,
                show_legend=show_legend,
                show_labels=show_labels,
                min_y=min_y,
                max_y=max_y,
                colors=colors,
                threshold=threshold,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
            ),
            extra=extra,
            **common,
        )


class Scatter(VisualComponent):
    """A scatter plot (``type: "scatter"``)."""

    TYPE = "scatter"

    def __init__(
        self,
        dataset_id: str,
        x_column: Column = None,
        y_column: Column = None,
        category_column: Optional[Column] = None,
        show_trendline: Optional[bool] = None,
        show_correlation: Optional[bool] = None,
        point_size: Optional[int] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            x_column / y_column: Columns for numeric X/Y values.
            category_column: Optional column for coloring points by category.
            show_trendline: Whether to show a linear regression trendline.
            show_correlation: Whether to show correlation stats.
            point_size: Point size.
            x_axis_label / y_axis_label: Axis labels.
        """
        super().__init__(
            dataset_id,
            dict(
                x_column=x_column,
                y_column=y_column,
                category_column=category_column,
                show_trendline=show_trendline,
                show_correlation=show_correlation,
                point_size=point_size,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
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
