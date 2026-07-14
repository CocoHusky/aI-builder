"""Fusion entry points for the add-in."""

from __future__ import annotations

from dataclasses import dataclass

from .app import FusionAIAssistantApp


@dataclass
class AddInState:
    app: FusionAIAssistantApp
    running: bool = False


STATE: AddInState | None = None


def run(context) -> None:  # Fusion calls this entry point.
    global STATE
    STATE = AddInState(app=FusionAIAssistantApp(), running=True)
    _ = context


def stop(context) -> None:  # Fusion calls this entry point.
    global STATE
    if STATE is not None:
        STATE.running = False
    STATE = None
    _ = context
