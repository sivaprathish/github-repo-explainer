import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from langsmith import traceable

from src.agents.architecture_agent import analyze_architecture
from src.agents.documentation_agent import analyze_documentation
from src.agents.report_agent import generate_final_report
from src.parsers.api_parser import discover_api_routes
from src.parsers.dependency_parser import discover_dependencies
from src.parsers.entrypoint_parser import detect_entrypoints
from src.parsers.quality_parser import inspect_quality
from src.scanners.repository_scanner import (
    build_file_tree,
    scan_repository,
)
from src.services.repository_service import RepositoryService


# ============================================================
# Context limits
# ============================================================

MAX_README_LENGTH = 4_000
MAX_FILE_TREE_LENGTH = 4_000
MAX_IMPORTANT_FILE_CONTENT = 3_000
MAX_IMPORTANT_FILES = 12
MAX_LIST_ITEMS = 75
MAX_ENTRY_POINTS = 8
MAX_ENTRY_POINT_CONTENT = 2_500
MAX_AGENT_REPORT_CONTEXT = 5_000


# ============================================================
# Helper functions
# ============================================================

def _serialize_models(
    items: list[Any],
) -> list[dict[str, Any]]:
    """
    Convert Pydantic models and dictionaries into plain dictionaries.
    """

    serialized: list[dict[str, Any]] = []

    for item in items:
        if hasattr(item, "model_dump"):
            serialized.append(item.model_dump())

        elif isinstance(item, dict):
            serialized.append(item)

    return serialized


def _important_files_context(
    state: dict[str, Any],
) -> str:
    """
    Return the content of important repository files only.

    This avoids sending the full repository to the LLM.
    """

    important_names = {
        "README",
        "README.md",
        "README.rst",
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "angular.json",
        "vite.config.js",
        "vite.config.ts",
        "next.config.js",
        "next.config.ts",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        ".env.example",
        "Makefile",
    }

    parts: list[str] = []

    for repository_file in state.get("files", []):
        if repository_file.name not in important_names:
            continue

        parts.append(
            f"FILE: {repository_file.path}\n"
            f"{repository_file.content[:MAX_IMPORTANT_FILE_CONTENT]}"
        )

        if len(parts) >= MAX_IMPORTANT_FILES:
            break

    if not parts:
        return "No important configuration or dependency files were found."

    return "\n\n".join(parts)


def build_documentation_context(
    state: dict[str, Any],
) -> str:
    """
    Build compact evidence for the documentation agent.

    Includes repository metadata, languages, README, file tree,
    dependencies, and important configuration files.
    """

    repository = state["repository_data"]

    readme = "README not found."

    if repository.readme:
        readme = repository.readme.content[:MAX_README_LENGTH]

    languages = [
        language.model_dump()
        for language in repository.languages
        if language.bytes > 0
    ]

    dependencies = _serialize_models(
        state.get("dependencies", [])
    )[:MAX_LIST_ITEMS]

    return f"""
REPOSITORY METADATA:
{repository.metadata.model_dump_json(indent=2)}

LANGUAGES:
{json.dumps(languages, indent=2)}

README:
{readme}

FILE TREE:
{state.get("file_tree", "")[:MAX_FILE_TREE_LENGTH]}

DEPENDENCIES:
{json.dumps(dependencies, indent=2)}

IMPORTANT FILE CONTENT:
{_important_files_context(state)}
""".strip()


def build_architecture_context(
    state: dict[str, Any],
) -> str:
    """
    Build compact evidence for architecture, API, dependency,
    and code-flow analysis.
    """

    dependencies = _serialize_models(
        state.get("dependencies", [])
    )[:MAX_LIST_ITEMS]

    routes = _serialize_models(
        state.get("api_routes", [])
    )[:MAX_LIST_ITEMS]

    entry_points = state.get("entry_points", [])

    entrypoint_parts: list[str] = []

    for repository_file in entry_points[:MAX_ENTRY_POINTS]:
        entrypoint_parts.append(
            f"FILE: {repository_file.path}\n"
            f"{repository_file.content[:MAX_ENTRY_POINT_CONTENT]}"
        )

    entrypoint_context = (
        "\n\n".join(entrypoint_parts)
        if entrypoint_parts
        else "No explicit entry point was detected."
    )

    documentation_report = state.get(
        "documentation_report",
        "",
    )[:MAX_AGENT_REPORT_CONTEXT]

    return f"""
FILE TREE:
{state.get("file_tree", "")[:MAX_FILE_TREE_LENGTH]}

ENTRY POINTS:
{entrypoint_context}

DEPENDENCIES:
{json.dumps(dependencies, indent=2)}

DISCOVERED API ROUTES:
{json.dumps(routes, indent=2)}

DOCUMENTATION REPORT:
{documentation_report}
""".strip()


