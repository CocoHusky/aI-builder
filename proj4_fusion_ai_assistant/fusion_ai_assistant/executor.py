"""Allowlisted executor for AI-generated CAD commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .schema import CadCommand, CommandSchema, CommandValidationError


class FusionDocument(Protocol):
    """Minimal document API required by the starter executor."""

    def create_checkpoint(self, name: str) -> str: ...

    def restore_checkpoint(self, checkpoint_id: str) -> None: ...

    def set_parameter(self, name: str, value: float | int | str) -> None: ...

    def create_enclosure(self, **kwargs: Any) -> str: ...

    def set_component_position(self, component: str, x_mm: float, y_mm: float, z_mm: float) -> None: ...


@dataclass
class ExecutionResult:
    checkpoint_id: str | None
    applied_commands: list[str] = field(default_factory=list)


class CommandExecutor:
    """Validate and apply a restricted set of CAD commands."""

    def __init__(self, document: FusionDocument) -> None:
        self._document = document

    def execute(self, schema: CommandSchema) -> ExecutionResult:
        checkpoint_id: str | None = None
        applied: list[str] = []
        for command in schema.commands:
            if command.type == "add_checkpoint":
                checkpoint_id = self._document.create_checkpoint(
                    str(command.args.get("name", "ai-checkpoint"))
                )
                applied.append(command.type)
                continue
            if command.type == "undo_to_checkpoint":
                self._restore_checkpoint(command)
                applied.append(command.type)
                continue
            if checkpoint_id is None:
                checkpoint_id = self._document.create_checkpoint("ai-preflight")
            self._execute_command(command)
            applied.append(command.type)
        return ExecutionResult(checkpoint_id=checkpoint_id, applied_commands=applied)

    def _execute_command(self, command: CadCommand) -> None:
        if command.type == "create_enclosure":
            self._document.create_enclosure(**self._require_mapping(command))
            return
        if command.type == "update_parameter":
            self._document.set_parameter(
                str(command.args["target"]),
                command.args["value"],
            )
            return
        if command.type == "set_component_position":
            self._document.set_component_position(
                str(command.args["component"]),
                float(command.args["x_mm"]),
                float(command.args["y_mm"]),
                float(command.args["z_mm"]),
            )
            return
        raise CommandValidationError(f"Command is not executable: {command.type}")

    def _restore_checkpoint(self, command: CadCommand) -> None:
        checkpoint_id = command.args.get("checkpoint_id")
        if not checkpoint_id:
            raise CommandValidationError("'undo_to_checkpoint' requires 'checkpoint_id'.")
        self._document.restore_checkpoint(str(checkpoint_id))

    @staticmethod
    def _require_mapping(command: CadCommand) -> dict[str, Any]:
        params = command.args.get("parameters")
        if not isinstance(params, dict):
            raise CommandValidationError("'create_enclosure' requires a 'parameters' object.")
        return params
