"""Builders for the dl2 0.3+ client-side aggregation spec.

An aggregate spec groups rows and computes per-group aggregate columns::

    {
        "groupBy": ["region"],
        "aggregates": [{"column": "amount", "fn": "sum", "as": "total"}]
    }

When ``as`` is omitted the JS runtime names the output column ``"{fn}_{column}"``
(e.g. ``sum_amount``) — downstream visuals must reference that name.

Aggregates can be used on any visual (``aggregate=...``, applied after its ``filter``)
or on a derived dataset (``report.add_derived_dataset(..., aggregate=...)``).

Example::

    from dl2_reports import aggregates as A

    row.add_bar(
        "region_totals",
        x_column="region",
        y_columns=["total"],
        aggregate=A.aggregate("region", A.agg("amount", "sum", as_="total")),
    )
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Union

AggregateSpec = Dict[str, Any]

VALID_FNS = frozenset({
    "sum", "avg", "min", "max", "count", "countDistinct", "first", "last",
})

Column = Union[str, int]


def agg(column: Column, fn: str, as_: str | None = None) -> Dict[str, Any]:
    """Builds one aggregate column definition.

    Args:
        column: Column name (or integer index) to aggregate. Ignored by ``count``.
        fn: One of ``sum, avg, min, max, count, countDistinct, first, last``.
        as_: Optional output column name. Defaults (in the viewer) to ``"{fn}_{column}"``.

    Raises:
        ValueError: If ``fn`` is not a valid aggregate function.
    """
    if fn not in VALID_FNS:
        raise ValueError(f"Invalid aggregate fn '{fn}'. Valid fns: {sorted(VALID_FNS)}")
    definition: Dict[str, Any] = {"column": column, "fn": fn}
    if as_ is not None:
        definition["as"] = as_
    return definition


def aggregate(group_by: Column | Sequence[Column], *aggs: Dict[str, Any]) -> AggregateSpec:
    """Builds a full aggregate spec.

    Args:
        group_by: Column (or list of columns) to group by.
        *aggs: Aggregate column definitions from :func:`agg` (or equivalent dicts).

    Raises:
        ValueError: If no group-by columns or no aggregates are given.
    """
    if isinstance(group_by, (str, int)):
        group_by = [group_by]
    group_by = list(group_by)
    if not group_by:
        raise ValueError("aggregate() requires at least one group_by column.")
    if not aggs:
        raise ValueError("aggregate() requires at least one aggregate column (use agg()).")
    spec = {"groupBy": group_by, "aggregates": list(aggs)}
    validate_aggregate(spec)
    return spec


def validate_aggregate(spec: Any) -> None:
    """Validates an aggregate spec dict (shape and fn names). Raises ValueError on problems.

    Accepts hand-written dicts (snake_case ``group_by`` or camelCase ``groupBy``).
    """
    if not isinstance(spec, dict):
        raise ValueError(f"Aggregate spec must be a dict, got {type(spec).__name__}.")
    group_by = spec.get("groupBy", spec.get("group_by"))
    if not isinstance(group_by, list) or not group_by:
        raise ValueError("Aggregate spec requires a non-empty 'groupBy' list.")
    aggs = spec.get("aggregates")
    if not isinstance(aggs, list) or not aggs:
        raise ValueError("Aggregate spec requires a non-empty 'aggregates' list.")
    for definition in aggs:
        if not isinstance(definition, dict):
            raise ValueError("Each aggregate must be a dict like {'column', 'fn', 'as'?}.")
        fn = definition.get("fn")
        if fn not in VALID_FNS:
            raise ValueError(f"Invalid aggregate fn '{fn}'. Valid fns: {sorted(VALID_FNS)}")
        if "column" not in definition and fn != "count":
            raise ValueError(f"Aggregate fn '{fn}' requires a 'column'.")
