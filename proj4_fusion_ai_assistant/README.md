# Project 4: Fusion AI Assistant

Long-term starter repository for an Autodesk Fusion add-in that uses OpenAI as a constrained CAD copilot.

## Goals

- Add an in-app chat/palette inside Fusion.
- Translate natural-language requests into structured CAD commands.
- Execute only allowlisted operations.
- Keep changes reviewable with checkpoints and undo support.
- Avoid exposing API keys in source control.

## What is included

- Fusion Python add-in scaffold
- Minimal palette UI shell
- OpenAI API client abstraction
- Structured CAD command schema
- Safe allowlisted command executor
- Undo/checkpoint support
- Logging and config loading
- Example enclosure and parameter-edit commands
- Tests for the command layer and client abstraction

## Repository layout

```text
proj4_fusion_ai_assistant/
├── README.md
├── pyproject.toml
├── fusion_ai_assistant/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── executor.py
│   ├── fusion_addin.py
│   ├── openai_client.py
│   ├── schema.py
│   └── ui.html
└── tests/
    ├── test_executor.py
    ├── test_openai_client.py
    └── test_schema.py
```

## How it works

1. The Fusion add-in opens a palette with a text box.
2. User instructions are sent to the OpenAI client abstraction.
3. The model response is parsed into a strict command schema.
4. The command executor validates each command against an allowlist.
5. The add-in records a checkpoint before applying changes.
6. If something goes wrong, the checkpoint can be rolled back.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/CocoHusky/aI-builder.git
cd aI-builder/proj4_fusion_ai_assistant
git checkout feature/fusion-ai-assistant-starter
```

### 2. Configure secrets

Use environment variables or a local, untracked secrets file.

Supported variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `FUSION_AI_ASSISTANT_LOG_LEVEL`
- `FUSION_AI_ASSISTANT_DEFAULT_UNITS`

Example local file:

```json
{
  "OPENAI_API_KEY": "your-key-here",
  "OPENAI_MODEL": "gpt-4.1-mini",
  "FUSION_AI_ASSISTANT_LOG_LEVEL": "INFO"
}
```

Do not commit real keys.

### 3. Load the add-in in Fusion

Point Fusion at the `fusion_ai_assistant/` package directory using Fusion's add-in loader.

Expected entry points:

- `run(context)`
- `stop(context)`

The scaffold is intentionally small so it can be adapted to your preferred Fusion add-in packaging flow.

### 4. Run tests

```bash
python -m unittest discover -s tests -v
```

## Example commands

The assistant understands a constrained command format such as:

```json
{
  "commands": [
    {
      "type": "create_enclosure",
      "name": "sensor_housing",
      "parameters": {
        "width_mm": 45,
        "height_mm": 32,
        "depth_mm": 10,
        "wall_mm": 1.5,
        "corner_radius_mm": 3
      }
    },
    {
      "type": "update_parameter",
      "target": "battery_clearance_mm",
      "value": 0.8
    }
  ]
}
```

Supported starter commands:

- `create_enclosure`
- `update_parameter`
- `set_component_position`
- `add_checkpoint`
- `undo_to_checkpoint`

## Security cautions

- Keep API keys in environment variables or local secrets only.
- Do not allow arbitrary Python execution from model output.
- Validate every command before touching the Fusion document.
- Require user confirmation for destructive or geometry-wide operations.
- Store logs without secrets or payloads that contain sensitive IP.

## Architecture notes

- `openai_client.py` only handles API transport and response parsing.
- `schema.py` owns the command schema and validation logic.
- `executor.py` converts validated commands into approved Fusion operations.
- `fusion_addin.py` wires the Fusion entry points and UI events.
- `app.py` provides a testable application service for orchestration.

## Roadmap

1. Add real Fusion API adapters for sketches, bodies, assemblies, and parameters.
2. Add richer geometry templates for wearable enclosures and PCB pockets.
3. Add automatic import of PCB STEP packages.
4. Add command previews before execution.
5. Add diff summaries and undo stack integration.
6. Add structured telemetry for reliability and debugging.
7. Add local prompt presets for repeated product categories.
