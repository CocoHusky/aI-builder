"""Orchestration layer for the Fusion AI Assistant."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .config import Settings, load_settings
from .executor import CommandExecutor, ExecutionResult, FusionDocument
from .openai_client import OpenAIClient
from .schema import CommandSchema


@dataclass
class FusionAIAssistantApp:
    settings: Settings | None = None
    document: FusionDocument | None = None
    client: OpenAIClient | None = None
    executor: CommandExecutor | None = None

    def __post_init__(self) -> None:
        self.settings = self.settings or load_settings()
        logging.basicConfig(level=getattr(logging, self.settings.log_level.upper(), logging.INFO))
        if self.client is None and self.settings.openai_api_key:
            self.client = OpenAIClient(
                api_key=self.settings.openai_api_key,
                model=self.settings.openai_model,
            )
        if self.document is not None and self.executor is None:
            self.executor = CommandExecutor(self.document)

    def handle_prompt(self, prompt: str, context: dict[str, Any] | None = None) -> ExecutionResult:
        if self.client is None:
            raise RuntimeError("OpenAI client is not configured.")
        if self.executor is None:
            raise RuntimeError("Fusion document executor is not configured.")
        schema = self.client.generate_commands(prompt, context=context)
        return self.executor.execute(schema)

    def execute_schema(self, schema: CommandSchema) -> ExecutionResult:
        if self.executor is None:
            raise RuntimeError("Fusion document executor is not configured.")
        return self.executor.execute(schema)
