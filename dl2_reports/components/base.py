from __future__ import annotations

from typing import Any, Optional


class ReportTreeComponent:
    """Base class for components in the report tree."""
    BASE_ID: int = 1
    def __init__(self):
        self.id = f"elem-{ReportTreeComponent.BASE_ID}"
        ReportTreeComponent.BASE_ID += 1

        self.parent: Optional[Any] = None

    def to_dict(self) -> Any:
        """Serializes the component to a JSON-ready dict. Implemented by subclasses."""
        raise NotImplementedError

    def get_report(self) -> Any:
        """Walks up the parent chain to find the report."""

        if self.parent is None:
            raise ValueError("Component is not attached to a report.")
        if hasattr(self.parent, "get_report"):
            return self.parent.get_report()

        return None
