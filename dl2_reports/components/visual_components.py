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
        column_formats: Optional[Dict[str, Any]] = None,
        conditional_formats: Optional[List[Any]] = None,
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
            column_formats: Per-column display formats (dl2 0.4.1+) — column name →
                :class:`~dl2_reports.ColumnFormat`, ``{"format", ...}`` dict, or
                shorthand kind string (``"due": "date"``). Keys are column names
                and are preserved verbatim. Display-only: CSV export keeps raw values.
            conditional_formats: Highlight rules (dl2 0.4.1+) — list of
                :class:`~dl2_reports.ConditionalFormat` or dicts. First matching
                rule wins per target; the preset field is ``style``, not ``preset``.
            extra: Passthrough props not modeled by this class.
            **common: Common visual props (id enables persistence/link targeting;
                persist_state opts out).
        """
        if isinstance(total_row, dict):
            total_row = _protect_total_fns(total_row)
        column_formats = _protect_column_formats(column_formats)
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
                column_formats=column_formats,
                conditional_formats=conditional_formats,
                id=id,
                persist_state=persist_state,
            ),
            extra=extra,
            **common,
        )


class Checklist(VisualComponent):
    """A task checklist (``type: "checklist"``) with completion status, due-date
    warnings, and — since dl2 0.4.1 — full table parity (sorting, column hiding,
    export, context menus, row modals, persistent state) plus status filter chips
    and a completion progress bar. Read-only by design: status always comes from
    the dataset."""

    TYPE = "checklist"

    def __init__(
        self,
        dataset_id: str,
        status_column: str = None,
        warning_column: Optional[str] = None,
        warning_threshold: Optional[int] = None,
        columns: Optional[List[str]] = None,
        page_size: Optional[int] = None,
        show_search: Optional[bool] = None,
        sortable: Optional[bool] = None,
        default_sort: Optional[List[Any]] = None,
        hidden_columns: Optional[List[str]] = None,
        allow_column_hiding: Optional[bool] = None,
        enable_export: Optional[bool] = None,
        export_file_name: Optional[str] = None,
        context_menu: Optional[bool] = None,
        max_height: Optional[int] = None,
        sticky_header: Optional[bool] = None,
        row_modal: Optional[bool] = None,
        row_modal_id: Optional[str] = None,
        row_modal_columns: Optional[List[str]] = None,
        row_modal_title: Optional[str] = None,
        show_status_filter: Optional[bool] = None,
        show_progress: Optional[bool] = None,
        hide_completed: Optional[bool] = None,
        column_formats: Optional[Dict[str, Any]] = None,
        conditional_formats: Optional[List[Any]] = None,
        id: Optional[str] = None,
        persist_state: Optional[bool] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            status_column: Column containing a truthy completion value.
            warning_column: Optional date column to evaluate for warnings.
            warning_threshold: Days before due date to trigger warning (viewer default 3).
            columns: Optional subset of columns to display.
            page_size: Rows per page.
            show_search: Whether to show the search box.
            sortable: Type-aware sorting; Shift+click multi-sort (viewer default True).
                The Status header sorts by urgency.
            default_sort: Initial sort — list of :class:`~dl2_reports.SortSpec` or
                ``{"column", "direction"}`` dicts. Accepts the special column
                ``"status"`` (sorts by urgency: overdue → due soon → pending →
                complete). Viewer default is the urgency sort, then due date.
            hidden_columns: Columns hidden initially.
            allow_column_hiding: Runtime Columns menu (viewer default True).
            enable_export: CSV export / clipboard copy (viewer default True).
                Exports include a derived ``Status`` column.
            export_file_name: File name for CSV export.
            context_menu: Right-click context menus (viewer default True).
            max_height: Max body height in px (scrollable body + sticky header).
            sticky_header: Viewer default True when max_height is set.
            row_modal: Built-in row detail modal on double-click (leads with status).
            row_modal_id: Open a custom modal instead; cards inside can use
                ``{{ row.Col }}`` templates.
            row_modal_columns: Columns listed in the built-in detail modal.
            row_modal_title: Title of the built-in detail modal.
            show_status_filter: Status filter chips with counts — All / Pending /
                Due Soon / Overdue / Complete (viewer default True).
            show_progress: Completion progress bar next to the "X / Y Completed"
                summary (viewer default True).
            hide_completed: Start with completed tasks hidden — the Complete chip
                toggled off (viewer default False).
            column_formats: Per-column display formats (dl2 0.4.1+) — column name →
                :class:`~dl2_reports.ColumnFormat`, ``{"format", ...}`` dict, or
                shorthand kind string (``"due": "date"``). Keys are column names
                and are preserved verbatim. Display-only: CSV export keeps raw values.
            conditional_formats: Highlight rules (dl2 0.4.1+) — list of
                :class:`~dl2_reports.ConditionalFormat` or dicts. First matching
                rule wins per target; the preset field is ``style``, not ``preset``.
            extra: Passthrough props not modeled by this class.
            **common: Common visual props (id enables persistence/link targeting;
                persist_state opts out).
        """
        column_formats = _protect_column_formats(column_formats)
        super().__init__(
            dataset_id,
            dict(
                status_column=status_column,
                warning_column=warning_column,
                warning_threshold=warning_threshold,
                columns=columns,
                page_size=page_size,
                show_search=show_search,
                sortable=sortable,
                default_sort=default_sort,
                hidden_columns=hidden_columns,
                allow_column_hiding=allow_column_hiding,
                enable_export=enable_export,
                export_file_name=export_file_name,
                context_menu=context_menu,
                max_height=max_height,
                sticky_header=sticky_header,
                row_modal=row_modal,
                row_modal_id=row_modal_id,
                row_modal_columns=row_modal_columns,
                row_modal_title=row_modal_title,
                show_status_filter=show_status_filter,
                show_progress=show_progress,
                hide_completed=hide_completed,
                column_formats=column_formats,
                conditional_formats=conditional_formats,
                id=id,
                persist_state=persist_state,
            ),
            extra=extra,
            **common,
        )


