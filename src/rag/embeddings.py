from __future__ import annotations

import os

from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings

from src.config import settings


def get_embeddings() -> NVIDIAEmbeddings:
    if not settings.nvidia_api_key:
        raise ValueError(
            "NVIDIA_API_KEY is missing."
        )

    model_name = os.getenv(
        "NVIDIA_EMBEDDING_MODEL",
        "nvidia/nv-embedqa-e5-v5",
    )

    return NVIDIAEmbeddings(
        model=model_name,
        api_key=settings.nvidia_api_key,
        base_url=settings.nvidia_base_url,
    )