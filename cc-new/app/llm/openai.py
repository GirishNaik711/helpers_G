#app.llm.openai.py
from __future__ import annotations

import json
import os
import httpx

from app.llm.base import LLMProvider
from dotenv import load_dotenv
load_dotenv()

class OpenAIProvider(LLMProvider):
    name = "openai"
    base_url = "https://api.openai.com/v1/chat/completions"

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

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
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }

        r = httpx.post(self.base_url, headers=self._headers(), json=body, timeout=20)
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
        return json.loads(content)

    def judge(self, text: str) -> dict:
        prompt = f"""
Classify the text as PASS or BLOCK for investment advice.

Return ONLY JSON:
{{ "verdict": "PASS" | "BLOCK", "reason": "..." }}

Text:
<<<{text}>>>
"""
        body = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }

        r = httpx.post(self.base_url, headers=self._headers(), json=body, timeout=15)
        r.raise_for_status()
        return json.loads(r.json()["choices"][0]["message"]["content"])
