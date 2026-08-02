from __future__ import annotations

from src.graph.workflow import repository_analysis_graph


class AnalysisService:
    def analyze(self, repo_url: str) -> dict:
        """
        Run the optimized repository-analysis workflow.
        """

        return repository_analysis_graph.invoke(
            {
                "repo_url": repo_url,
                "completed_agents": [],
                "errors": [],
            }
        )