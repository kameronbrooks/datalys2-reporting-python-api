from __future__ import annotations

from typing import Dict, List, Optional

from .base import ReportTreeComponent
from .layout import Layout


class Page(ReportTreeComponent):
    """
    Represents a page in the report.
    """
    def __init__(self, title: str, description: Optional[str] = None):
        """
        Initializes a new Page.

        Args:
            title (str): The title of the page.
            description (str, optional): A description for the page. Defaults to None.
        """
        super().__init__()
        self.title = title
        self.description = description
        self.rows: List[Layout] = []

    def add_row(self, direction: str = "row", **kwargs) -> Layout:
        """
        Adds a layout row to the page.

        Args:
            direction (str, optional): The flexbox direction of the row ('row' or 'column'). Defaults to "row".
            **kwargs: Additional properties for the layout.

        Returns:
            Layout: The newly created Layout instance.
        """
        row = Layout(direction, **kwargs)
        row.parent = self
        self.rows.append(row)
        return row

    def to_dict(self) -> Dict[str, object]:
        """
        Converts the page to a dictionary for serialization.

        Returns:
            Dict[str, object]: The dictionary representation of the page.
        """
        d: Dict[str, object] = {
            "title": self.title,
            "rows": [r.to_dict() for r in self.rows],
        }
        if self.description:
            d["description"] = self.description
        return d
