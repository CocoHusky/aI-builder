import unittest

from fusion_ai_assistant.schema import CommandSchema, CommandValidationError


class CommandSchemaTests(unittest.TestCase):
    def test_parses_supported_payload(self) -> None:
        schema = CommandSchema.from_payload(
            {
                "commands": [
                    {
                        "type": "create_enclosure",
                        "name": "sensor_housing",
                        "parameters": {"width_mm": 45},
                    }
                ]
            }
        )
        self.assertEqual(list(schema.command_types()), ["create_enclosure"])

    def test_rejects_unknown_command(self) -> None:
        with self.assertRaises(CommandValidationError):
            CommandSchema.from_payload({"commands": [{"type": "delete_everything"}]})


if __name__ == "__main__":
    unittest.main()
