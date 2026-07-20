from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

from ...serialization import RawDict

if TYPE_CHECKING:
    from ..visual import Visual


class TableVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> Optional["Visual"]: ...

    def add_table(
        self,
        dataset_id: str,
        title: Optional[str] = None,
        columns: Optional[List[str]] = None,
        page_size: int | None = None,
        table_style: str | None = None,
        show_search: bool | None = None,
        # dl2 0.3+ table UX
        sortable: bool | None = None,
        default_sort: Optional[List[Dict[str, str]]] = None,
        hidden_columns: Optional[List[str]] = None,
        allow_column_hiding: bool | None = None,
        group_by: str | None = None,
        group_aggregates: Optional[List[Dict[str, Any]]] = None,
        groups_collapsed: bool | None = None,
        enable_export: bool | None = None,
        export_file_name: str | None = None,
        context_menu: bool | None = None,
        max_height: int | None = None,
        sticky_header: bool | None = None,
        # dl2 0.4+ totals
        total_row: Union[bool, Dict[str, Any], None] = None,
        total_column: Union[bool, Dict[str, Any], None] = None,
        # dl2 0.4+ row detail modals
        row_modal: bool | None = None,
        row_modal_id: str | None = None,
        row_modal_columns: Optional[List[str]] = None,
        row_modal_title: str | None = None,
        # dl2 0.4+ persistent view state
        id: str | None = None,
        persist_state: bool | None = None,
        **kwargs,
    ) -> Optional[Visual]:
        """Adds a table visual.

        Args:
            dataset_id: The dataset id.
            title: Optional table title.
            columns: Optional list of columns to display.
            page_size: Rows per page (groups per page while grouped).
            table_style: 'plain', 'bordered', or 'alternating'.
            show_search: Whether to show the search box.
            sortable: Whether columns are sortable (type-aware; Shift+click multi-sort).
            default_sort: Initial sort, e.g. ``[{"column": "Amount", "direction": "desc"}]``.
            hidden_columns: Columns hidden initially (user can re-show via Columns menu).
            allow_column_hiding: Whether the runtime Columns menu is available.
            group_by: Column to group rows by initially.
            group_aggregates: Per-group header aggregates, e.g.
                ``[aggregates.agg("Amount", "sum")]``.
            groups_collapsed: Whether groups start collapsed.
            enable_export: Whether CSV export / clipboard copy are available.
            export_file_name: File name for CSV export.
            context_menu: Whether right-click context menus are enabled.
            max_height: Max body height in px (scrollable body + sticky header).
            sticky_header: Whether the header sticks while scrolling (defaults to
                True in the viewer when max_height is set).
            total_row: ``True`` to sum all numeric columns over the filtered data, or
                ``{"label": ..., "fns": {"<column>": "<fn>"}}`` for per-column
                aggregate functions (fns: sum/avg/min/max/count/countDistinct/first/last).
            total_column: ``True`` to add a per-row sum of numeric columns, or
                ``{"label": ..., "columns": [...]}`` to pick columns.
            row_modal: ``True`` to open a built-in row detail modal on
                double-click / right-click → Open details.
            row_modal_id: Open a custom modal (from ``report.add_modal``) instead;
                cards inside can use ``{{ row.ColumnName }}`` templates.
            row_modal_columns: Columns listed in the built-in detail modal.
            row_modal_title: Title of the built-in detail modal.
            id: Stable element id (enables view-state persistence and link targeting).
            persist_state: Whether runtime view changes (sort/hidden/grouping) are
                saved to localStorage (defaults to True in the viewer when the table
                has an id; pass False to opt out).
            **kwargs: Additional common visual properties.

        Returns:
            The created table visual.
        """
        visual_kwargs = dict(kwargs)
        if title is not None:
            visual_kwargs["title"] = title
        if columns is not None:
            visual_kwargs["columns"] = columns
        if page_size is not None:
            visual_kwargs["page_size"] = page_size
        if table_style is not None:
            visual_kwargs["table_style"] = table_style
        if show_search is not None:
            visual_kwargs["show_search"] = show_search
        if sortable is not None:
            visual_kwargs["sortable"] = sortable
        if default_sort is not None:
            visual_kwargs["default_sort"] = default_sort
        if hidden_columns is not None:
            visual_kwargs["hidden_columns"] = hidden_columns
        if allow_column_hiding is not None:
            visual_kwargs["allow_column_hiding"] = allow_column_hiding
        if group_by is not None:
            visual_kwargs["group_by"] = group_by
        if group_aggregates is not None:
            visual_kwargs["group_aggregates"] = group_aggregates
        if groups_collapsed is not None:
            visual_kwargs["groups_collapsed"] = groups_collapsed
        if enable_export is not None:
            visual_kwargs["enable_export"] = enable_export
        if export_file_name is not None:
            visual_kwargs["export_file_name"] = export_file_name
        if context_menu is not None:
            visual_kwargs["context_menu"] = context_menu
        if max_height is not None:
            visual_kwargs["max_height"] = max_height
        if sticky_header is not None:
            visual_kwargs["sticky_header"] = sticky_header
        if total_row is not None:
            visual_kwargs["total_row"] = _protect_total_fns(total_row)
        if total_column is not None:
            visual_kwargs["total_column"] = total_column
        if row_modal is not None:
            visual_kwargs["row_modal"] = row_modal
        if row_modal_id is not None:
            visual_kwargs["row_modal_id"] = row_modal_id
        if row_modal_columns is not None:
            visual_kwargs["row_modal_columns"] = row_modal_columns
        if row_modal_title is not None:
            visual_kwargs["row_modal_title"] = row_modal_title
        if id is not None:
            visual_kwargs["id"] = id
        if persist_state is not None:
            visual_kwargs["persist_state"] = persist_state
        return self.add_visual("table", dataset_id, **visual_kwargs)


def _protect_total_fns(total_row: Union[bool, Dict[str, Any]]) -> Union[bool, Dict[str, Any]]:
    """Wraps totalRow's per-column ``fns`` mapping in RawDict so column names used as
    dict keys are not snake_case→camelCase converted during serialization."""
    if isinstance(total_row, dict) and isinstance(total_row.get("fns"), dict):
        protected = dict(total_row)
        protected["fns"] = RawDict(total_row["fns"])
        return protected
    return total_row
