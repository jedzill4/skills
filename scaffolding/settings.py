"""Validated config: env vars (back-compat) + CLI flag overrides + defaults."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_RAW_BASE = "https://raw.githubusercontent.com/jedzill4/scaffolding/main"


class Settings(BaseSettings):
    """Field names match the legacy env vars case-insensitively.

    e.g. ``agent`` reads ``AGENT``, ``skip_skills`` reads ``SKIP_SKILLS``.
    """

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    agent: str = "opencode"
    assume_yes: bool = False
    with_ci: bool = False
    skip_ci: bool = False
    skip_skills: bool = False
    skip_varlock: bool = False
    no_deps: bool = False
    raw_base: str = DEFAULT_RAW_BASE
