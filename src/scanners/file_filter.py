from __future__ import annotations

from pathlib import Path


EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    ".angular",
    ".cache",
    ".gradle",
    "dist",
    "build",
    "coverage",
    "target",
    "vendor",
    "out",
    "bin",
    "obj",
}

EXCLUDED_FILES = {
    ".env",
    "credentials.json",
    "secrets.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "uv.lock",
}

IMPORTANT_FILES = {
    "README",
    "README.md",
    "README.rst",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "angular.json",
    "vite.config.js",
    "vite.config.ts",
    "next.config.js",
    "next.config.ts",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Makefile",
    ".env.example",
    "manage.py",
    "main.py",
    "app.py",
    "server.py",
    "index.js",
    "index.ts",
    "main.js",
    "main.ts",
}

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".go",
    ".rs",
    ".cs",
    ".c",
    ".cpp",
    ".h",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".graphql",
    ".gql",
}

CONFIG_EXTENSIONS = {
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".xml",
}

MAX_FILE_SIZE = 300_000
MAX_SOURCE_FILES = 250


def is_excluded_path(
    root: Path,
    file_path: Path,
) -> bool:
    relative_path = file_path.relative_to(root)

    return any(
        part in EXCLUDED_DIRECTORIES
        for part in relative_path.parts
    )


def calculate_file_priority(file_path: Path) -> int:
    """
    Lower values have higher priority.
    """

    name = file_path.name
    path_text = file_path.as_posix().lower()

    if name in IMPORTANT_FILES:
        return 0

    if any(
        section in path_text
        for section in (
            "/src/",
            "/app/",
            "/api/",
            "/routes/",
            "/services/",
            "/controllers/",
            "/models/",
            "/components/",
            "/config/",
            "/tests/",
        )
    ):
        return 1

    if file_path.suffix.lower() in SOURCE_EXTENSIONS:
        return 2

    if file_path.suffix.lower() in CONFIG_EXTENSIONS:
        return 3

    return 10


def should_read_file(
    root: Path,
    file_path: Path,
) -> bool:
    if not file_path.is_file():
        return False

    if is_excluded_path(root, file_path):
        return False

    if file_path.name in EXCLUDED_FILES:
        return False

    try:
        size = file_path.stat().st_size
    except OSError:
        return False

    if size == 0 or size > MAX_FILE_SIZE:
        return False

    if file_path.name in IMPORTANT_FILES:
        return True

    suffix = file_path.suffix.lower()

    return (
        suffix in SOURCE_EXTENSIONS
        or suffix in CONFIG_EXTENSIONS
    )