from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


class Settings:
    """Simple runtime configuration container for the application."""

    def __init__(self) -> None:
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY")
        self.nvidia_model = os.getenv(
            "NVIDIA_MODEL",
            "mistralai/mistral-medium-3.5-128b",
        )
        self.nvidia_base_url = os.getenv(
            "NVIDIA_BASE_URL",
            "https://integrate.api.nvidia.com/v1",
        )


settings = Settings()