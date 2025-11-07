"""Configuration management for lilagent."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration for the multi-agent system."""

    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: Optional[str] = os.getenv("OPENAI_API_BASE")
    ANTHROPIC_API_BASE: Optional[str] = os.getenv("ANTHROPIC_API_BASE")

    # Model Selection
    NORMALIZER_MODEL: str = os.getenv("NORMALIZER_MODEL", "evals-anthropic/claude-haiku-4-0")
    AGENT_MODEL: str = os.getenv("AGENT_MODEL", "evals-anthropic/claude-sonnet-4-0")

    # Webhook Configuration
    WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL")

    # GitHub Configuration
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    GITHUB_REPO: Optional[str] = os.getenv("GITHUB_REPO")  # Format: owner/repo
    GITHUB_DEFAULT_BRANCH: str = os.getenv("GITHUB_DEFAULT_BRANCH", "main")

    # Agent Configuration
    MAX_CODER_REVIEWER_ITERATIONS: int = int(os.getenv("MAX_CODER_REVIEWER_ITERATIONS", "3"))
    MAX_PLANNING_UAT_ITERATIONS: int = int(os.getenv("MAX_PLANNING_UAT_ITERATIONS", "2"))
    ENABLE_VERBOSE_LOGGING: bool = os.getenv("ENABLE_VERBOSE_LOGGING", "true").lower() == "true"

    # Paths
    DEFAULT_WORK_DIR: str = os.getenv("DEFAULT_WORK_DIR", "/tmp/lilagent-output")

    @classmethod
    def get_spec_template_path(cls) -> Path:
        """Get path to specification template."""
        return Path(__file__).parent / "prompts" / "templates" / "spec_template.md"

    @classmethod
    def validate(cls) -> None:
        """Validate that required configuration is present.

        Raises:
            ValueError: If required configuration is missing
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Copy .env.example to .env and configure."
            )

    @classmethod
    def validate_github(cls) -> None:
        """Validate GitHub configuration for GitHub mode.

        Raises:
            ValueError: If GitHub configuration is missing
        """
        if not cls.GITHUB_TOKEN:
            raise ValueError(
                "GITHUB_TOKEN environment variable is required for GitHub mode. "
                "Set it in your .env file."
            )
        if not cls.GITHUB_REPO:
            raise ValueError(
                "GITHUB_REPO environment variable is required for GitHub mode. "
                "Format: owner/repo (e.g., 'myuser/myproject')"
            )

    @classmethod
    def get_llm_config(cls, model_type: str = "agent") -> dict:
        """Get LLM configuration for CrewAI.

        Args:
            model_type: Either "normalizer" (cheap) or "agent" (smart)

        Returns:
            Dict with LLM configuration
        """
        model = cls.NORMALIZER_MODEL if model_type == "normalizer" else cls.AGENT_MODEL

        config = {
            "model": model,
            "api_key": cls.OPENAI_API_KEY,
        }

        # Add base URL if configured (for proxy)
        if "anthropic" in model.lower() and cls.ANTHROPIC_API_BASE:
            config["base_url"] = cls.ANTHROPIC_API_BASE
        elif "openai" in model.lower() and cls.OPENAI_API_BASE:
            config["base_url"] = cls.OPENAI_API_BASE

        return config


# Validate configuration on import (can be disabled if needed)
if os.getenv("SKIP_CONFIG_VALIDATION") != "true":
    try:
        Config.validate()
    except ValueError as e:
        # Don't fail hard on import, just warn
        print(f"Warning: Configuration validation failed: {e}")
