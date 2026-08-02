from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA

from src.config import settings
from src.models.repository_models import RepositoryData


SYSTEM_PROMPT = """
You are a senior software architect.

Explain the supplied GitHub repository using only the information provided.

Include:

1. Repository purpose
2. Main programming languages and technologies
3. Default branch
4. Latest repository activity
5. Features mentioned in the README
6. Setup information, when available
7. Concise technical overview

Do not invent details that are not present.
Keep the response below 500 words.
"""


def create_repository_summary_chain():
    if not settings.nvidia_api_key:
        raise ValueError(
            "NVIDIA_API_KEY is missing from the environment."
        )

    model = ChatNVIDIA(
        model=settings.nvidia_model,
        api_key=settings.nvidia_api_key,
        base_url="https://integrate.api.nvidia.com/v1",
        temperature=0.1,
        max_completion_tokens=600,
        timeout=180,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                """
Repository metadata:
{metadata}

Languages:
{languages}

Branches:
{branches}

Latest commit:
{latest_commit}

README:
{readme}
""",
            ),
        ]
    )

    return prompt | model | StrOutputParser()


def summarize_repository(
    repository_data: RepositoryData,
) -> str:
    chain = create_repository_summary_chain()

    readme_content = "README not found."

    if repository_data.readme:
        readme_content = repository_data.readme.content[:8_000]

    valid_languages = [
        language.model_dump()
        for language in repository_data.languages
        if language.bytes > 0
    ]

    branches = [
        branch.model_dump()
        for branch in repository_data.branches[:10]
    ]

    latest_commit = (
        repository_data.latest_commit.model_dump_json(indent=2)
        if repository_data.latest_commit
        else "No commit found."
    )

    return chain.invoke(
        {
            "metadata": (
                repository_data.metadata.model_dump_json(indent=2)
            ),
            "languages": valid_languages,
            "branches": branches,
            "latest_commit": latest_commit,
            "readme": readme_content,
        },
        config={
            "run_name": "nvidia-mistral-repository-summary",
            "tags": [
                "nvidia",
                "mistral",
                "repository-summary",
            ],
            "metadata": {
                "repository": (
                    repository_data.metadata.full_name
                ),
                "model": settings.nvidia_model,
            },
        },
    )