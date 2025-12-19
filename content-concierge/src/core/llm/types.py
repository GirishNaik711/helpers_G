from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence


Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class LlmMessage:
    role: Role
    content: str


@dataclass(frozen=True)
class LlmResponse:
    text: str


class LlmClient:
    """
    Minimal interface: both OpenAI and Ollama implement this.
    """

    def generate(self, *, messages: Sequence[LlmMessage], temperature: float = 0.0) -> LlmResponse:
        raise NotImplementedError
