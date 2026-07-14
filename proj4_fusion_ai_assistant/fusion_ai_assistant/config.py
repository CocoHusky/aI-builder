"""Configuration helpers for the Fusion AI Assistant."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    log_level: str
    default_units: str


def load_local_secrets(path: str | Path | None = None) -> dict[str, Any]:
    if path is None:
        return {}
    secret_path = Path(path)
    if not secret_path.exists():
        return {}
    return json.loads(secret_path.read_text(encoding="utf-8"))


def load_settings() -> Settings:
    local_secrets = load_local_secrets(os.environ.get("FUSION_AI_ASSISTANT_SECRETS"))
    return Settings(
        openai_api_key=os.environ.get("OPENAI_API_KEY") or local_secrets.get("OPENAI_API_KEY"),
        openai_model=os.environ.get("OPENAI_MODEL")
        or local_secrets.get("OPENAI_MODEL")
        or "gpt-4.1-mini",
        log_level=os.environ.get("FUSION_AI_ASSISTANT_LOG_LEVEL")
        or local_secrets.get("FUSION_AI_ASSISTANT_LOG_LEVEL")
        or "INFO",
        default_units=os.environ.get("FUSION_AI_ASSISTANT_DEFAULT_UNITS")
        or local_secrets.get("FUSION_AI_ASSISTANT_DEFAULT_UNITS")
        or "mm",
    )
