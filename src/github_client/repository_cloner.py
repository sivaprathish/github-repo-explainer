from __future__ import annotations

import os
import tempfile
from pathlib import Path

from git import GitCommandError, Repo
from langsmith import traceable

from src.config import settings


class RepositoryCloner:
    @staticmethod
    def _clone_url(full_name: str, is_private: bool) -> str:
        if not is_private:
            return f"https://github.com/{full_name}.git"

        if not settings.github_token:
            raise ValueError(
                "GITHUB_TOKEN is required for private repositories."
            )

        return (
            f"https://x-access-token:{settings.github_token}"
            f"@github.com/{full_name}.git"
        )

    @traceable(name="clone-repository", run_type="tool")
    def clone(
        self,
        *,
        full_name: str,
        repository_name: str,
        default_branch: str,
        is_private: bool,
    ) -> Path:
        directory = Path(
            tempfile.mkdtemp(
                prefix=f"github_explainer_{repository_name}_"
            )
        )

        try:
            Repo.clone_from(
                self._clone_url(full_name, is_private),
                directory,
                branch=default_branch,
                depth=1,
                single_branch=True,
                no_tags=True,
            )
        except GitCommandError as error:
            try:
                os.rmdir(directory)
            except OSError:
                pass

            raise RuntimeError(f"Git clone failed: {error}") from error

        return directory