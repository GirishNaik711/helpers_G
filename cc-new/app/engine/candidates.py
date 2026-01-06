#app.engine.candidates.py
from __future__ import annotations
from typing import List, Dict
from app.providers.base import ProviderResponse


def build_candidates(
    provider_payloads: List[ProviderResponse],
) -> List[Dict]:
    candidates = []

    for payload in provider_payloads:
        for item in payload.items:
            candidates.append(
                {
                    "facts": [item.summary],
                    "allowed_claims": [],
                    "citations": payload.citations,
                    "type": item.kind,
                }
            )

    return candidates
