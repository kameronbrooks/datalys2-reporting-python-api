"""Typed shapes for structured visual props (dl2 v2 API).

These small dataclasses replace hand-written dicts for props like ``threshold=`` and
``total_row=``. Plain dicts remain accepted everywhere — shapes are validated sugar:

    Line("sales", x_column="Month", y_columns=["Revenue"],
         threshold=Threshold(value=5000, mode="above"))

Each shape serializes via ``to_dict()`` (the prop serializer calls it automatically),
mapping field names to the viewer's camelCase keys and dropping ``None`` values.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional, Union

from .aggregates import VALID_FNS
from .serialization import RawDict, snake_to_camel

Column = Union[str, int]


@dataclass
class Shape:
    """Base: serializes non-None fields with snake→camel keys.

    Class-level overrides:
        KEY_OVERRIDES: field name → serialized key (for Python keywords like ``from``).
        RAW_KEYS: fields whose dict values keep their keys verbatim (data-keyed maps).
    """

    KEY_OVERRIDES: ClassVar[Dict[str, str]] = {}
    RAW_KEYS: ClassVar[frozenset] = frozenset()

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)
            if value is None:
                continue
            key = self.KEY_OVERRIDES.get(f.name, snake_to_camel(f.name))
            if f.name in self.RAW_KEYS and isinstance(value, dict):
                value = RawDict(value)
            d[key] = value
        return d


@dataclass
class Threshold(Shape):
    """Pass/fail coloring for line, area, and clusteredBar visuals.

    Args:
        value: The threshold value to compare against.
        pass_color / fail_color: Colors for passing/failing values.
        mode: 'above' (default in viewer), 'below', or 'equals'.
        show_line: Whether to draw a reference line at the threshold.
        line_style: 'solid', 'dashed', or 'dotted'.
        blend_width: Gradient blend zone width in % of chart width (line/area).
        apply_to: 'both', 'markers', or 'lines'.
    """

    value: float
    pass_color: Optional[str] = None
    fail_color: Optional[str] = None
    mode: Optional[str] = None
    show_line: Optional[bool] = None
    line_style: Optional[str] = None
    blend_width: Optional[float] = None
    apply_to: Optional[str] = None

    def __post_init__(self):
        if self.mode is not None and self.mode not in ("above", "below", "equals"):
            raise ValueError(f"Threshold.mode must be 'above', 'below', or 'equals', got '{self.mode}'.")
        if self.apply_to is not None and self.apply_to not in ("both", "markers", "lines"):
            raise ValueError(f"Threshold.apply_to must be 'both', 'markers', or 'lines', got '{self.apply_to}'.")


@dataclass
class SortSpec(Shape):
    """One entry of a table's ``default_sort`` (multi-sort priority = list order)."""

    column: Column
    direction: str = "asc"

    def __post_init__(self):
        if self.direction not in ("asc", "desc"):
            raise ValueError(f"SortSpec.direction must be 'asc' or 'desc', got '{self.direction}'.")


@dataclass
class TotalRow(Shape):
    """A table's grand-total row (dl2 0.4+). ``fns`` maps column name → aggregate fn;
    keys are column names and are serialized verbatim."""

    RAW_KEYS = frozenset({"fns"})

    label: Optional[str] = None
    fns: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.fns:
            for column, fn in self.fns.items():
                if fn not in VALID_FNS:
                    raise ValueError(
                        f"TotalRow.fns['{column}'] = '{fn}' is not a valid aggregate fn. "
                        f"Valid fns: {sorted(VALID_FNS)}"
                    )


@dataclass
class TotalColumn(Shape):
    """A table's per-row total column (dl2 0.4+)."""

    label: Optional[str] = None
    columns: Optional[List[str]] = None


@dataclass
class GaugeRange(Shape):
    """One colored range band of a gauge. ``from_``/``to`` serialize as ``from``/``to``."""

    KEY_OVERRIDES = {"from_": "from"}

    from_: float = 0
    to: float = 0
    color: Optional[str] = None
    label: Optional[str] = None
    show_plus: Optional[bool] = None


