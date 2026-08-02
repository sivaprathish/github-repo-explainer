from __future__ import annotations

import re

from src.models.analysis_models import (
    QualityFinding,
    RepositoryFile,
)


MARKER_PATTERN = re.compile(
    r"\b(TODO|FIXME|HACK|XXX)\b",
    re.IGNORECASE,
)


def inspect_quality(
    files: list[RepositoryFile],
) -> list[QualityFinding]:
    findings = []

    for file in files:
        if file.line_count > 500:
            findings.append(
                QualityFinding(
                    category="large_file",
                    severity="medium",
                    file_path=file.path,
                    message=(
                        f"File contains {file.line_count} lines."
                    ),
                )
            )

        if not file.content.strip():
            findings.append(
                QualityFinding(
                    category="empty_file",
                    severity="low",
                    file_path=file.path,
                    message="File is empty.",
                )
            )

        for number, line in enumerate(
            file.content.splitlines(),
            start=1,
        ):
            if MARKER_PATTERN.search(line):
                findings.append(
                    QualityFinding(
                        category="maintenance_marker",
                        severity="low",
                        file_path=file.path,
                        line_number=number,
                        message=line.strip(),
                    )
                )

    return findings