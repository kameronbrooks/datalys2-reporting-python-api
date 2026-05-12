from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..serialization import camel_case_dict, snake_to_camel
from .base import ReportTreeComponent
from .visual import Visual

from .visuals import (
    KPIVisual,
    TableVisual,
    CardVisual,
    PieVisual,
    BarVisual,
    ScatterVisual,
    LineVisual,
    AreaVisual,
    ChecklistVisual,
    HistogramVisual,
    HeatmapVisual,
    GaugeVisual,
    BoxplotVisual,
)


class CompileTimeConditional(
    KPIVisual,
    TableVisual,
    CardVisual,
    PieVisual,
    BarVisual,
    ScatterVisual,
    LineVisual,
    AreaVisual,
    ChecklistVisual,
    HistogramVisual,
    HeatmapVisual,
    GaugeVisual,
    BoxplotVisual,
    ):
    """
    Temporary wrapper returned by ``Layout.on_condition()``.
    When the condition is True, delegates all ``add_*`` calls to the parent layout.
    When the condition is False, returns a :class:`NullVisual` sentinel that safely
    absorbs any further chained method calls (e.g. ``.add_trend()``).

    Does **not** inherit from :class:`ReportTreeComponent` and does not consume an
    element ID, so it has no effect on the ID sequence of the compiled report.
    """

    def __init__(self, parent: Layout, condition: bool):
        # Intentionally not calling super().__init__() — this is not a real tree
        # node and must not consume a BASE_ID slot.
        self.parent = parent
        self.condition = condition

    def add_visual(self, type: str, dataset_id: Optional[str] = None, visual: Optional[Visual] = None, **kwargs) -> Optional[Visual]:
        if not self.condition:
            return None
        return self.parent.add_visual(type, dataset_id, visual=visual, **kwargs)



class Layout(
    ReportTreeComponent,
    KPIVisual,
    TableVisual,
    CardVisual,
    PieVisual,
    BarVisual,
    ScatterVisual,
    LineVisual,
    AreaVisual,
    ChecklistVisual,
    HistogramVisual,
    HeatmapVisual,
    GaugeVisual,
    BoxplotVisual,
    ):
    def __init__(self, direction: str = "row", **kwargs):
        """Initializes a new layout container.

        Layouts can contain other layouts and/or visuals and control how children
        are arranged.

        Args:
            direction: Layout direction ('row', 'column', or 'grid' depending on viewer support).
            **kwargs: Additional layout properties (serialized to JSON):
                padding, margin, border, shadow, flex, height, gap, columns, etc.
        """
        super().__init__()
        self.type = "layout"
        self.direction = direction
        self.children: List[Layout | Visual] = []
        self.props = kwargs

    def add_visual(self, type: str, dataset_id: Optional[str] = None, visual: Optional[Visual] = None, **kwargs) -> Optional[Visual]:
        """Adds a generic visual to the layout.

        Args:
            type: Visual type (e.g., 'kpi', 'table', 'line', 'scatter').
            dataset_id: Dataset id to bind to this visual.
            visual: An existing Visual instance to add to the layout.
            **kwargs: Visual properties (serialized to JSON). Common ones include:
                padding, margin, border, shadow, flex, modal_id.

        Returns:
            The created :class:`~dl2_reports.components.visual.Visual` instance.
        """
        if visual is None:
            visual = Visual(type, dataset_id, **kwargs)
        
        visual.parent = self
        self.children.append(visual)
        return visual
    
    def on_condition(self, condition: bool) -> CompileTimeConditional:
        """Returns a conditional wrapper for this layout that only adds visuals if the condition is True.

        Example usage:
            layout.on_condition(show_sales).add_bar(...)
        """
        return CompileTimeConditional(self, condition)
    
    
    def remove_visual(self, visual: Visual) -> None:
        """Removes a visual from the layout.

        Args:
            visual: The visual instance to remove.
        """
        if visual in self.children:
            self.children.remove(visual)
            visual.parent = None

    def add_layout(self, direction: str = "row", **kwargs) -> Layout:
        """Adds a nested layout to this layout.

        Args:
            direction: Layout direction for the nested layout.
            **kwargs: Additional layout properties.

        Returns:
            The created nested :class:`~dl2_reports.components.layout.Layout`.
        """
        layout = Layout(direction, **kwargs)
        layout.parent = self
        self.children.append(layout)
        return layout

    def add_modal_button(self, modal_id: str, button_label: str, **kwargs) -> Optional[Visual]:
        """Adds a modal trigger button.

        Args:
            modal_id: The global modal id to open.
            button_label: Button label text.
            **kwargs: Additional common visual properties.

        Returns:
            The created modal trigger visual.
        """
        return self.add_visual("modal", id=modal_id, button_label=button_label, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes this layout and its children to a JSON-ready dict."""
        d: Dict[str, Any] = {
            "type": "layout",
            "direction": self.direction,
            "children": [c.to_dict() for c in self.children],
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
