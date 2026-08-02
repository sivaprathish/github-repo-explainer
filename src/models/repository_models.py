from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RepositoryMetadata(BaseModel):
    repository_id: int
    name: str
    full_name: str
    owner: str
    description: str | None = None
    html_url: str
    clone_url: str
    default_branch: str
    primary_language: str | None = None
    license_name: str | None = None
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    size_kb: int = 0
    is_private: bool = False
    is_fork: bool = False
    topics: list[str] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    pushed_at: datetime | None = None


class RepositoryLanguage(BaseModel):
    language: str
    bytes: int
    percentage: float


class RepositoryBranch(BaseModel):
    name: str
    commit_sha: str
    protected: bool


class RepositoryReadme(BaseModel):
    name: str
    path: str
    size_bytes: int
    content: str


class RepositoryCommit(BaseModel):
    sha: str
    short_sha: str
    message: str
    author_name: str | None = None
    author_email: str | None = None
    committed_at: datetime | None = None
    html_url: str


class RepositoryData(BaseModel):
    metadata: RepositoryMetadata
    languages: list[RepositoryLanguage]
    branches: list[RepositoryBranch]
    readme: RepositoryReadme | None
    latest_commit: RepositoryCommit | None
    local_path: str