"""Configuration management for VoiceBridge.

Loads configuration from .env file and validates required API keys.
"""

import os
from dotenv import load_dotenv


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(
        self,
        deepgram_api_key: str,
        anthropic_api_key: str,
        target_language: str = "en",
        sample_rate: int = 16000,
        input_device: int | None = None,
        output_device: int | None = None,
    ):
        self.deepgram_api_key = deepgram_api_key
        self.anthropic_api_key = anthropic_api_key
        self.target_language = target_language
        self.sample_rate = sample_rate
        self.input_device = input_device
        self.output_device = output_device

    @classmethod
    def load_from_env(cls) -> "Config":
        """Load configuration from .env file.

        Returns:
            Config: Configured instance with validated API keys.

        Raises:
            ValueError: If required API keys are missing.
        """
        load_dotenv()

        deepgram_key = os.getenv("DEEPGRAM_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not deepgram_key:
            raise ValueError(
                "DEEPGRAM_API_KEY is required. "
                "Please set it in your .env file (see .env.example)."
            )

        if not anthropic_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required. "
                "Please set it in your .env file (see .env.example)."
            )

        return cls(
            deepgram_api_key=deepgram_key,
            anthropic_api_key=anthropic_key,
        )
