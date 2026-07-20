from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..serialization import camel_case_dict, snake_to_camel
from .base import ReportTreeComponent
from .component import split_legacy_kwargs
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
    LinkVisual,
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
    LinkVisual,
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

    def add_tabs(self, id: Optional[str] = None, default_tab: Optional[int] = None, title: Optional[str] = None, **kwargs):
        if not self.condition:
            return None
        return self.parent.add_tabs(id=id, default_tab=default_tab, title=title, **kwargs)

    def add_layout(self, direction: str = "row", **kwargs) -> Optional[Layout]:
        if not self.condition:
            return None
        return self.parent.add_layout(direction, **kwargs)

    def add_component(self, cls: type, *args, **kwargs):
        if not self.condition:
            return None
        return self.parent.add_component(cls, *args, **kwargs)

    def add(self, child):
        if not self.condition:
            return None
        return self.parent.add(child)



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
    LinkVisual,
    ):
    def __init__(self, direction: str = "row", **kwargs):
        """Initializes a new layout container.

        Layouts can contain other layouts and/or visuals and control how children
        are arranged.

        Args:
            direction: Layout direction ('row', 'column', or 'grid').
            **kwargs: Additional layout properties (serialized to JSON):
                padding, margin, border, shadow, flex, height, gap, columns, title, etc.
                dl2 0.3+ adds: wrap (bool), align (CSS align-items),
                justify (CSS justify-content) for row/column layouts, and
                min_child_width (px or CSS size) for responsive grids.
        """
        super().__init__()
        self.type = "layout"
        self.direction = direction
        self.children: List[ReportTreeComponent] = []
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
    
    def add(self, child: ReportTreeComponent) -> ReportTreeComponent:
        """Adds a constructed component (visual, layout, or tabs container) to this
        layout and returns it — the v2 entry point.

        Example:
            row.add(KPI("sales", value_column="Revenue", format="currency"))
            row.add(Table("sales", group_by="Region")).add_element("yAxis", value=100)

        Args:
            child: Any report-tree component (e.g. a typed visual component, a
                Visual, a Layout, or a Tabs container).

        Returns:
            The added child, for chaining.
        """
        if not isinstance(child, ReportTreeComponent):
            raise TypeError(
                f"layout.add() expects a component (Visual/Layout/Tabs), got {type(child).__name__}."
            )
        child.parent = self
        self.children.append(child)
        return child

    def add_component(self, cls: type, *args, **kwargs):
        """Constructs a typed component and adds it to this layout.

        Used by the legacy ``add_*`` helpers; kwargs the component does not model are
        routed into its ``extra`` passthrough dict for backward compatibility.
        Direct v2 usage constructs the component itself and calls :meth:`add`.
        """
        comp = cls(*args, **split_legacy_kwargs(cls, dict(kwargs)))
        comp.parent = self
        self.children.append(comp)
        return comp

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

    def add_tabs(self, id: Optional[str] = None, default_tab: Optional[int] = None, title: Optional[str] = None, **kwargs):
        """Adds a tabs container visual (dl2 0.3+) to this layout.

        Example usage:
            tabs = row.add_tabs(id="sales-tabs")
            tabs.add_tab("Chart").add_bar("sales", x_column="Month", y_columns=["Revenue"])
            tabs.add_tab("Data").add_table("sales")

        Args:
            id: Stable id for the tab group (enables active-tab persistence in
                dl2 0.4+ and link/anchor targeting). Defaults to an auto id.
            default_tab: Index of the initially active tab.
            title: Optional title rendered above the tab strip.
            **kwargs: Additional container properties (padding, margin, border,
                shadow, flex, persist_state, ...).

        Returns:
            The created :class:`~dl2_reports.components.tabs.Tabs` container.
        """
        from .tabs import Tabs  # Local import to avoid a circular dependency

        tabs = Tabs(id=id, default_tab=default_tab, title=title, **kwargs)
        tabs.parent = self
        self.children.append(tabs)
        return tabs

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
