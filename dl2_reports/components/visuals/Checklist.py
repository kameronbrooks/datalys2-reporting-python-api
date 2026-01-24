from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class ChecklistVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    def add_checklist(
        self,
        dataset_id: str,
        status_column: str,
        warning_column: Optional[str] = None,
        warning_threshold: int | None = None,
        columns: Optional[List[str]] = None,
        page_size: int | None = None,
        show_search: bool | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a checklist visual.

        Args:
            dataset_id: The dataset id.
            status_column: Column containing a truthy completion value.
            warning_column: Optional date column to evaluate for warnings.
            warning_threshold: Days before due date to trigger warning.
            columns: Optional subset of columns to display.
            page_size: Rows per page.
            show_search: Whether to show the search box.
            **kwargs: Additional common visual properties.

        Returns:
            The created checklist visual.
        """
        visual_kwargs = dict(kwargs)
        visual_kwargs["status_column"] = status_column
        if warning_column is not None:
            visual_kwargs["warning_column"] = warning_column
        if warning_threshold is not None:
            visual_kwargs["warning_threshold"] = warning_threshold
        if columns is not None:
            visual_kwargs["columns"] = columns
        if page_size is not None:
            visual_kwargs["page_size"] = page_size
        if show_search is not None:
            visual_kwargs["show_search"] = show_search
        return self.add_visual("checklist", dataset_id, **visual_kwargs)
