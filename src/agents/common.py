from __future__ import annotations

import random
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.agents.base import get_llm


MAX_AGENT_CONTEXT = 10_000
MAX_ATTEMPTS = 5
INITIAL_DELAY_SECONDS = 3
MAX_DELAY_SECONDS = 30


def _is_retryable_error(error: Exception) -> bool:
    message = str(error).lower()

    retryable_markers = (
        "[529]",
        "service temporarily overloaded",
        "overloaded",
        "read timed out",
        "timeout",
        "[502]",
        "[503]",
        "[504]",
        "connection reset",
    )

    return any(
        marker in message
        for marker in retryable_markers
    )


def run_agent(
    *,
    role: str,
    instructions: str,
    context: str,
    run_name: str,
) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a {role}.

Instructions:
{instructions}

Rules:
- Use only the supplied repository evidence.
- Do not invent files, dependencies, APIs, technologies, or behavior.
- Mention relevant file paths when evidence is available.
- State clearly when information cannot be determined.
- Keep the response concise.
""",
            ),
            (
                "human",
                "Repository evidence:\n\n{context}",
            ),
        ]
    )

    chain = prompt | get_llm() | StrOutputParser()

    payload = {
        "role": role,
        "instructions": instructions,
        "context": context[:MAX_AGENT_CONTEXT],
    }

    delay = INITIAL_DELAY_SECONDS

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return chain.invoke(
                payload,
                config={
                    "run_name": run_name,
                    "tags": [
                        "github-explainer",
                        "optimized-multi-agent",
                    ],
                    "metadata": {
                        "attempt": attempt,
                    },
                },
            )

        except Exception as error:
            if (
                not _is_retryable_error(error)
                or attempt == MAX_ATTEMPTS
            ):
                raise

            jitter = random.uniform(0, 1.5)
            wait_seconds = min(
                delay + jitter,
                MAX_DELAY_SECONDS,
            )

            print(
                f"{run_name} temporarily unavailable. "
                f"Retry {attempt}/{MAX_ATTEMPTS} "
                f"in {wait_seconds:.1f} seconds."
            )

            time.sleep(wait_seconds)
            delay = min(delay * 2, MAX_DELAY_SECONDS)

    raise RuntimeError(
        f"{run_name} failed after {MAX_ATTEMPTS} attempts."
    )