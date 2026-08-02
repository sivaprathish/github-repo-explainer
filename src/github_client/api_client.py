from __future__ import annotations

from github import Auth, Github

from src.config import settings


def create_github_client() -> Github:
    if settings.github_token:
        return Github(
            auth=Auth.Token(settings.github_token),
            timeout=30,
            retry=3,
        )

    return Github(timeout=30, retry=3)