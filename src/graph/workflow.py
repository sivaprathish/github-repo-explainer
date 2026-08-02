from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.graph.nodes import (
    architecture_agent_node,
    documentation_agent_node,
    load_repository_node,
    report_agent_node,
    scan_repository_node,
    static_analysis_node,
)
from src.graph.state import RepositoryAnalysisState


def build_analysis_graph():
    """
    Build an optimized repository-analysis graph.

    LLM calls:
    1. Documentation agent
    2. Architecture agent
    3. Final report agent
    """

    builder = StateGraph(RepositoryAnalysisState)

    builder.add_node(
        "load_repository",
        load_repository_node,
    )

    builder.add_node(
        "scan_repository",
        scan_repository_node,
    )

    builder.add_node(
        "static_analysis",
        static_analysis_node,
    )

    builder.add_node(
        "documentation_agent",
        documentation_agent_node,
    )

    builder.add_node(
        "architecture_agent",
        architecture_agent_node,
    )

    builder.add_node(
        "report_agent",
        report_agent_node,
    )

    builder.add_edge(
        START,
        "load_repository",
    )

    builder.add_edge(
        "load_repository",
        "scan_repository",
    )

    builder.add_edge(
        "scan_repository",
        "static_analysis",
    )

    builder.add_edge(
        "static_analysis",
        "documentation_agent",
    )

    builder.add_edge(
        "documentation_agent",
        "architecture_agent",
    )

    builder.add_edge(
        "architecture_agent",
        "report_agent",
    )

    builder.add_edge(
        "report_agent",
        END,
    )

    return builder.compile()


repository_analysis_graph = build_analysis_graph()