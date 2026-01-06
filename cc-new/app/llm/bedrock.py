#app.llm.bedrock.py
from __future__ import annotations

import json
import boto3

from app.llm.base import LLMProvider
from app.core.config import settings


class BedrockProvider(LLMProvider):
    name = "bedrock"

    def __init__(self) -> None:
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
        )
        self.model_id = settings.bedrock_model_id

    def realize(self, payload: dict) -> dict:
        prompt = f"""
You are writing educational investment insights.

Rules:
- Use ONLY provided facts
- No advice
- No new data

Return ONLY JSON:
{{ "headline": "...", "explanation": "...", "personal_relevance": "..." }}

Facts:
{json.dumps(payload["facts"], indent=2)}

Allowed claims:
{json.dumps(payload["allowed_claims"], indent=2)}
"""

        body = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
        }

        resp = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
        )

        text = json.loads(resp["body"].read())["content"][0]["text"]
        return json.loads(text)

    def judge(self, text: str) -> dict:
        prompt = f"""
Is the following investment education text compliant?

Return ONLY JSON:
{{ "verdict": "PASS" | "BLOCK", "reason": "..." }}

Text:
<<<{text}>>>
"""

        body = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
        }

        resp = self.client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(body),
        )

        text = json.loads(resp["body"].read())["content"][0]["text"]
        return json.loads(text)
