from __future__ import annotations

from github.GithubException import GithubException
from github.Repository import Repository
from langsmith import traceable

from src.github_client.api_client import create_github_client
from src.github_client.url_parser import ParsedGitHubURL
from src.models.repository_models import (
    RepositoryBranch,
    RepositoryCommit,
    RepositoryLanguage,
    RepositoryMetadata,
    RepositoryReadme,
)


class GitHubRepositoryLoader:
    def __init__(self) -> None:
        self.client = create_github_client()

    def get_repository(
        self,
        parsed_url: ParsedGitHubURL,
    ) -> Repository:
        try:
            return self.client.get_repo(parsed_url.full_name)
        except GithubException as error:
            if error.status == 404:
                raise ValueError(
                    "Repository was not found or is private."
                ) from error
            raise

    @traceable(name="load-metadata", run_type="tool")
    def get_metadata(
        self,
        repository: Repository,
    ) -> RepositoryMetadata:
        return RepositoryMetadata(
            repository_id=repository.id,
            name=repository.name,
            full_name=repository.full_name,
            owner=repository.owner.login,
            description=repository.description,
            html_url=repository.html_url,
            clone_url=repository.clone_url,
            default_branch=repository.default_branch,
            primary_language=repository.language,
            license_name=(
                repository.license.name
                if repository.license
                else None
            ),
            stars=repository.stargazers_count,
            forks=repository.forks_count,
            open_issues=repository.open_issues_count,
            size_kb=repository.size,
            is_private=repository.private,
            is_fork=repository.fork,
            topics=repository.get_topics(),
            created_at=repository.created_at,
            updated_at=repository.updated_at,
            pushed_at=repository.pushed_at,
        )

    def get_languages(
        self,
        repository: Repository,
    ) -> list[RepositoryLanguage]:
        raw = repository.get_languages()
        cleaned: dict[str, int] = {}

        for language, value in raw.items():
            try:
                byte_count = int(value)
            except (TypeError, ValueError):
                continue

            if byte_count > 0:
                cleaned[str(language)] = byte_count

        total = sum(cleaned.values())

        return sorted(
            [
                RepositoryLanguage(
                    language=language,
                    bytes=byte_count,
                    percentage=round(byte_count * 100 / total, 2)
                    if total
                    else 0,
                )
                for language, byte_count in cleaned.items()
            ],
            key=lambda item: item.bytes,
            reverse=True,
        )

    def get_branches(
        self,
        repository: Repository,
        limit: int = 20,
    ) -> list[RepositoryBranch]:
        result = []

        for index, branch in enumerate(repository.get_branches()):
            if index >= limit:
                break

            result.append(
                RepositoryBranch(
                    name=branch.name,
                    commit_sha=branch.commit.sha,
                    protected=branch.protected,
                )
            )

        return result

    def get_readme(
        self,
        repository: Repository,
    ) -> RepositoryReadme | None:
        try:
            readme = repository.get_readme(
                ref=repository.default_branch
            )
        except GithubException as error:
            if error.status == 404:
                return None
            raise

        return RepositoryReadme(
            name=readme.name,
            path=readme.path,
            size_bytes=readme.size,
            content=readme.decoded_content.decode(
                "utf-8",
                errors="replace",
            ),
        )

    def get_latest_commit(
        self,
        repository: Repository,
    ) -> RepositoryCommit | None:
        commits = repository.get_commits(
            sha=repository.default_branch
        )

        try:
            latest = commits[0]
        except IndexError:
            return None

        author = latest.commit.author

        return RepositoryCommit(
            sha=latest.sha,
            short_sha=latest.sha[:7],
            message=latest.commit.message,
            author_name=author.name if author else None,
            author_email=author.email if author else None,
            committed_at=author.date if author else None,
            html_url=latest.html_url,
        )