from __future__ import annotations

import operator
from typing import Annotated, Any, TypedDict

from src.models.analysis_models import (
    APIRoute,
    DependencyItem,
    QualityFinding,
    RepositoryFile,
)


class RepositoryAnalysisState(TypedDict, total=False):
    # Input
    repo_url: str

    # Repository data
    repository_data: Any
    local_path: str

    # Scanning and static analysis
    files: list[RepositoryFile]
    file_tree: str
    dependencies: list[DependencyItem]
    api_routes: list[APIRoute]
    quality_findings: list[QualityFinding]
    entry_points: list[RepositoryFile]

    # Three combined LLM outputs
    documentation_report: str
    architecture_report: str
    final_report: str

    # Execution information
    completed_agents: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]