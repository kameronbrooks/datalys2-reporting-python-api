from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..serialization import camel_case_dict, snake_to_camel
from .base import ReportTreeComponent
from .layout import Layout


class Tabs(ReportTreeComponent):
    """
    A tabs container visual (dl2 0.3+, ``type: "tabs"``).

    Holds named tabs, each backed by a full :class:`Layout`, so any layout/visual
    helper works inside a tab. Can be nested inside rows, grids, and other tab groups.

    When an ``id`` is provided, the active tab is persisted to localStorage by the
    viewer (dl2 0.4+); pass ``persist_state=False`` to opt out.
    """

    def __init__(
        self,
        id: Optional[str] = None,
        default_tab: Optional[int] = None,
        title: Optional[str] = None,
        tabs: Optional[List[Any]] = None,
        **kwargs,
    ):
        """
        Initializes a new Tabs container.

        Tabs can be declared up front (v2 style) with :class:`dl2_reports.Tab` shapes:

            row.add(Tabs(id="views", tabs=[
                Tab("Chart", children=[Line("sales", x_column="Month", y_columns=["Revenue"])]),
                Tab("Data", children=[Table("sales")]),
            ]))

        or built incrementally with :meth:`add_tab`.

        Args:
            id (str, optional): Stable id for the tab group (enables active-tab
                persistence and link/anchor targeting). Defaults to an auto id.
            default_tab (int, optional): Index of the initially active tab. Defaults to 0.
            title (str, optional): Optional title rendered above the tab strip.
            tabs (list, optional): :class:`~dl2_reports.Tab` shapes (or equivalent
                ``{"title", "children"|"layout"}`` dicts) declaring the tabs up front.
            **kwargs: Additional container properties (e.g. padding, margin, border,
                shadow, flex, persist_state).
        """
        super().__init__()
        if id is not None:
            self.id = id
        self.type = "tabs"
        self.tab_entries: List[Dict[str, Any]] = []
        self.props = dict(kwargs)
        if default_tab is not None:
            self.props["default_tab"] = default_tab
        if title is not None:
            self.props["title"] = title
        for tab in tabs or []:
            self._add_tab_entry(tab)

    def _add_tab_entry(self, tab: Any) -> None:
        """Normalizes a Tab shape (or equivalent dict) into a tab entry."""
        title = getattr(tab, "title", None) if not isinstance(tab, dict) else tab.get("title")
        children = getattr(tab, "children", None) if not isinstance(tab, dict) else tab.get("children")
        layout = getattr(tab, "layout", None) if not isinstance(tab, dict) else tab.get("layout")

        if layout is not None:
            if hasattr(layout, "to_dict"):
                layout.parent = self
            self.tab_entries.append({"title": title, "layout": layout})
        elif children is not None:
            entry_layout = Layout("row")
            entry_layout.parent = self
            for child in children:
                entry_layout.add(child)
            self.tab_entries.append({"title": title, "layout": entry_layout})
        else:
            raise ValueError(f"Tab '{title}' needs children or a layout.")

    def add_tab(self, title: str, direction: str = "column", **kwargs) -> Layout:
        """
        Adds a tab and returns its content layout.

        Args:
            title (str): The tab label.
            direction (str, optional): Layout direction for the tab's content
                ('row', 'column', or 'grid'). Defaults to "column".
            **kwargs: Additional layout properties (gap, wrap, align, columns, etc.).

        Returns:
            Layout: The tab's content layout — add visuals/layouts to it as usual.
        """
        layout = Layout(direction, **kwargs)
        layout.parent = self
        self.tab_entries.append({"title": title, "layout": layout})
        return layout

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the tab group and its tabs to a JSON-ready dict."""
        d: Dict[str, Any] = {
            "type": "tabs",
            "elementType": "visual",
            "id": self.id,
            "tabs": [
                {
                    "title": entry["title"],
                    "layout": entry["layout"].to_dict()
                    if hasattr(entry["layout"], "to_dict")
                    else entry["layout"],
                }
                for entry in self.tab_entries
            ],
        }
        for k, v in self.props.items():
            camel_k = snake_to_camel(k)
            if isinstance(v, dict):
                d[camel_k] = camel_case_dict(v)
            elif isinstance(v, list):
                d[camel_k] = [camel_case_dict(i) if isinstance(i, dict) else i for i in v]
            else:
                d[camel_k] = v
        return d
