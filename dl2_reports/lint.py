"""Compile-time prop lint.

Mirrors the JS runtime's config validation philosophy on the Python side: at
``compile()`` the report tree is checked for props the known visual types don't
model, and issues are emitted as warnings (never blocking) — or raised when
``compile(strict=True)``.

What gets flagged:
- Legacy helper calls whose unknown kwargs were routed into the component's
  passthrough (e.g. ``add_table(..., pagesize=20)``) — the classic silent typo.
- Generic ``add_visual(type, ...)`` calls whose type matches a known component
  but whose props don't.
- Layout kwargs that the viewer doesn't read (e.g. ``colums=2``).

Explicit ``extra={...}`` on a typed component is an intentional opt-out and is
never flagged. Comparison is camelCase-insensitive: ``page_size`` and
``pageSize`` are both accepted spellings of a known prop.
"""

from __future__ import annotations

import difflib
from typing import Any, Dict, List, Optional, Set

from .components.component import VisualComponent
from .components.layout import Layout
from .components.tabs import Tabs
from .components.visual import Visual
from .components import visual_components as _vc
from .serialization import snake_to_camel

# Layout props the viewer reads (camelCase), incl. common element props.
_LAYOUT_PROPS = {
    "direction", "columns", "gap", "wrap", "align", "justify", "minChildWidth",
    "flex", "margin", "padding", "border", "shadow", "title", "height", "width",
    "modalId", "id",
}

# Visual props that are structural rather than modeled fields.
_STRUCTURAL = {"id", "type", "elementType", "datasetId"}


def _component_registry() -> Dict[str, type]:
    registry: Dict[str, type] = {}
    for name in dir(_vc):
        cls = getattr(_vc, name)
        if isinstance(cls, type) and issubclass(cls, VisualComponent) and cls is not VisualComponent:
            registry[cls.TYPE] = cls
    registry["stackedBar"] = _vc.Bar
    return registry


def _known_camel(cls: type) -> Set[str]:
    return {snake_to_camel(p) for p in cls.known_props()} | _STRUCTURAL


def _suggest(name: str, valid: Set[str]) -> str:
    match = difflib.get_close_matches(snake_to_camel(name), sorted(valid), n=1)
    return f" (did you mean '{match[0]}'?)" if match else ""


def lint_report(report: Any) -> List[str]:
    """Walks the report tree and returns human-readable prop issues (empty = clean)."""
    registry = _component_registry()
    issues: List[str] = []

    def check_props(label: str, cls: type, prop_names) -> None:
        valid = _known_camel(cls)
        for name in prop_names:
            if snake_to_camel(name) not in valid:
                issues.append(f"{label}: unknown prop '{name}'{_suggest(name, valid)}")

    def walk_visual(visual: Visual) -> None:
        label = f"{visual.type} '{visual.id}'"
        if isinstance(visual, VisualComponent):
            routed = getattr(visual, "_legacy_extra_keys", None)
            if routed:
                check_props(label, type(visual), routed)
        elif type(visual) is Visual:
            cls = registry.get(visual.type)
            if cls is not None:
                check_props(label, cls, visual.props.keys())

    def walk_layout(layout: Layout) -> None:
        label = f"layout '{layout.id}'"
        for name in layout.props:
            if snake_to_camel(name) not in _LAYOUT_PROPS:
                issues.append(f"{label}: unknown layout prop '{name}'{_suggest(name, _LAYOUT_PROPS)}")
        for child in layout.children:
            walk_child(child)

    def walk_child(child: Any) -> None:
        if isinstance(child, Layout):
            walk_layout(child)
        elif isinstance(child, Tabs):
            for entry in child.tab_entries:
                if hasattr(entry.get("layout"), "children"):
                    walk_layout(entry["layout"])
        elif isinstance(child, Visual):
            walk_visual(child)

    for page in report.pages:
        for row in page.rows:
            walk_layout(row)
    for modal in report.modals:
        for row in modal.rows:
            walk_layout(row)

    return issues
