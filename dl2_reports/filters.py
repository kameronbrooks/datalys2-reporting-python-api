"""Builders for the dl2 0.3+ client-side filter grammar.

A filter expression is either a leaf condition::

    {"column": "region", "op": "eq", "value": "West"}

or a boolean group (``{"and": [...]}``, ``{"or": [...]}``, ``{"not": {...}}``), nested
arbitrarily. These helpers produce plain dicts and validate operator names eagerly —
the JS runtime only console-warns on an unknown op, so catching typos at build time
is much friendlier.

Filters can be used on any visual (``filter=...``) or on a derived dataset
(``report.add_derived_dataset(..., filter=...)``).

Example::

    from dl2_reports import filters as F

    row.add_table(
        "sales",
        filter=F.and_(F.eq("region", "West"), F.gte("amount", 1000)),
    )
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Union

FilterExpression = Dict[str, Any]

VALID_OPS = frozenset({
    "eq", "neq", "gt", "gte", "lt", "lte",
    "in", "nin", "contains", "startsWith", "endsWith",
    "between", "isNull", "notNull",
})

_VALUELESS_OPS = frozenset({"isNull", "notNull"})

Column = Union[str, int]


def where(column: Column, op: str, value: Any = None, values: Sequence[Any] | None = None) -> FilterExpression:
    """Builds a leaf filter condition.

    Args:
        column: Column name (or integer column index).
        op: One of ``eq, neq, gt, gte, lt, lte, in, nin, contains, startsWith,
            endsWith, between, isNull, notNull``.
        value: Scalar comparison value (or ``[low, high]`` for ``between``).
        values: List of values for ``in``/``nin``/``between``.

    Raises:
        ValueError: If ``op`` is not a valid filter operator.
    """
    if op not in VALID_OPS:
        raise ValueError(f"Invalid filter op '{op}'. Valid ops: {sorted(VALID_OPS)}")
    condition: FilterExpression = {"column": column, "op": op}
    if value is not None:
        condition["value"] = value
    if values is not None:
        condition["values"] = list(values)
    if op not in _VALUELESS_OPS and value is None and values is None:
        raise ValueError(f"Filter op '{op}' requires a value (or values).")
    return condition


def and_(*expressions: FilterExpression) -> FilterExpression:
    """Combines expressions with logical AND."""
    return {"and": list(expressions)}


def or_(*expressions: FilterExpression) -> FilterExpression:
    """Combines expressions with logical OR."""
    return {"or": list(expressions)}


def not_(expression: FilterExpression) -> FilterExpression:
    """Negates an expression."""
    return {"not": expression}


# Shorthand builders for each operator

def eq(column: Column, value: Any) -> FilterExpression:
    """column == value"""
    return where(column, "eq", value)


def neq(column: Column, value: Any) -> FilterExpression:
    """column != value"""
    return where(column, "neq", value)


def gt(column: Column, value: Any) -> FilterExpression:
    """column > value (numeric/date aware)"""
    return where(column, "gt", value)


def gte(column: Column, value: Any) -> FilterExpression:
    """column >= value (numeric/date aware)"""
    return where(column, "gte", value)


def lt(column: Column, value: Any) -> FilterExpression:
    """column < value (numeric/date aware)"""
    return where(column, "lt", value)


def lte(column: Column, value: Any) -> FilterExpression:
    """column <= value (numeric/date aware)"""
    return where(column, "lte", value)


def isin(column: Column, values: Sequence[Any]) -> FilterExpression:
    """column value is in the list"""
    return where(column, "in", values=values)


def notin(column: Column, values: Sequence[Any]) -> FilterExpression:
    """column value is not in the list"""
    return where(column, "nin", values=values)


def contains(column: Column, value: str) -> FilterExpression:
    """case-insensitive substring match"""
    return where(column, "contains", value)


def starts_with(column: Column, value: str) -> FilterExpression:
    """case-insensitive prefix match"""
    return where(column, "startsWith", value)


def ends_with(column: Column, value: str) -> FilterExpression:
    """case-insensitive suffix match"""
    return where(column, "endsWith", value)


def between(column: Column, low: Any, high: Any) -> FilterExpression:
    """low <= column <= high (inclusive; date aware)"""
    return where(column, "between", values=[low, high])


def is_null(column: Column) -> FilterExpression:
    """column is null/undefined/empty-string"""
    return where(column, "isNull")


def not_null(column: Column) -> FilterExpression:
    """column has a non-null value"""
    return where(column, "notNull")


def validate_filter(expression: Any) -> None:
    """Recursively validates a filter expression dict (shape and operator names).

    Accepts hand-written dicts as well as builder output. Raises ValueError on problems.
    """
    if not isinstance(expression, dict):
        raise ValueError(f"Filter expression must be a dict, got {type(expression).__name__}.")

    group_keys = [k for k in ("and", "or", "not") if k in expression]
    if group_keys:
        if len(expression) != 1:
            raise ValueError(f"Filter group must have exactly one key, got {sorted(expression)}.")
        key = group_keys[0]
        if key == "not":
            validate_filter(expression["not"])
        else:
            children = expression[key]
            if not isinstance(children, list) or not children:
                raise ValueError(f"Filter group '{key}' must be a non-empty list.")
            for child in children:
                validate_filter(child)
        return

    if "column" not in expression or "op" not in expression:
        raise ValueError(f"Filter condition must have 'column' and 'op' keys, got {sorted(expression)}.")
    if expression["op"] not in VALID_OPS:
        raise ValueError(f"Invalid filter op '{expression['op']}'. Valid ops: {sorted(VALID_OPS)}")
