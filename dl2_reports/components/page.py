from __future__ import annotations

from typing import Dict, List, Optional

from .base import ReportTreeComponent
from .layout import Layout


class Page(ReportTreeComponent):
    def __init__(self, title: str, description: Optional[str] = None):
        super().__init__()
        self.title = title
        self.description = description
        self.rows: List[Layout] = []

    def add_row(self, direction: str = "row", **kwargs) -> Layout:
        row = Layout(direction, **kwargs)
        row.parent = self
        self.rows.append(row)
        return row

    def to_dict(self) -> Dict[str, object]:
        d: Dict[str, object] = {
            "title": self.title,
            "rows": [r.to_dict() for r in self.rows],
        }
        if self.description:
            d["description"] = self.description
        return d
