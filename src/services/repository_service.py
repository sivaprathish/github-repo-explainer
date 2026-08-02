from __future__ import annotations

from src.github_client.repository_cloner import RepositoryCloner
from src.github_client.repository_loader import GitHubRepositoryLoader
from src.github_client.url_parser import parse_github_url
from src.models.repository_models import RepositoryData


class RepositoryService:
    def __init__(self) -> None:
        self.loader = GitHubRepositoryLoader()
        self.cloner = RepositoryCloner()

    def load_repository(self, repo_url: str) -> RepositoryData:
        parsed = parse_github_url(repo_url)
        repository = self.loader.get_repository(parsed)

        metadata = self.loader.get_metadata(repository)

        local_path = self.cloner.clone(
            full_name=metadata.full_name,
            repository_name=metadata.name,
            default_branch=metadata.default_branch,
            is_private=metadata.is_private,
        )

        return RepositoryData(
            metadata=metadata,
            languages=self.loader.get_languages(repository),
            branches=self.loader.get_branches(repository),
            readme=self.loader.get_readme(repository),
            latest_commit=self.loader.get_latest_commit(repository),
            local_path=str(local_path),
        )