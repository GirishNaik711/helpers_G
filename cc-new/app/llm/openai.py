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

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def realize(self, payload: dict) -> dict:
        prompt = f"""
You are writing educational investment insights.

Rules:
- Use ONLY the provided facts
- No advice or calls to action
- No new data

Return ONLY valid JSON:
{{ "headline": "...", "explanation": "...", "personal_relevance": "..." }}

Facts:
{json.dumps(payload["facts"], indent=2)}

Allowed claims:
{json.dumps(payload["allowed_claims"], indent=2)}
"""

        body = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
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
