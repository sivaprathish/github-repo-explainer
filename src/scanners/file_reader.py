from __future__ import annotations

from pathlib import Path

from src.models.analysis_models import RepositoryFile


def read_file(
    root: Path,
    file_path: Path,
) -> RepositoryFile | None:
    """
    Read one repository file and return structured metadata.
    """

    try:
        content = file_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        size_bytes = file_path.stat().st_size

    except OSError:
        return None

    return RepositoryFile(
        path=file_path.relative_to(root).as_posix(),
        name=file_path.name,
        extension=file_path.suffix.lower(),
        size_bytes=size_bytes,
        line_count=len(content.splitlines()),
        content=content,
    )