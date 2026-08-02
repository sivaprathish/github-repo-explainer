from __future__ import annotations

from src.models.analysis_models import RepositoryFile


ENTRYPOINT_NAMES = {
    "app.py",
    "main.py",
    "server.py",
    "manage.py",
    "index.js",
    "index.ts",
    "main.ts",
    "main.js",
    "app.js",
    "app.ts",
    "Dockerfile",
}


def detect_entrypoints(
    files: list[RepositoryFile],
) -> list[RepositoryFile]:
    return [
        file
        for file in files
        if file.name in ENTRYPOINT_NAMES
    ]