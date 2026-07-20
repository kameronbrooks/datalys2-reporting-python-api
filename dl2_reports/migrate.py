"""Migrate dl2-reports scripts from the helper API (<=0.4.x style) to the v2 component API.

Rewrites calls like

    row.add_kpi("sales", value_column="Revenue", format="currency")

into

    row.add(KPI("sales", value_column="Revenue", format="currency"))

and upgrades known literal-dict props to typed shapes
(threshold= -> Threshold(...), total_row= -> TotalRow(...), default_sort= -> [SortSpec(...)], ...),
managing the `from dl2_reports import ...` line automatically.

Built on libcst so comments and formatting are preserved. The old helper API keeps working in
v2, so migration is optional and can be done file-by-file.

Usage:
    python -m dl2_reports.migrate PATH [PATH ...]          # dry run: print unified diffs
    python -m dl2_reports.migrate PATH [PATH ...] --write  # apply changes in place

Requires libcst:  pip install dl2-reports[migrate]

PATH may be a .py file, a .ipynb notebook, or a directory (recurses into *.py and *.ipynb).

Known limitations (left unchanged, still supported by the package):
    - generic add_visual("type", ...) calls
    - group_aggregates=/aggregates= dicts ('as' is a Python keyword; use the aggregates.agg builder)
    - dynamic patterns (helpers called via getattr, **kwargs splats, non-literal dicts)
    - notebook cells that fail to parse as pure Python (e.g. %magics) are skipped
"""

from __future__ import annotations

import argparse
import difflib
import json
import keyword
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple

try:
    import libcst as cst
except ImportError:  # pragma: no cover
    print(
        "This tool requires libcst (it preserves your comments and formatting).\n"
        "Install it with:  pip install dl2-reports[migrate]",
        file=sys.stderr,
    )
    sys.exit(1)


# Visual helper method -> v2 component class
HELPER_TO_CLASS = {
    "add_kpi": "KPI",
    "add_table": "Table",
    "add_card": "Card",
    "add_pie": "Pie",
    "add_bar": "Bar",
    "add_scatter": "Scatter",
    "add_line": "Line",
    "add_area": "Area",
    "add_checklist": "Checklist",
    "add_histogram": "Histogram",
    "add_heatmap": "Heatmap",
    "add_gauge": "Gauge",
    "add_boxplot": "Boxplot",
    "add_link": "Link",
    "add_modal_button": "ModalButton",
}

# Keyword props whose literal-dict values become typed shape constructors
DICT_PROP_TO_CLASS = {
    "threshold": "Threshold",
    "total_row": "TotalRow",
    "total_column": "TotalColumn",
}

# Keyword props holding a list of literal dicts, each becoming a shape constructor
LIST_PROP_TO_CLASS = {
    "default_sort": "SortSpec",
    "ranges": "GaugeRange",
}

# Dict keys whose values must stay plain dicts (data-keyed mappings, not props)
KEEP_DICT_KEYS = {"fns"}

_NO_SPACE_EQ = cst.AssignEqual(
    whitespace_before=cst.SimpleWhitespace(""),
    whitespace_after=cst.SimpleWhitespace(""),
)


def _dict_to_ctor(node: cst.Dict, class_name: str) -> Optional[cst.Call]:
    """Converts {"key": value, ...} to ClassName(key=value, ...).

    Returns None (leave unchanged) unless every key is a string literal that is a
    valid, non-keyword Python identifier.
    """
    args: List[cst.Arg] = []
    for element in node.elements:
        if not isinstance(element, cst.DictElement):
            return None
        key = element.key
        if not isinstance(key, cst.SimpleString):
            return None
        name = key.evaluated_value
        if not isinstance(name, str) or not name.isidentifier() or keyword.iskeyword(name):
            return None
        args.append(cst.Arg(keyword=cst.Name(name), value=element.value, equal=_NO_SPACE_EQ))
    return cst.Call(func=cst.Name(class_name), args=args)


