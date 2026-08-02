from __future__ import annotations

import json

from src.agents.api_agent import analyze_apis
from src.agents.architecture_agent import analyze_architecture
from src.agents.code_flow_agent import analyze_code_flow
from src.agents.dependency_agent import analyze_dependencies
from src.agents.installation_agent import generate_installation_guide
from src.agents.quality_agent import analyze_quality
from src.agents.readme_agent import analyze_readme
from src.agents.report_agent import build_final_report
from src.agents.structure_agent import analyze_structure
from src.agents.tech_stack_agent import analyze_tech_stack
from src.parsers.api_parser import discover_api_routes
from src.parsers.dependency_parser import discover_dependencies
from src.parsers.entrypoint_parser import detect_entrypoints
from src.parsers.quality_parser import inspect_quality
from src.scanners.repository_scanner import (
    build_file_tree,
    scan_repository,
)
from src.services.repository_service import RepositoryService


def load_repository_node(state):
    data = RepositoryService().load_repository(state["repo_url"])

    return {
        "repository_data": data,
        "local_path": data.local_path,
        "completed_agents": ["repository-loader"],
    }


def scan_repository_node(state):
    files = scan_repository(state["local_path"])

    return {
        "files": files,
        "file_tree": build_file_tree(files),
        "completed_agents": ["repository-scanner"],
    }


def static_analysis_node(state):
    return {
        "dependencies": discover_dependencies(state["files"]),
        "api_routes": discover_api_routes(state["files"]),
        "quality_findings": inspect_quality(state["files"]),
        "completed_agents": ["static-analysis"],
    }


def _important_file_context(state) -> str:
    important_names = {
        "README.md",
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "angular.json",
        "Dockerfile",
        "docker-compose.yml",
        ".env.example",
    }

    contents = []

    for file in state["files"]:
        if file.name in important_names:
            contents.append(
                f"\nFILE: {file.path}\n{file.content[:8000]}"
            )

    return "\n".join(contents)


def readme_node(state):
    repository = state["repository_data"]

    context = (
        repository.readme.content
        if repository.readme
        else "README not found."
    )

    return {
        "readme_summary": analyze_readme(context),
        "completed_agents": ["readme-agent"],
    }


def tech_stack_node(state):
    return {
        "tech_stack_report": analyze_tech_stack(
            _important_file_context(state)
        ),
        "completed_agents": ["tech-stack-agent"],
    }


def structure_node(state):
    return {
        "structure_report": analyze_structure(
            state["file_tree"]
        ),
        "completed_agents": ["structure-agent"],
    }


def architecture_node(state):
    context = (
        f"FILE TREE:\n{state['file_tree']}\n\n"
        f"DEPENDENCIES:\n"
        f"{json.dumps([d.model_dump() for d in state['dependencies']], indent=2)}"
    )

    return {
        "architecture_report": analyze_architecture(context),
        "completed_agents": ["architecture-agent"],
    }


def dependency_node(state):
    context = json.dumps(
        [item.model_dump() for item in state["dependencies"]],
        indent=2,
    )

    return {
        "dependency_report": analyze_dependencies(context),
        "completed_agents": ["dependency-agent"],
    }


def code_flow_node(state):
    entrypoints = detect_entrypoints(state["files"])

    context = "\n\n".join(
        f"FILE: {file.path}\n{file.content[:8000]}"
        for file in entrypoints
    )

    if not context:
        context = f"FILE TREE:\n{state['file_tree']}"

    return {
        "code_flow_report": analyze_code_flow(context),
        "completed_agents": ["code-flow-agent"],
    }


def api_node(state):
    context = json.dumps(
        [route.model_dump() for route in state["api_routes"]],
        indent=2,
    )

    return {
        "api_report": analyze_apis(context),
        "completed_agents": ["api-agent"],
    }


def installation_node(state):
    return {
        "installation_guide": generate_installation_guide(
            _important_file_context(state)
        ),
        "completed_agents": ["installation-agent"],
    }


def quality_node(state):
    context = json.dumps(
        [
            finding.model_dump()
            for finding in state["quality_findings"]
        ],
        indent=2,
    )

    return {
        "quality_report": analyze_quality(context),
        "completed_agents": ["quality-agent"],
    }


def report_node(state):
    return {
        "final_report": build_final_report(state),
        "completed_agents": ["report-agent"],
    }