class Histogram(VisualComponent):
    """A histogram (``type: "histogram"``) of a numeric column."""

    TYPE = "histogram"

    def __init__(
        self,
        dataset_id: str,
        column: Column = None,
        bins: Optional[int] = None,
        color: Optional[str] = None,
        show_labels: Optional[bool] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            column: Numeric column to bin.
            bins: Number of bins.
            color: Bar color.
            show_labels: Whether to show count labels.
            x_axis_label / y_axis_label: Axis labels.
        """
        super().__init__(
            dataset_id,
            dict(
                column=column,
                bins=bins,
                color=color,
                show_labels=show_labels,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
            ),
            extra=extra,
            **common,
        )


class Heatmap(VisualComponent):
    """A heatmap matrix (``type: "heatmap"``)."""

    TYPE = "heatmap"

    def __init__(
        self,
        dataset_id: str,
        x_column: Column = None,
        y_column: Column = None,
        value_column: Column = None,
        show_cell_labels: Optional[bool] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        color: Union[str, List[str], None] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            x_column / y_column: Category columns.
            value_column: Column for cell heat values.
            show_cell_labels: Whether to show values inside cells.
            min_value / max_value: Optional color-scale bounds.
            color: D3 interpolator name (e.g. 'Viridis') or list of colors.
            x_axis_label / y_axis_label: Axis labels.
        """
        super().__init__(
            dataset_id,
            dict(
                x_column=x_column,
                y_column=y_column,
                value_column=value_column,
                show_cell_labels=show_cell_labels,
                min_value=min_value,
                max_value=max_value,
                color=color,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
            ),
            extra=extra,
            **common,
        )


class Gauge(VisualComponent):
    """A gauge/speedometer (``type: "gauge"``) with animated needle and range bands."""

    TYPE = "gauge"

    def __init__(
        self,
        dataset_id: str,
        value_column: Column = 0,
        row_index: Optional[int] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        title: Optional[str] = None,
        thickness: Optional[int] = None,
        start_angle: Optional[float] = None,
        end_angle: Optional[float] = None,
        ranges: Optional[List[Any]] = None,
        track_color: Optional[str] = None,
        value_color: Optional[str] = None,
        needle_color: Optional[str] = None,
        show_needle: Optional[bool] = None,
        show_value: Optional[bool] = None,
        show_min_max: Optional[bool] = None,
        format: Optional[str] = None,
        rounding_precision: Optional[int] = None,
        currency_symbol: Optional[str] = None,
        unit: Optional[str] = None,
        colors: Union[str, List[str], None] = None,
        show_legend: Optional[bool] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            value_column: Column containing the gauge value.
            row_index: Row index to read the value from (viewer default 0).
            min_value / max_value: Gauge scale bounds (viewer defaults 0/100).
            title: Optional title displayed above the gauge.
            thickness: Arc thickness in px (viewer default 24).
            start_angle / end_angle: Angles in radians.
            ranges: Range bands — :class:`~dl2_reports.GaugeRange` shapes or dicts.
            track_color / value_color / needle_color: Colors.
            show_needle / show_value / show_min_max / show_legend: Display toggles.
            format: 'number', 'currency', or 'percent'.
            rounding_precision: Decimal precision (viewer default 1).
            currency_symbol: Currency symbol (viewer default '$').
            unit: Optional unit text below the value.
            colors: Color palette for ranges (D3 scheme or array).
        """
        super().__init__(
            dataset_id,
            dict(
                value_column=value_column,
                row_index=row_index,
                min_value=min_value,
                max_value=max_value,
                title=title,
                thickness=thickness,
                start_angle=start_angle,
                end_angle=end_angle,
                ranges=ranges,
                track_color=track_color,
                value_color=value_color,
                needle_color=needle_color,
                show_needle=show_needle,
                show_value=show_value,
                show_min_max=show_min_max,
                format=format,
                rounding_precision=rounding_precision,
                currency_symbol=currency_symbol,
                unit=unit,
                colors=colors,
                show_legend=show_legend,
            ),
            extra=extra,
            **common,
        )


class Boxplot(VisualComponent):
    """A box plot (``type: "boxplot"``): raw-data mode (``data_column``) or
    pre-calculated mode (``min/q1/median/q3/max`` columns)."""

    TYPE = "boxplot"

    def __init__(
        self,
        dataset_id: str,
        data_column: Optional[Column] = None,
        category_column: Optional[Column] = None,
        min_column: Optional[Column] = None,
        q1_column: Optional[Column] = None,
        median_column: Optional[Column] = None,
        q3_column: Optional[Column] = None,
        max_column: Optional[Column] = None,
        mean_column: Optional[Column] = None,
        direction: Optional[str] = None,
        show_outliers: Optional[bool] = None,
        color: Union[str, List[str], None] = None,
        x_axis_label: Optional[str] = None,
        y_axis_label: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: The dataset id.
            data_column: Raw values column (data mode).
            category_column: Grouping/label column.
            min_column/q1_column/median_column/q3_column/max_column/mean_column:
                Pre-calculated stat columns.
            direction: 'vertical' or 'horizontal'.
            show_outliers: Whether to show outliers (data mode).
            color: Fill color, list, or D3 scheme name.
            x_axis_label / y_axis_label: Axis labels.
        """
        super().__init__(
            dataset_id,
            dict(
                data_column=data_column,
                category_column=category_column,
                min_column=min_column,
                q1_column=q1_column,
                median_column=median_column,
                q3_column=q3_column,
                max_column=max_column,
                mean_column=mean_column,
                direction=direction,
                show_outliers=show_outliers,
                color=color,
                x_axis_label=x_axis_label,
                y_axis_label=y_axis_label,
            ),
            extra=extra,
            **common,
        )


class Link(VisualComponent):
    """A navigation link (``type: "link"``, dl2 0.4+). Requires exactly one of
    ``target_id`` (in-report navigation) or ``href`` (external URL)."""

    TYPE = "link"

    def __init__(
        self,
        target_id: Optional[str] = None,
        href: Optional[str] = None,
        label: Optional[str] = None,
        link_style: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            target_id: Id of a visual to navigate to (switches page/tabs, scrolls, flashes).
            href: External URL (opens in a new tab).
            label: Link text (viewer falls back to the target/href).
            link_style: 'link' (viewer default) or 'button'.

        Raises:
            ValueError: If neither or both of target_id and href are given.
        """
        if (target_id is None) == (href is None):
            raise ValueError("Link requires exactly one of target_id or href.")
        super().__init__(
            None,
            dict(
                target_id=target_id,
                href=href,
                label=label,
                link_style=link_style,
            ),
            extra=extra,
            **common,
        )


class ModalButton(VisualComponent):
    """A button that opens a global modal (``type: "modal"``)."""

    TYPE = "modal"

    def __init__(
        self,
        modal_id: str,
        button_label: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            modal_id: The global modal id to open.
            button_label: Button label text.
        """
        super().__init__(
            None,
            dict(id=modal_id, button_label=button_label),
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


def _protect_column_formats(column_formats: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Wraps a ``column_formats`` mapping in RawDict so column names used as dict
    keys survive serialization verbatim (values still serialize normally)."""
    from ..serialization import RawDict

    if isinstance(column_formats, dict) and not isinstance(column_formats, RawDict):
        return RawDict(column_formats)
    return column_formats


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
