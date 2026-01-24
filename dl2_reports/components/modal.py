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

    def add_row(self, direction: str = "row", **kwargs) -> Layout:
        """
        Adds a layout row to the modal.

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
