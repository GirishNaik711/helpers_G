from __future__ import annotations

from typing import Sequence

import httpx

from core.config.settings import settings
from core.llm.types import LlmClient, LlmMessage, LlmResponse


class OllamaClient(LlmClient):
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self._http = httpx.Client(timeout=60)

    def generate(self, *, messages: Sequence[LlmMessage], temperature: float = 0.0) -> LlmResponse:
        # Ollama chat endpoint
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        r = self._http.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        # Ollama returns: { message: { role, content }, ... }
        text = (data.get("message") or {}).get("content") or ""
        return LlmResponse(text=text)
