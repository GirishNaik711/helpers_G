"""Anthropic Claude LLM provider for generating financial insights."""
from __future__ import annotations

import json
import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _strip_code_fences(text: str) -> str:
    """Claude often wraps JSON in ```json ... ``` fences. Strip those safely."""
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


class AnthropicLLM:
    """Anthropic Claude API wrapper for generating insights."""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-sonnet-4-5-20250929"

    def __init__(self) -> None:
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.error("ANTHROPIC_API_KEY is not set in environment")
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        logger.debug("AnthropicLLM initialized successfully")

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

    def _call_api(self, prompt: str, max_tokens: int = 300) -> str:
        """Make API call and return extracted text."""
        body = {
            "model": self.MODEL,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        logger.debug(f"Calling Anthropic API with model={self.MODEL}, max_tokens={max_tokens}")
        logger.debug(f"Prompt length: {len(prompt)} chars")

        try:
            r = httpx.post(self.BASE_URL, headers=self._headers(), json=body, timeout=30)
            logger.debug(f"Anthropic API response status: {r.status_code}")

            if r.status_code != 200:
                logger.error(f"Anthropic API error: status={r.status_code}, body={r.text}")

            r.raise_for_status()
            response_json = r.json()
            text = _strip_code_fences(self._extract_text(response_json))
            logger.debug(f"Extracted response text ({len(text)} chars): {text[:200]}...")
            return text
        except httpx.HTTPStatusError as e:
            logger.exception(f"Anthropic HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.exception(f"Anthropic request error: {e}")
            raise

    def generate_insight(self, tickers: list[str], market_data: list[dict]) -> dict:
        """Generate personalized insight for user's tickers."""
        logger.info(f"Generating insight for tickers: {tickers}")
        logger.debug(f"Market data: {market_data}")

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

Return ONLY JSON with this structure:
{{ "headline": "...", "explanation": "...", "personal_relevance": "..." }}

User's Holdings: {', '.join(tickers)}

Market Data:
{json.dumps(market_data, indent=2)}
""".strip()

        text = self._call_api(prompt)
        if not text:
            logger.error("Anthropic returned empty response")
            raise RuntimeError("Anthropic returned empty response")

        try:
            result = json.loads(text)
            logger.info("Successfully parsed JSON response from Anthropic")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Anthropic: {text}")
            raise RuntimeError(f"Invalid JSON from Anthropic:\n{text}") from e
