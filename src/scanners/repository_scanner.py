from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from src.models.analysis_models import RepositoryFile
from src.scanners.file_filter import (
    MAX_SOURCE_FILES,
    calculate_file_priority,
    should_read_file,
)
from src.scanners.file_reader import read_file


MAX_FILE_READ_WORKERS = 8


def scan_repository(
    repo_path: str,
) -> list[RepositoryFile]:
    root = Path(repo_path)

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    candidate_paths: list[Path] = []

    for file_path in root.rglob("*"):
        try:
            if should_read_file(root, file_path):
                candidate_paths.append(file_path)
        except (OSError, ValueError):
            continue

    candidate_paths.sort(
        key=lambda path: (
            calculate_file_priority(path),
            path.stat().st_size,
            path.as_posix().lower(),
        )
    )

    selected_paths = candidate_paths[:MAX_SOURCE_FILES]

    files: list[RepositoryFile] = []

    with ThreadPoolExecutor(
        max_workers=MAX_FILE_READ_WORKERS
    ) as executor:
        futures = {
            executor.submit(
                read_file,
                root,
                file_path,
            ): file_path
            for file_path in selected_paths
        }

        for future in as_completed(futures):
            try:
                repository_file = future.result()
            except OSError:
                continue

            if repository_file is not None:
                files.append(repository_file)

    return sorted(
        files,
        key=lambda file: (
            calculate_file_priority(Path(file.path)),
            file.path.lower(),
        ),
    )


def build_file_tree(
    files: list[RepositoryFile],
) -> str:
    if not files:
        return "No supported repository files were found."

    return "\n".join(
        sorted(file.path for file in files)
    )