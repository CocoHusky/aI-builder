"""OpenAI API transport abstraction."""

from __future__ import annotations

from dataclasses import dataclass
import json
from urllib import request

from .schema import CommandSchema, CommandValidationError


class OpenAIClientError(RuntimeError):
    """Raised when API calls or response parsing fails."""


@dataclass
class OpenAIClient:
    api_key: str
    model: str
    endpoint: str = "https://api.openai.com/v1/responses"

    def generate_commands(self, prompt: str, context: dict[str, object] | None = None) -> CommandSchema:
        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": "Return only JSON matching {\"commands\": [...]} for CAD operations.",
                },
                {
                    "role": "user",
                    "content": json.dumps({"prompt": prompt, "context": context or {}}, sort_keys=True),
                },
            ],
        }
        raw_response = self._post_json(payload)
        return self._extract_schema(raw_response)

    def _post_json(self, payload: dict[str, object]) -> dict[str, object]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - network path
            raise OpenAIClientError("OpenAI request failed.") from exc

    @staticmethod
    def _extract_schema(response: dict[str, object]) -> CommandSchema:
        try:
            output = response["output"]
            first_item = output[0]
            content = first_item["content"][0]
            text = content["text"]
            parsed = json.loads(text)
            return CommandSchema.from_payload(parsed)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise OpenAIClientError("OpenAI response did not contain valid command JSON.") from exc
        except CommandValidationError as exc:
            raise OpenAIClientError(str(exc)) from exc
