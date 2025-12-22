from __future__ import annotations

from anthropic import Anthropic
from core.llm.types import LlmClient, LlmMessage
from core.config.settings import settings


class AnthropicClient(LlmClient):
    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def generate(self, messages: list[LlmMessage], temperature: float = 0.0):
        system = ""
        prompt = []

        for m in messages:
            if m.role == "system":
                system += m.content + "\n"
            else:
                prompt.append({"role": m.role, "content": m.content})

        resp = self.client.messages.create(
            model=self.model,
            system=system.strip() or None,
            messages=prompt,
            temperature=temperature,
            max_tokens=1024,
        )

        return type(
            "LLMResponse",
            (),
            {"text": resp.content[0].text},
        )()
