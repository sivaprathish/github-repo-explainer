from __future__ import annotations

from langchain_nvidia_ai_endpoints import ChatNVIDIA

from src.config import settings


def get_llm() -> ChatNVIDIA:
    """
    Create the shared NVIDIA chat model.

    A smaller output limit reduces API usage and response time.
    """

    if not settings.nvidia_api_key:
        raise ValueError(
            "NVIDIA_API_KEY is missing from the environment."
        )

    base_url = getattr(
        settings,
        "nvidia_base_url",
        "https://integrate.api.nvidia.com/v1",
    )

    return ChatNVIDIA(
        model=settings.nvidia_model,
        api_key=settings.nvidia_api_key,
        base_url=base_url,
        temperature=0.1,
        max_tokens=500,
        timeout=180,
    )