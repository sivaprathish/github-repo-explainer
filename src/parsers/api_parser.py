from __future__ import annotations

import re

from src.models.analysis_models import APIRoute, RepositoryFile


API_PATTERNS = [
    (
        "FastAPI/Flask",
        re.compile(
            r'@\w+\.(get|post|put|patch|delete)'
            r'\(\s*["'']([^"'']+)["'']'
        ),
    ),
    (
        "Express",
        re.compile(
            r'\b(?:app|router)\.(get|post|put|patch|delete)'
            r'\(\s*["'']([^"'']+)["'']'
        ),
    ),
]


def discover_api_routes(
    files: list[RepositoryFile],
) -> list[APIRoute]:
    routes: list[APIRoute] = []

    for file in files:
        for framework, pattern in API_PATTERNS:
            for match in pattern.finditer(file.content):
                routes.append(
                    APIRoute(
                        method=match.group(1).upper(),
                        route=match.group(2),
                        file_path=file.path,
                        framework=framework,
                    )
                )

    return routes