@dataclass
class AggregateColumn(Shape):
    """One aggregate output column (``{column, fn, as}``) for ``group_aggregates`` or
    aggregate specs. Equivalent to :func:`dl2_reports.aggregates.agg`."""

    KEY_OVERRIDES = {"as_": "as"}

    column: Column = ""
    fn: str = "sum"
    as_: Optional[str] = None

    def __post_init__(self):
        if self.fn not in VALID_FNS:
            raise ValueError(f"AggregateColumn.fn '{self.fn}' is not valid. Valid fns: {sorted(VALID_FNS)}")


@dataclass
class Tab(Shape):
    """One tab of a Tabs container: a title plus either ``children`` (list of
    components/layouts) or a full ``layout``."""

    title: str = ""
    children: Optional[List[Any]] = None
    layout: Optional[Any] = None


VALID_COLUMN_FORMATS = frozenset({"number", "currency", "percent", "date", "hms"})
VALID_CF_STYLES = frozenset({"success", "warning", "error", "info", "muted"})
VALID_CF_TARGETS = frozenset({"cell", "row"})


@dataclass
class ColumnFormat(Shape):
    """One entry of a table/checklist ``column_formats`` mapping (dl2 0.4.1+).

    Formatting is display-only: CSV export keeps raw values; clipboard copy
    matches the formatted view. A bare kind string (``"due": "date"``) is
    accepted in the mapping as shorthand for ``ColumnFormat("date")``.

    Args:
        format: 'number', 'currency', 'percent', 'date', or 'hms'.
            'percent' multiplies by 100 (store ratios like 0.42); 'hms' treats
            the value as seconds.
        digits: Decimal places (viewer defaults: currency 2, percent 1).
        symbol: Currency symbol when format is 'currency' (viewer default '$').
    """

    format: str = "number"
    digits: Optional[int] = None
    symbol: Optional[str] = None

    def __post_init__(self):
        if self.format not in VALID_COLUMN_FORMATS:
            raise ValueError(
                f"ColumnFormat.format '{self.format}' is not valid. "
                f"Valid formats: {sorted(VALID_COLUMN_FORMATS)}"
            )


@dataclass
class ConditionalFormat(Shape):
    """One conditional-format highlight rule for tables/checklists (dl2 0.4.1+).

    Rules are evaluated per data row against raw (unformatted) values; the first
    matching rule wins per target (one ``row`` rule and one ``cell`` rule can
    compose). Totals/aggregate rows are exempt.

    Args:
        when: Filter expression (standard filter grammar — build with the
            :mod:`dl2_reports.filters` helpers or a plain dict).
        target: 'cell' (default — styles the matching cell(s)) or 'row'.
        columns: Cell-target columns to style. Defaults to the ``when``
            condition's own column; required when ``when`` is a compound
            (``and``/``or``/``not``) expression.
        style: Named theme-aware preset: 'success', 'warning', 'error',
            'info', or 'muted'. (The viewer prop is ``style``, not ``preset``.)
        css: Inline CSS overrides layered over ``style``. Keys are camelCase
            React style names; snake_case keys are converted for you
            (``background_color`` → ``backgroundColor``).
    """

    when: Dict[str, Any] = None
    target: Optional[str] = None
    columns: Optional[List[str]] = None
    style: Optional[str] = None
    css: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.when:
            raise ValueError("ConditionalFormat requires a 'when' filter expression.")
        from .filters import validate_filter

        validate_filter(self.when)
        if self.target is not None and self.target not in VALID_CF_TARGETS:
            raise ValueError(
                f"ConditionalFormat.target must be one of {sorted(VALID_CF_TARGETS)}, got '{self.target}'."
            )
        if self.style is not None and self.style not in VALID_CF_STYLES:
            raise ValueError(
                f"ConditionalFormat.style '{self.style}' is not valid. "
                f"Valid styles: {sorted(VALID_CF_STYLES)}"
            )
        if self.style is None and not self.css:
            raise ValueError(
                "ConditionalFormat requires 'style' and/or 'css' (the viewer skips rules with neither)."
            )
        if self.target != "row" and self.columns is None and "column" not in self.when:
            raise ValueError(
                "ConditionalFormat with a compound 'when' expression needs explicit "
                "'columns' for cell targeting (or use target='row')."
            )
