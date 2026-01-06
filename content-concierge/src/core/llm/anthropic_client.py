# app/llm/anthropic.py
from __future__ import annotations

import json
from typing import Any, Dict

from anthropic import Anthropic

from app.llm.base import LLMProvider
from app.core.config import settings


def _strip_code_fences(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return text
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        # Keep your current default; make configurable later if you want
        self.model = getattr(settings, "anthropic_model", None) or "claude-3-5-sonnet-20240620"

    def _parse_json(self, text: str) -> Dict[str, Any]:
        text = _strip_code_fences(text)
        if not text:
            raise RuntimeError("Anthropic returned empty response text")
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from Anthropic:\n{text}") from e

    def realize(self, payload: dict) -> dict:
        prompt = f"""
You are writing personalized investment insights in a neutral, educational-exploration style.

Rules:
- Use ONLY the provided facts.
- Treat analyst ratings/price targets as market context, not recommendations.
- Do NOT give advice or calls to action (no “you should”, no “buy/sell”, no “shift X%”).
- Do NOT add new data or claims.

Return ONLY valid JSON (no markdown fences):
{{
  "headline": "...",
  "explanation": "...",
  "personal_relevance": "..."
}}

Facts:
{json.dumps(payload.get("facts", []), indent=2)}
""".strip()

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=300,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )

        text = resp.content[0].text if resp.content else ""
        return self._parse_json(text)

    def judge(self, text: str) -> dict:
        prompt = f"""
You are a compliance reviewer for an investment education product.

Rules:
- Educational explanations are allowed.
- Any advice/call-to-action is NOT allowed (even soft suggestions like “consider”).
- Analyst ratings/price targets are allowed only as market context.

Return ONLY valid JSON (no markdown fences):
{{ "verdict": "PASS" | "BLOCK", "reason": "..." }}

Text:
<<<{text}>>>
""".strip()

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=120,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )

        out = resp.content[0].text if resp.content else ""
        try:
            parsed = self._parse_json(out)
        except Exception:
            return {"verdict": "BLOCK", "reason": "Invalid judge output"}

        if parsed.get("verdict") not in ("PASS", "BLOCK"):
            return {"verdict": "BLOCK", "reason": "Invalid verdict shape"}
        return parsed
