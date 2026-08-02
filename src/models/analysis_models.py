from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RepositoryFile(BaseModel):
    path: str
    name: str
    extension: str
    size_bytes: int
    line_count: int
    content: str


class DependencyItem(BaseModel):
    name: str
    version: str | None = None
    dependency_type: str
    source_file: str


class APIRoute(BaseModel):
    method: str
    route: str
    file_path: str
    framework: str | None = None


class QualityFinding(BaseModel):
    category: str
    severity: str
    file_path: str
    message: str
    line_number: int | None = None


class AnalysisResult(BaseModel):
    repository_data: Any
    files: list[RepositoryFile] = Field(default_factory=list)
    file_tree: str = ""

    dependencies: list[DependencyItem] = Field(default_factory=list)
    api_routes: list[APIRoute] = Field(default_factory=list)
    quality_findings: list[QualityFinding] = Field(default_factory=list)

    readme_summary: str = ""
    tech_stack_report: str = ""
    structure_report: str = ""
    architecture_report: str = ""
    dependency_report: str = ""
    code_flow_report: str = ""
    api_report: str = ""
    installation_guide: str = ""
    quality_report: str = ""
    final_report: str = ""