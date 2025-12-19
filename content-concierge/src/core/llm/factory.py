from __future__ import annotations

from core.config.settings import settings
from core.llm.openai_client import OpenAiClient
from core.llm.ollama_client import OllamaClient
from core.llm.types import LlmClient


def get_llm_client() -> LlmClient:
    provider = (settings.llm_provider or "").strip().lower()
    if provider == "openai":
        return OpenAiClient()
    if provider == "ollama":
        return OllamaClient()
    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
