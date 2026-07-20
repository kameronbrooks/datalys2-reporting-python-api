from __future__ import annotations

from typing import Dict, List, Optional

from .base import ReportTreeComponent
from .layout import Layout


class Modal(ReportTreeComponent):
    """
    Represents a modal dialog in the report.
    """
    def __init__(self, id: str, title: str, description: Optional[str] = None):
        """
        Initializes a new Modal.

        Args:
            id (str): A unique identifier for the modal.
            title (str): The title of the modal.
            description (str, optional): A description for the modal. Defaults to None.
        """
        super().__init__()
        self.id = id
        self.title = title
        self.description = description
        self.rows: List[Layout] = []

    def add_row(self, *children, direction: str = "row", **kwargs) -> Layout:
        """
        Adds a layout row to the modal.

        Components may be passed directly (v2 style); a single leading string
        positional argument is treated as the layout direction (legacy).

        Args:
            *children: Optional components/layouts to add to the new row.
            direction (str, optional): The flexbox direction of the row ('row', 'column',
                or 'grid'). Defaults to "row".
            **kwargs: Additional properties for the layout.

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
        Converts the modal to a dictionary for serialization.

        Returns:
            Dict[str, object]: The dictionary representation of the modal.
        """
        d: Dict[str, object] = {
            "id": self.id,
            "title": self.title,
            "rows": [r.to_dict() for r in self.rows],
        }
        if self.description:
            d["description"] = self.description
        return d
