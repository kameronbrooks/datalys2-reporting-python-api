from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class GaugeVisual:

    class Range:
        """Legacy gauge range object. Prefer :class:`dl2_reports.GaugeRange`."""

        def __init__(self,
                     from_value: Optional[float] = None,
                     to_value: Optional[float] = None,
                     color: Optional[str] = None,
                     label: Optional[str] = None
            ):
            self.from_value = from_value
            self.to_value = to_value
            self.color = color
            self.label = label

        def to_dict(self) -> Dict[str, Any]:
            d = {}
            if self.from_value is not None:
                d["from"] = self.from_value
            if self.to_value is not None:
                d["to"] = self.to_value
            if self.color is not None:
                d["color"] = self.color
            if self.label is not None:
                d["label"] = self.label
            return d

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_gauge(self, *args, **kwargs) -> Optional[Visual]:
        """Adds a gauge visual. Legacy helper — see :class:`dl2_reports.Gauge`
        for the typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Gauge

        return self.add_component(Gauge, *args, **kwargs)
