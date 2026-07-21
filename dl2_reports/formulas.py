"""Pandas-style datasource formulas, parsed with the stdlib ``ast`` module.

Anywhere a dataset is referenced as an input — a visual's ``dataset_id`` or
``report.add_derived_dataset(source=...)`` — the string may be a formula instead
of a plain dataset name::

    "sales"                                   # plain dataset id (unchanged)
    "sales[Amount > 200]"                     # boolean filter
    "sales[Region == 'West' and Amount > 0]"  # and/or/not (or pandas-style &, |, ~)
    "sales[['Region', 'Amount']]"             # double-bracket column projection
    "sales[Amount > 200][['Region']]"         # chains compose; filters AND together

A formula compiles at construction time to the real dataset id plus the standard
filter grammar (see :mod:`dl2_reports.filters`) and, for projections, a
``columns`` list — nothing new reaches the report JSON.

Column references inside the brackets are bare names (``Amount``), attribute
style (``sales.amount``), or subscript style for non-identifier column names
(``sales["Due Date"]``). Supported comparison forms mirror pandas/`df.query`:
``== != > >= < <= in/not in``, ``lo <= Col <= hi`` (→ ``between``),
``is None``/``== None`` (→ ``isNull``), and the methods ``.contains()``,
``.startswith()``, ``.endswith()``, ``.isin()``, ``.between()``, ``.isnull()`` /
``.isna()``, ``.notnull()`` / ``.notna()`` (an intermediate ``.str`` is allowed).

Anything else — arithmetic, calls on non-columns, column-to-column comparisons,
variables — raises ``ValueError`` at construction time. As with pandas, ``&``
binds tighter than comparisons, so parenthesize: ``(Amount > 1) & (Units < 5)``.
"""

from __future__ import annotations

import ast
from typing import Any, List, NamedTuple, Optional, Tuple

from .filters import (
    FilterExpression,
    and_,
    not_,
    or_,
    validate_filter,
    where,
)


class DatasourceSpec(NamedTuple):
    """The result of parsing a datasource string.

    ``dataset_id`` is the resolved dataset name (or the original value verbatim
    when the input was not a formula); ``filter``/``columns`` are the compiled
    bracket expressions, or ``None``.
    """

    dataset_id: Any
    filter: Optional[FilterExpression] = None
    columns: Optional[List[str]] = None


def and_merge(
    formula_filter: Optional[FilterExpression],
    explicit_filter: Optional[FilterExpression],
) -> Optional[FilterExpression]:
    """Combines a formula-derived filter with an explicit ``filter=`` (formula first)."""
    if formula_filter is None:
        return explicit_filter
    if explicit_filter is None:
        return formula_filter
    return and_(formula_filter, explicit_filter)


# ast.parse emits ast.Index wrappers on Python 3.8 only; the class is deprecated
# on 3.9+ and slated for removal, so never name it directly.
_AST_INDEX = getattr(ast, "Index", None)

_COMPARE_OPS = {
    ast.Eq: "eq",
    ast.NotEq: "neq",
    ast.Gt: "gt",
    ast.GtE: "gte",
    ast.Lt: "lt",
    ast.LtE: "lte",
}
# Op to use when the column is on the right-hand side (200 < Amount → Amount > 200).
_FLIPPED_OPS = {"eq": "eq", "neq": "neq", "gt": "lt", "gte": "lte", "lt": "gt", "lte": "gte"}

# method name → (filter op, positional arg count)
_METHOD_OPS = {
    "contains": ("contains", 1),
    "startswith": ("startsWith", 1),
    "endswith": ("endsWith", 1),
    "isin": ("in", 1),
    "between": ("between", 2),
    "isnull": ("isNull", 0),
    "isna": ("isNull", 0),
    "notnull": ("notNull", 0),
    "notna": ("notNull", 0),
}

_NOT_A_VALUE = object()  # sentinel: distinguishes "not a literal" from a literal None


def _unwrap_slice(node: ast.AST) -> ast.AST:
    if _AST_INDEX is not None and isinstance(node, _AST_INDEX):
        return node.value
    return node


def parse_datasource(source: Any) -> DatasourceSpec:
    """Parses a datasource string, returning a :class:`DatasourceSpec`.

    Plain dataset ids (and any non-formula value, including ``None`` and legacy
    non-identifier ids like ``"my-data"``) pass through verbatim. A string
    containing ``[`` must be a valid ``dataset[...]`` formula or ``ValueError``
    is raised.
    """
    if not isinstance(source, str):
        return DatasourceSpec(source)
    if source.isidentifier() or "[" not in source:
        return DatasourceSpec(source)
    return _FormulaParser(source).parse()


