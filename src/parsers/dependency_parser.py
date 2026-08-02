from __future__ import annotations

import json
import re

from src.models.analysis_models import (
    DependencyItem,
    RepositoryFile,
)


def parse_package_json(
    file: RepositoryFile,
) -> list[DependencyItem]:
    try:
        payload = json.loads(file.content)
    except json.JSONDecodeError:
        return []

    results = []

    for section in (
        "dependencies",
        "devDependencies",
        "peerDependencies",
    ):
        for name, version in payload.get(section, {}).items():
            results.append(
                DependencyItem(
                    name=name,
                    version=str(version),
                    dependency_type=section,
                    source_file=file.path,
                )
            )

    return results


def parse_requirements(
    file: RepositoryFile,
) -> list[DependencyItem]:
    results = []

    for line in file.content.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        match = re.split(r"==|>=|<=|~=|>|<", line, maxsplit=1)

        results.append(
            DependencyItem(
                name=match[0].strip(),
                version=match[1].strip()
                if len(match) > 1
                else None,
                dependency_type="dependency",
                source_file=file.path,
            )
        )

    return results


def discover_dependencies(
    files: list[RepositoryFile],
) -> list[DependencyItem]:
    results = []

    for file in files:
        if file.name == "package.json":
            results.extend(parse_package_json(file))
        elif file.name == "requirements.txt":
            results.extend(parse_requirements(file))

    return results