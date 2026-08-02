from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from langsmith import traceable


@dataclass(frozen=True)
class ParsedGitHubURL:
    owner: str
    repository: str

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repository}"


@traceable(name="parse-github-url", run_type="tool")
def parse_github_url(repo_url: str) -> ParsedGitHubURL:
    parsed = urlparse(repo_url.strip())

    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        raise ValueError("Enter a valid github.com repository URL.")

    parts = [part for part in parsed.path.strip("/").split("/") if part]

    if len(parts) < 2:
        raise ValueError("GitHub URL must contain owner and repository.")

    return ParsedGitHubURL(
        owner=parts[0],
        repository=parts[1].removesuffix(".git"),
    )