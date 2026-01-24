from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class TableVisual:

    # Mixin assumes parent class provides add_visual method
    def add_visual(self, type: str, dataset_id: str | None = None, **kwargs) -> "Visual": ...

    def add_table(
        self,
        dataset_id: str,
        title: Optional[str] = None,
        columns: Optional[List[str]] = None,
        page_size: int | None = None,
        table_style: str | None = None,
        show_search: bool | None = None,
        **kwargs,
    ) -> Visual:
        """Adds a table visual.

        Args:
            dataset_id: The dataset id.
            title: Optional table title.
            columns: Optional list of columns to display.
            page_size: Rows per page.
            table_style: 'plain', 'bordered', or 'alternating'.
            show_search: Whether to show the search box.
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
        return self.add_visual("table", dataset_id, **visual_kwargs)
