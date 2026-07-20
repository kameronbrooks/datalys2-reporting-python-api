from __future__ import annotations

from typing import Dict, List, Optional

from .base import ReportTreeComponent
from .layout import Layout


class Page(ReportTreeComponent):
    """
    Represents a page in the report.
    """
    def __init__(self, title: str, description: Optional[str] = None, last_updated: Optional[str] = None):
        """
        Initializes a new Page.

        Args:
            title (str): The title of the page.
            description (str, optional): A description for the page. Defaults to None.
            last_updated (str, optional): The last updated date for the page. Defaults to None.
        """
        super().__init__()
        self.title = title
        self.description = description
        self.last_updated = last_updated
        self.rows: List[Layout] = []

    def add_row(self, *children, direction: str = "row", **kwargs) -> Layout:
        """
        Adds a layout row to the page.

        Components may be passed directly (v2 style):
            page.add_row(KPI("sales", value_column="Revenue"), Card(title="Hi", text="..."))

        For backward compatibility, a single leading string positional argument is
        treated as the layout direction: ``page.add_row("column")``.

        Args:
            *children: Optional components/layouts to add to the new row.
            direction (str, optional): The flexbox direction of the row ('row', 'column',
                or 'grid'). Defaults to "row".
            **kwargs: Additional properties for the layout (gap, wrap, align, ...).

        Returns:
            Layout: The newly created Layout instance.
        """
        if children and isinstance(children[0], str):
            direction = children[0]
            children = children[1:]
        row = Layout(direction, **kwargs)
        row.parent = self
        self.rows.append(row)
        for child in children:
            row.add(child)
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
        if self.last_updated:
            d["lastUpdated"] = self.last_updated
        return d