class MigrateTransformer(cst.CSTTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.used_names: Set[str] = set()
        self.changed = False

    def _transform_shape_arg(self, arg: cst.Arg) -> cst.Arg:
        """Upgrades known literal-dict keyword args to shape constructors."""
        if arg.keyword is None or not isinstance(arg.keyword, cst.Name):
            return arg
        prop = arg.keyword.value
        if prop in KEEP_DICT_KEYS:
            return arg

        if prop in DICT_PROP_TO_CLASS and isinstance(arg.value, cst.Dict):
            ctor = _dict_to_ctor(arg.value, DICT_PROP_TO_CLASS[prop])
            if ctor is not None:
                self.used_names.add(DICT_PROP_TO_CLASS[prop])
                return arg.with_changes(value=ctor)

        if prop in LIST_PROP_TO_CLASS and isinstance(arg.value, (cst.List, cst.Tuple)):
            class_name = LIST_PROP_TO_CLASS[prop]
            new_elements = []
            for el in arg.value.elements:
                if not isinstance(el, cst.Element) or not isinstance(el.value, cst.Dict):
                    return arg  # mixed/non-literal content: leave the whole list alone
                ctor = _dict_to_ctor(el.value, class_name)
                if ctor is None:
                    return arg
                new_elements.append(el.with_changes(value=ctor))
            self.used_names.add(class_name)
            return arg.with_changes(value=arg.value.with_changes(elements=new_elements))

        return arg

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.Call:
        func = updated_node.func
        if not isinstance(func, cst.Attribute) or not isinstance(func.attr, cst.Name):
            return updated_node
        class_name = HELPER_TO_CLASS.get(func.attr.value)
        if class_name is None:
            return updated_node

        ctor_args = [self._transform_shape_arg(a) for a in updated_node.args]
        ctor = cst.Call(func=cst.Name(class_name), args=ctor_args)
        self.used_names.add(class_name)
        self.changed = True
        return updated_node.with_changes(
            func=func.with_changes(attr=cst.Name("add")),
            args=[cst.Arg(value=ctor)],
        )


def _is_dl2_import(node: cst.CSTNode) -> bool:
    return (
        isinstance(node, cst.SimpleStatementLine)
        and len(node.body) == 1
        and isinstance(node.body[0], cst.ImportFrom)
        and isinstance(node.body[0].module, cst.Name)
        and node.body[0].module.value == "dl2_reports"
        and not isinstance(node.body[0].names, cst.ImportStar)
    )


def _inject_imports(module: cst.Module, needed: Set[str]) -> cst.Module:
    """Ensures `from dl2_reports import ...` covers all needed names."""
    if not needed:
        return module

    body = list(module.body)

    for i, stmt in enumerate(body):
        if _is_dl2_import(stmt):
            import_from = stmt.body[0]
            existing = {
                alias.name.value
                for alias in import_from.names
                if isinstance(alias.name, cst.Name)
            }
            missing = sorted(needed - existing)
            if not missing:
                return module
            aliases = [
                alias.with_changes(comma=cst.Comma(whitespace_after=cst.SimpleWhitespace(" ")))
                for alias in import_from.names
            ]
            aliases += [
                cst.ImportAlias(
                    name=cst.Name(name),
                    comma=cst.Comma(whitespace_after=cst.SimpleWhitespace(" ")),
                )
                for name in missing
            ]
            aliases[-1] = aliases[-1].with_changes(comma=cst.MaybeSentinel.DEFAULT)
            body[i] = stmt.with_changes(body=[import_from.with_changes(names=aliases)])
            return module.with_changes(body=body)

    # No dl2_reports import found: insert one after the last top-level import
    new_import = cst.parse_statement(f"from dl2_reports import {', '.join(sorted(needed))}\n")
    insert_at = 0
    for i, stmt in enumerate(body):
        if isinstance(stmt, cst.SimpleStatementLine) and all(
            isinstance(s, (cst.Import, cst.ImportFrom)) for s in stmt.body
        ):
            insert_at = i + 1
    body.insert(insert_at, new_import)
    return module.with_changes(body=body)


def transform_source(source: str) -> Tuple[str, bool]:
    """Transforms one Python source string. Returns (new_source, changed)."""
    module = cst.parse_module(source)
    transformer = MigrateTransformer()
    module = module.visit(transformer)
    if not transformer.changed:
        return source, False
    module = _inject_imports(module, transformer.used_names)
    return module.code, True


def transform_notebook(raw: str) -> Tuple[str, bool, List[str]]:
    """Transforms a .ipynb JSON string. Returns (new_json, changed, warnings)."""
    nb = json.loads(raw)
    changed = False
    warnings: List[str] = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        src = "".join(cell.get("source", []))
        if not src.strip():
            continue
        try:
            new_src, cell_changed = transform_source(src)
        except cst.ParserSyntaxError:
            if any(m in src for m in HELPER_TO_CLASS):
                warnings.append(f"cell {i}: could not parse (magics?); skipped")
            continue
        if cell_changed:
            cell["source"] = new_src.splitlines(keepends=True)
            changed = True
    if not changed:
        return raw, False, warnings
    return json.dumps(nb, indent=1, ensure_ascii=False) + "\n", True, warnings


def _collect_files(paths: List[str]) -> List[Path]:
    files: List[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
            files.extend(sorted(path.rglob("*.ipynb")))
        elif path.exists():
            files.append(path)
        else:
            print(f"warning: {path} does not exist, skipping", file=sys.stderr)
    return files


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate dl2-reports scripts/notebooks to the v2 component API.",
        epilog=__doc__.split("Known limitations")[1].join(["Known limitations", ""]),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("paths", nargs="+", help=".py / .ipynb files or directories")
    parser.add_argument("--write", action="store_true", help="apply changes in place (default: print diff)")
    args = parser.parse_args(argv)

    any_changed = False
    for file in _collect_files(args.paths):
        original = file.read_text(encoding="utf-8")
        warnings: List[str] = []
        try:
            if file.suffix == ".ipynb":
                new_content, changed, warnings = transform_notebook(original)
            else:
                new_content, changed = transform_source(original)
        except cst.ParserSyntaxError as e:
            print(f"error: {file}: could not parse ({e.message.splitlines()[0]})", file=sys.stderr)
            continue

        for w in warnings:
            print(f"warning: {file}: {w}", file=sys.stderr)
        if not changed:
            continue
        any_changed = True

        if args.write:
            file.write_text(new_content, encoding="utf-8")
            print(f"migrated: {file}")
        else:
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=str(file),
                tofile=f"{file} (migrated)",
            )
            sys.stdout.writelines(diff)

    if not any_changed:
        print("nothing to migrate")
    elif not args.write:
        print("\n(dry run — re-run with --write to apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
