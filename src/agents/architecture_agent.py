from __future__ import annotations

from src.agents.common import run_agent


def analyze_architecture(context: str) -> str:
    """
    Generate architecture, dependencies, APIs, and code flow
    in one LLM call.
    """

    return run_agent(
        role="senior software architecture analyst",
        instructions="""
Create the following sections:

## Architecture Overview
Explain:
- Main application components
- Layers and responsibilities
- UI, services, APIs, and storage
- External integrations
- High-level architecture

Include a Mermaid flowchart when enough evidence is available.

## Dependency Analysis
Explain:
- Important runtime dependencies
- Important development dependencies
- Why the major packages are used
- Which dependency files contain them

## API Discovery
Explain:
- Detected REST routes
- HTTP methods and paths
- GraphQL endpoints, when present
- External service calls
- Files containing API implementations

## Code Flow
Explain:
- Application entry points
- Startup sequence
- Request or UI event flow
- Service and component interactions
- Database or external-service interactions
- Important file paths

Use only supplied evidence.
Clearly mention uncertain parts.
""",
        context=context,
        run_name="architecture-agent",
    )