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
        **kwargs,
    ):
        """
        Initializes a new Tabs container.

        Args:
            id (str, optional): Stable id for the tab group (enables active-tab
                persistence and link/anchor targeting). Defaults to an auto id.
            default_tab (int, optional): Index of the initially active tab. Defaults to 0.
            title (str, optional): Optional title rendered above the tab strip.
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
                {"title": entry["title"], "layout": entry["layout"].to_dict()}
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
