"""Structured command schema for AI-generated CAD actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


class CommandValidationError(ValueError):
    """Raised when a command payload is malformed or disallowed."""


ALLOWED_COMMAND_TYPES = {
    "add_checkpoint",
    "create_enclosure",
    "set_component_position",
    "undo_to_checkpoint",
    "update_parameter",
}


@dataclass(frozen=True)
class CadCommand:
    type: str
    args: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CommandSchema:
    commands: list[CadCommand]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CommandSchema":
        commands = payload.get("commands")
        if not isinstance(commands, list) or not commands:
            raise CommandValidationError("Payload must include a non-empty 'commands' list.")
        parsed_commands = [cls._parse_command(command) for command in commands]
        return cls(commands=parsed_commands)

    @staticmethod
    def _parse_command(command: dict[str, Any]) -> CadCommand:
        if not isinstance(command, dict):
            raise CommandValidationError("Each command must be an object.")
        command_type = command.get("type")
        if command_type not in ALLOWED_COMMAND_TYPES:
            raise CommandValidationError(f"Unsupported command type: {command_type!r}")
        args = {key: value for key, value in command.items() if key != "type"}
        return CadCommand(type=command_type, args=args)

    def as_dict(self) -> dict[str, Any]:
        return {"commands": [{"type": command.type, **command.args} for command in self.commands]}

    def command_types(self) -> Iterable[str]:
        return (command.type for command in self.commands)
