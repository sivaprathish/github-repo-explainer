from __future__ import annotations

import re
from typing import Any


def parse_typescript(content: str) -> dict[str, Any]:
    imports = re.findall(
        r'import\s+.*?\s+from\s+["\']([^"\']+)["\']',
        content,
    )

    classes = re.findall(
        r'\bclass\s+([A-Za-z_][A-Za-z0-9_]*)',
        content,
    )

    functions = re.findall(
        r'\b(?:function|async\s+function)\s+'
        r'([A-Za-z_][A-Za-z0-9_]*)',
        content,
    )

    return {
        "imports": imports,
        "classes": classes,
        "functions": functions,
    }