def build_report_context(
    state: dict[str, Any],
) -> str:
    """
    Build compact evidence for the final report agent.
    """

    quality_findings = _serialize_models(
        state.get("quality_findings", [])
    )[:MAX_LIST_ITEMS]

    documentation_report = state.get(
        "documentation_report",
        "",
    )[:MAX_AGENT_REPORT_CONTEXT]

    architecture_report = state.get(
        "architecture_report",
        "",
    )[:MAX_AGENT_REPORT_CONTEXT]

    return f"""
DOCUMENTATION REPORT:
{documentation_report}

ARCHITECTURE REPORT:
{architecture_report}

STATIC CODE-QUALITY FINDINGS:
{json.dumps(quality_findings, indent=2)}

REPOSITORY STATISTICS:
- Files analyzed: {len(state.get("files", []))}
- Dependencies detected: {len(state.get("dependencies", []))}
- API routes detected: {len(state.get("api_routes", []))}
- Entry points detected: {len(state.get("entry_points", []))}
- Quality findings: {len(state.get("quality_findings", []))}
""".strip()


# ============================================================
# LangGraph nodes
# ============================================================

@traceable(
    name="load-repository-node",
    run_type="tool",
)
def load_repository_node(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Fetch GitHub metadata and clone the repository.
    """

    repository_data = RepositoryService().load_repository(
        state["repo_url"]
    )

    return {
        "repository_data": repository_data,
        "local_path": repository_data.local_path,
        "completed_agents": ["repository-loader"],
    }


@traceable(
    name="scan-repository-node",
    run_type="tool",
)
def scan_repository_node(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Scan important repository files and build the file tree.
    """

    local_path = state.get("local_path")

    if not local_path:
        raise ValueError(
            "Repository local path is missing from graph state."
        )

    files = scan_repository(local_path)

    return {
        "files": files,
        "file_tree": build_file_tree(files),
        "completed_agents": ["repository-scanner"],
    }


@traceable(
    name="static-analysis-node",
    run_type="tool",
)
def static_analysis_node(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Run independent Python analyses concurrently.

    These tasks do not call the LLM:
    - Dependency detection
    - API-route detection
    - Code-quality checks
    - Entry-point detection
    """

    files = state.get("files", [])

    if not files:
        return {
            "dependencies": [],
            "api_routes": [],
            "quality_findings": [],
            "entry_points": [],
            "completed_agents": ["static-analysis"],
        }

    with ThreadPoolExecutor(max_workers=4) as executor:
        dependencies_future = executor.submit(
            discover_dependencies,
            files,
        )

        api_routes_future = executor.submit(
            discover_api_routes,
            files,
        )

        quality_future = executor.submit(
            inspect_quality,
            files,
        )

        entry_points_future = executor.submit(
            detect_entrypoints,
            files,
        )

        dependencies = dependencies_future.result()
        api_routes = api_routes_future.result()
        quality_findings = quality_future.result()
        entry_points = entry_points_future.result()

    return {
        "dependencies": dependencies,
        "api_routes": api_routes,
        "quality_findings": quality_findings,
        "entry_points": entry_points,
        "completed_agents": ["static-analysis"],
    }


@traceable(
    name="documentation-agent-node",
    run_type="chain",
)
def documentation_agent_node(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate README, technology-stack, folder-structure,
    and installation analysis in one LLM call.
    """

    context = build_documentation_context(state)

    report = analyze_documentation(context)

    return {
        "documentation_report": report,
        "completed_agents": ["documentation-agent"],
    }


@traceable(
    name="architecture-agent-node",
    run_type="chain",
)
def architecture_agent_node(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate architecture, dependency, API, and code-flow
    analysis in one LLM call.
    """

    context = build_architecture_context(state)

    report = analyze_architecture(context)

    return {
        "architecture_report": report,
        "completed_agents": ["architecture-agent"],
    }


@traceable(
    name="report-agent-node",
    run_type="chain",
)
def report_agent_node(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate the final combined repository report.
    """

    context = build_report_context(state)

    report = generate_final_report(context)

    return {
        "final_report": report,
        "completed_agents": ["report-agent"],
    }