from __future__ import annotations

import os

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    github_token: str | None = Field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN")
    )

    nvidia_api_key: str | None = Field(
        default_factory=lambda: os.getenv("NVIDIA_API_KEY")
    )

    nvidia_model: str = Field(
        default_factory=lambda: os.getenv(
            "NVIDIA_MODEL",
            "mistralai/mistral-medium-3.5-128b",
        )
    )

    nvidia_base_url: str = Field(
        default_factory=lambda: os.getenv(
            "NVIDIA_BASE_URL",
            "https://integrate.api.nvidia.com/v1",
        )
    )


settings = Settings()