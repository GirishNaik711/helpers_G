#app.llm.base.py
from __future__ import annotations
from typing import Protocol, Dict, Any


class LLMProvider(Protocol):
    name: str
    def realize(self, payload: Dict[str, Any]) -> Dict[str, str]: ...
    def judge(self, text: str) -> Dict[str, str]: ...
