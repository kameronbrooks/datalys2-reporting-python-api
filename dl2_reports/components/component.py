"""Base class for the v2 typed component API.

A :class:`VisualComponent` is a :class:`~dl2_reports.components.visual.Visual` whose
constructor is a typed signature instead of a ``**kwargs`` bag. Concrete subclasses
(``KPI``, ``Table``, ...) declare their specific props explicitly and pass them to
``super().__init__``; common container props (``padding``, ``border``, ``flex``,
``modal_id``, ``filter``, ...) are accepted by every component and validated against
:data:`COMMON_PROPS`.

Strictness is the point: an unknown keyword raises ``TypeError`` at construction time
(the JS viewer silently ignores unknown props, which turns typos into invisible bugs).
Props that the viewer supports but this package does not model yet can always be passed
through explicitly via ``extra={...}``.
"""

from __future__ import annotations

import difflib
from typing import Any, ClassVar, Dict, FrozenSet, Optional

from .visual import Visual

# Container/behavior props every visual accepts (serialized like any other prop).
COMMON_PROPS: FrozenSet[str] = frozenset({
    "id",
    "title",
    "description",
    "padding",
    "margin",
    "border",
    "shadow",
    "flex",
    "width",
    "height",
    "modal_id",
    "filter",
    "aggregate",
    "persist_state",
})


class VisualComponent(Visual):
    """Base for typed visual components. Subclasses set ``TYPE`` and declare a typed
    ``__init__`` that forwards specific props as a dict."""

    TYPE: ClassVar[str] = ""

    def __init__(
        self,
        dataset_id: Optional[str] = None,
        specific: Optional[Dict[str, Any]] = None,
        extra: Optional[Dict[str, Any]] = None,
        **common: Any,
    ):
        """
        Args:
            dataset_id: Dataset id this visual is bound to (None for dataset-less visuals).
            specific: The subclass's own props (None values are dropped).
            extra: Explicit passthrough props not modeled by this class — serialized
                verbatim (snake_case keys are still camelCased).
            **common: Common visual props; must be members of :data:`COMMON_PROPS`.

        Raises:
            TypeError: On any keyword outside the component's declared surface.
        """
        unknown = set(common) - COMMON_PROPS
        if unknown:
            hints = []
            valid = sorted(COMMON_PROPS | set((specific or {}).keys()))
            for name in sorted(unknown):
                match = difflib.get_close_matches(name, valid, n=1)
                hints.append(f"'{name}'" + (f" (did you mean '{match[0]}'?)" if match else ""))
            raise TypeError(
                f"{type(self).__name__} got unknown prop(s): {', '.join(hints)}. "
                f"Use extra={{...}} to pass unmodeled viewer props through explicitly."
            )

        props: Dict[str, Any] = {k: v for k, v in (specific or {}).items() if v is not None}
        props.update({k: v for k, v in common.items() if v is not None})
        if extra:
            props.update(extra)

        super().__init__(self.TYPE, dataset_id, **props)

    @classmethod
    def known_props(cls) -> FrozenSet[str]:
        """All prop names this component models (specific + common). Used by the
        compile-time lint and the legacy-helper compatibility shim."""
        import inspect

        specific = {
            name
            for name in inspect.signature(cls.__init__).parameters
            if name not in ("self", "dataset_id", "specific", "extra", "common")
        }
        return frozenset(specific) | COMMON_PROPS


def split_legacy_kwargs(cls: type, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility shim for the legacy ``add_*`` helpers.

    The old helpers accepted arbitrary ``**kwargs`` passthrough; the typed constructors
    do not. This routes any kwarg the component doesn't model into ``extra`` so legacy
    call sites keep working unchanged.
    """
    known = cls.known_props() | {"dataset_id", "extra"}
    extra = dict(kwargs.pop("extra", None) or {})
    for key in [k for k in kwargs if k not in known]:
        extra[key] = kwargs.pop(key)
    if extra:
        kwargs["extra"] = extra
    return kwargs
