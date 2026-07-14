import unittest

from fusion_ai_assistant.executor import CommandExecutor
from fusion_ai_assistant.schema import CommandSchema


class FakeDocument:
    def __init__(self) -> None:
        self.calls = []
        self.parameters = {}

    def create_checkpoint(self, name: str) -> str:
        self.calls.append(("create_checkpoint", name))
        return f"checkpoint:{name}"

    def restore_checkpoint(self, checkpoint_id: str) -> None:
        self.calls.append(("restore_checkpoint", checkpoint_id))

    def set_parameter(self, name: str, value):
        self.calls.append(("set_parameter", name, value))
        self.parameters[name] = value

    def create_enclosure(self, **kwargs):
        self.calls.append(("create_enclosure", kwargs))
        return "enclosure:1"

    def set_component_position(self, component: str, x_mm: float, y_mm: float, z_mm: float) -> None:
        self.calls.append(("set_component_position", component, x_mm, y_mm, z_mm))


class ExecutorTests(unittest.TestCase):
    def test_executes_allowlisted_commands(self) -> None:
        document = FakeDocument()
        executor = CommandExecutor(document)
        schema = CommandSchema.from_payload(
            {
                "commands": [
                    {"type": "add_checkpoint", "name": "before-enclosure"},
                    {
                        "type": "create_enclosure",
                        "parameters": {"width_mm": 45, "height_mm": 32, "depth_mm": 10},
                    },
                    {"type": "update_parameter", "target": "wall_mm", "value": 1.5},
                ]
            }
        )
        result = executor.execute(schema)
        self.assertEqual(result.checkpoint_id, "checkpoint:before-enclosure")
        self.assertEqual(result.applied_commands, ["add_checkpoint", "create_enclosure", "update_parameter"])
        self.assertIn(("set_parameter", "wall_mm", 1.5), document.calls)


if __name__ == "__main__":
    unittest.main()
