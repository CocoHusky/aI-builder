import unittest

from fusion_ai_assistant.openai_client import OpenAIClient


class OpenAIClientTests(unittest.TestCase):
    def test_extract_schema_from_response(self) -> None:
        response = {
            "output": [
                {
                    "content": [
                        {
                            "text": '{"commands":[{"type":"update_parameter","target":"wall_mm","value":1.5}]}'
                        }
                    ]
                }
            ]
        }
        schema = OpenAIClient._extract_schema(response)
        self.assertEqual(schema.as_dict()["commands"][0]["type"], "update_parameter")


if __name__ == "__main__":
    unittest.main()
