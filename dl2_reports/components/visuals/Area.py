from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..visual import Visual


class AreaVisual:

    class Threshold:
        """Legacy threshold config object. Prefer :class:`dl2_reports.Threshold`."""

        def __init__(self,
                     value: float | int,
                     pass_color: Optional[str] = None,
                     fail_color: Optional[str] = None,
                     mode: str = "above",
                     show_line: bool = True,
                     line_style: str = "dashed",
                     blend_width: int = 5,
                     apply_to: str = "both"
            ):
            self.value = value
            self.pass_color = pass_color
            self.fail_color = fail_color
            self.mode = mode
            self.show_line = show_line
            self.line_style = line_style
            self.blend_width = blend_width
            self.apply_to = apply_to

        def to_dict(self) -> Dict[str, Any]:
            # Construct dictionary with snake_case keys which will be
            # automatically converted to camelCase during serialization
            d: Dict[str, Any] = {
                "value": self.value,
                "mode": self.mode,
                "show_line": self.show_line,
                "line_style": self.line_style,
                "blend_width": self.blend_width,
                "apply_to": self.apply_to
            }
            if self.pass_color is not None:
                d["pass_color"] = self.pass_color
            if self.fail_color is not None:
                d["fail_color"] = self.fail_color
            return d

    # Mixin assumes parent class provides the add_component hook
    def add_component(self, cls: type, *args, **kwargs) -> Optional["Visual"]: ...

    def add_area(self, *args, **kwargs) -> Optional[Visual]:
        """Adds an area chart. Legacy helper — see :class:`dl2_reports.Area` for the
        typed parameter reference; unknown kwargs pass through for compatibility."""
        from ..visual_components import Area

        return self.add_component(Area, *args, **kwargs)
