# app/llm/anthropic.py
from __future__ import annotations

import json
import os
import httpx

from app.llm.base import LLMProvider


def _strip_code_fences(text: str) -> str:
    """
    Claude often wraps JSON in ```json ... ``` fences. Strip those safely.
    """
    text = (text or "").strip()
    if not text:
        return text

    if text.startswith("```"):
        lines = text.splitlines()

        # Drop opening fence (``` or ```json)
        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        # Drop closing fence
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    return text


class AnthropicProvider(LLMProvider):
    name = "anthropic"
    base_url = "https://api.anthropic.com/v1/messages"

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

    def _headers(self) -> dict:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

    def _extract_text(self, raw: dict) -> str:
        blocks = raw.get("content", [])
        if not blocks or not isinstance(blocks, list):
            return ""
        first = blocks[0] if blocks else {}
        return (first.get("text") or "").strip()

    def realize(self, payload: dict) -> dict:
        prompt = f"""
You generate investor-friendly insights for a wealth app.

Style:
- Concise, confident, consumer-friendly.
- Phrase anything action-ish as educational exploration (e.g., "Some investors explore...", "It may be useful to learn...").
- No direct advice or calls to action (no "you should", no "buy/sell", no "% shift").
- NEVER use these words anywhere: buy, sell, short, long.
- If you would normally use them, replace with neutral phrasing like:
  "increase exposure", "reduce exposure", "positioning", "market sentiment".
- Use ONLY the facts provided. Do not invent numbers.

Return ONLY JSON. The JSON strings must not contain the banned words.


{{ "headline": "...", "explanation": "...", "personal_relevance": "..." }}

Facts:
{json.dumps(payload.get("facts", []), indent=2)}
""".strip()

        body = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
        }

        r = httpx.post(self.base_url, headers=self._headers(), json=body, timeout=20)
        r.raise_for_status()

        raw = r.json()
        text = _strip_code_fences(self._extract_text(raw))

        if not text:
            raise RuntimeError("Anthropic returned empty response")

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON from Anthropic:\n{text}") from e

    def judge(self, text: str) -> dict:
        prompt = f"""
Classify the text as PASS or BLOCK for investment advice.

Return ONLY JSON:
{{ "verdict": "PASS" | "BLOCK", "reason": "..." }}

Text:
<<<{text}>>>
""".strip()

        body = {
            "model": "claude-sonnet-4-5-20250929",
            "max_tokens": 120,
            "messages": [{"role": "user", "content": prompt}],
        }

        r = httpx.post(self.base_url, headers=self._headers(), json=body, timeout=20)
        r.raise_for_status()

        raw = r.json()
        out = _strip_code_fences(self._extract_text(raw))

        if not out:
            return {"verdict": "BLOCK", "reason": "Empty judge output"}

        try:
            parsed = json.loads(out)
        except Exception:
            return {"verdict": "BLOCK", "reason": f"Non-JSON judge output: {out[:200]}"}

        verdict = parsed.get("verdict")
        if verdict not in ("PASS", "BLOCK"):
            return {"verdict": "BLOCK", "reason": "Invalid verdict shape"}
        return parsed
