from __future__ import annotations

import ast
from typing import Any


def parse_python(content: str) -> dict[str, Any]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {
            "imports": [],
            "classes": [],
            "functions": [],
        }

    imports = []
    classes = []
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

        elif isinstance(node, ast.ClassDef):
            classes.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )

        elif isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                }
            )

    return {
        "imports": imports,
        "classes": classes,
        "functions": functions,
    }