class _FormulaParser:
    def __init__(self, source: str):
        self.source = source
        self.text = source.strip()

    def _err(self, message: str, node: Optional[ast.AST] = None) -> ValueError:
        segment = None
        if node is not None:
            try:
                segment = ast.get_source_segment(self.text, node)
            except Exception:
                segment = None
        at = f" (at '{segment}')" if segment else ""
        return ValueError(f"Invalid datasource formula '{self.source}': {message}{at}.")

    def parse(self) -> DatasourceSpec:
        try:
            tree = ast.parse(self.text, mode="eval")
        except SyntaxError as exc:
            raise ValueError(
                f"Invalid datasource formula '{self.source}': {exc.msg}."
            ) from None

        node = tree.body
        slices: List[ast.AST] = []
        while isinstance(node, ast.Subscript):
            slices.append(_unwrap_slice(node.slice))
            node = node.value
        if not isinstance(node, ast.Name) or not slices:
            raise self._err(
                "expected '<dataset>[...]' with a plain dataset name before the brackets"
            )
        self.dataset = node.id
        slices.reverse()  # left-to-right, as written

        filters: List[FilterExpression] = []
        columns: Optional[List[str]] = None
        for sl in slices:
            if isinstance(sl, ast.List):
                if columns is not None:
                    raise self._err("only one [[...]] column selection is allowed", sl)
                columns = self._projection(sl)
            elif isinstance(sl, ast.Constant) and isinstance(sl.value, str):
                raise self._err(
                    f"single-bracket column selection is not supported; use double "
                    f"brackets: {self.dataset}[['{sl.value}']]"
                )
            else:
                filters.append(self._condition(sl))

        combined = filters[0] if len(filters) == 1 else (and_(*filters) if filters else None)
        if combined is not None:
            validate_filter(combined)  # belt and braces: converter bugs fail here, not in the viewer
        return DatasourceSpec(self.dataset, combined, columns)

    # -- projection ------------------------------------------------------------

    def _projection(self, node: ast.List) -> List[str]:
        if not node.elts:
            raise self._err("[[...]] column selection needs at least one column", node)
        columns: List[str] = []
        for el in node.elts:
            if isinstance(el, ast.Constant) and isinstance(el.value, str):
                columns.append(el.value)
            elif isinstance(el, ast.Name):
                columns.append(el.id)
            else:
                raise self._err("[[...]] entries must be column names", el)
        return columns

    # -- boolean conditions ----------------------------------------------------

    def _condition(self, node: ast.AST) -> FilterExpression:
        if isinstance(node, ast.BoolOp):
            group = and_ if isinstance(node.op, ast.And) else or_
            return group(*[self._condition(v) for v in node.values])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.Not, ast.Invert)):
            return not_(self._condition(node.operand))
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.BitAnd, ast.BitOr)):
            group = and_ if isinstance(node.op, ast.BitAnd) else or_
            return group(*[self._condition(t) for t in self._flatten_binop(node, type(node.op))])
        if isinstance(node, ast.Compare):
            return self._compare(node)
        if isinstance(node, ast.Call):
            return self._method_call(node)
        raise self._err(
            "expected a boolean condition or a [[...]] column selection", node
        )

    def _flatten_binop(self, node: ast.AST, op_type: type) -> List[ast.AST]:
        if isinstance(node, ast.BinOp) and isinstance(node.op, op_type):
            return self._flatten_binop(node.left, op_type) + self._flatten_binop(node.right, op_type)
        return [node]

    def _compare(self, node: ast.Compare) -> FilterExpression:
        items = [node.left] + list(node.comparators)
        ops = node.ops

        # lo <= Col <= hi → between (inclusive, matching the viewer's semantics)
        if (
            len(ops) == 2
            and all(isinstance(op, ast.LtE) for op in ops)
            and self._column_of(items[1]) is not None
            and self._value_of(items[0]) is not _NOT_A_VALUE
            and self._value_of(items[2]) is not _NOT_A_VALUE
        ):
            column = self._column_of(items[1])
            return where(column, "between", values=[self._value_of(items[0]), self._value_of(items[2])])

        pairs = [self._pair(items[i], ops[i], items[i + 1]) for i in range(len(ops))]
        return pairs[0] if len(pairs) == 1 else and_(*pairs)

    def _pair(self, left: ast.AST, op_node: ast.AST, right: ast.AST) -> FilterExpression:
        if isinstance(op_node, (ast.In, ast.NotIn)):
            column = self._column_of(left)
            if column is None:
                raise self._err("'in' needs a column on the left-hand side", left)
            values = self._container_of(right)
            if values is _NOT_A_VALUE:
                raise self._err("'in' needs a list/tuple/set of literal values", right)
            return where(column, "in" if isinstance(op_node, ast.In) else "nin", values=values)

        if isinstance(op_node, (ast.Is, ast.IsNot)):
            column, other = self._column_and_other(left, right, op_node)
            if not (isinstance(other, ast.Constant) and other.value is None):
                raise self._err("'is' comparisons only support None", other)
            return where(column, "isNull" if isinstance(op_node, ast.Is) else "notNull")

        op = _COMPARE_OPS.get(type(op_node))
        if op is None:
            raise self._err(f"unsupported comparison operator '{type(op_node).__name__}'")

        left_col, right_col = self._column_of(left), self._column_of(right)
        if left_col is not None and right_col is not None:
            raise self._err("column-to-column comparisons are not supported", right)
        if left_col is None and right_col is None:
            raise self._err("comparison needs a column on one side", left)

        column = left_col if left_col is not None else right_col
        value_node = right if left_col is not None else left
        if left_col is None:
            op = _FLIPPED_OPS[op]

        value = self._value_of(value_node)
        if value is _NOT_A_VALUE:
            raise self._err("comparison value must be a literal", value_node)
        if value is None:
            if op == "eq":
                return where(column, "isNull")
            if op == "neq":
                return where(column, "notNull")
            raise self._err("None only supports ==/!= (or is/is not)", value_node)
        return where(column, op, value)

    def _column_and_other(self, left: ast.AST, right: ast.AST, op_node: ast.AST) -> Tuple[Any, ast.AST]:
        left_col = self._column_of(left)
        if left_col is not None:
            return left_col, right
        right_col = self._column_of(right)
        if right_col is not None:
            return right_col, left
        raise self._err("comparison needs a column on one side", left)

    def _method_call(self, node: ast.Call) -> FilterExpression:
        func = node.func
        if not isinstance(func, ast.Attribute):
            raise self._err("unsupported function call", node)
        method = func.attr
        receiver = func.value
        # tolerate pandas' .str accessor: Region.str.contains("W")
        if isinstance(receiver, ast.Attribute) and receiver.attr == "str":
            receiver = receiver.value
        column = self._column_of(receiver)
        if column is None:
            raise self._err(f"'.{method}()' must be called on a column", node)
        if method not in _METHOD_OPS:
            raise self._err(
                f"unsupported method '.{method}()'. Valid methods: {sorted(_METHOD_OPS)}"
            )
        if node.keywords:
            raise self._err(
                f"'.{method}()' does not accept keyword arguments (viewer string ops "
                f"are always case-insensitive)",
                node,
            )
        op, argc = _METHOD_OPS[method]
        if len(node.args) != argc:
            raise self._err(f"'.{method}()' takes exactly {argc} argument(s)", node)

        if op in ("isNull", "notNull"):
            return where(column, op)
        if op == "in":
            values = self._container_of(node.args[0])
            if values is _NOT_A_VALUE:
                raise self._err("'.isin()' needs a list/tuple/set of literal values", node.args[0])
            return where(column, "in", values=values)
        if op == "between":
            bounds = [self._value_of(a) for a in node.args]
            if any(b is _NOT_A_VALUE for b in bounds):
                raise self._err("'.between()' bounds must be literals", node)
            return where(column, "between", values=bounds)
        value = self._value_of(node.args[0])
        if value is _NOT_A_VALUE or value is None:
            raise self._err(f"'.{method}()' argument must be a literal", node.args[0])
        return where(column, op, value)

    # -- leaf helpers ----------------------------------------------------------

    def _column_of(self, node: ast.AST) -> Optional[str]:
        """Returns the column name if ``node`` is a column reference, else None."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id != self.dataset:
                return None
            return node.attr
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            if node.value.id != self.dataset:
                raise self._err(
                    f"column subscripts must use the dataset name "
                    f"('{self.dataset}[\"Col\"]'), got '{node.value.id}'",
                    node,
                )
            sl = _unwrap_slice(node.slice)
            if not (isinstance(sl, ast.Constant) and isinstance(sl.value, str)):
                raise self._err("column subscript must be a string literal", node)
            return sl.value
        return None

    def _value_of(self, node: ast.AST) -> Any:
        """Returns the literal value of ``node``, or the _NOT_A_VALUE sentinel."""
        if isinstance(node, ast.Constant):
            if node.value is None or isinstance(node.value, (str, int, float, bool)):
                return node.value
            return _NOT_A_VALUE
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            inner = self._value_of(node.operand)
            if isinstance(inner, (int, float)) and not isinstance(inner, bool):
                return -inner if isinstance(node.op, ast.USub) else inner
        return _NOT_A_VALUE

    def _container_of(self, node: ast.AST) -> Any:
        """Returns a list of literal values for a list/tuple/set node, else _NOT_A_VALUE."""
        if not isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return _NOT_A_VALUE
        values = []
        for el in node.elts:
            value = self._value_of(el)
            if value is _NOT_A_VALUE:
                return _NOT_A_VALUE
            values.append(value)
        return values
