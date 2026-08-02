from __future__ import annotations

from src.agents.common import run_agent


def analyze_documentation(context: str) -> str:
    """
    Generate repository documentation-related sections in one LLM call.
    """

    return run_agent(
        role="repository documentation and technology analyst",
        instructions="""
Create the following sections:

## README Summary
Explain:
- Project purpose
- Main features
- Target users
- How the project works

## Technology Stack
Identify:
- Programming languages
- Frontend frameworks
- Backend frameworks
- Databases
- APIs and external services
- Important libraries
- Build and testing tools

## Folder Structure
Explain:
- Important top-level folders
- Important source folders
- Entry-point files
- Configuration files
- Test folders
- Build and deployment files

## Installation Guide
Generate evidence-based instructions for:
- Prerequisites
- Dependency installation
- Environment configuration
- Development command
- Build command
- Test command

Do not invent missing setup commands.
Mark uncertain instructions clearly.
""",
        context=context,
        run_name="documentation-agent",
    )