from __future__ import annotations

from typing import Sequence

from openai import OpenAI

from core.config.settings import settings
from core.llm.types import LlmClient, LlmMessage, LlmResponse


class OpenAiClient(LlmClient):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.llm_model

    def generate(self, *, messages: Sequence[LlmMessage], temperature: float = 0.0) -> LlmResponse:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        text = resp.choices[0].message.content or ""
        return LlmResponse(text=text)
