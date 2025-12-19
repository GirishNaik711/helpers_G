from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


PRESCRIPTIVE_PATTERNS = [
    r"\bshould buy\b",
    r"\bshould sell\b",
    r"\bbuy now\b",
    r"\bsell now\b",
    r"\brecommend\b",
    r"\byou should\b",
    r"\bstrong buy\b",
    r"\bstrong sell\b",
    r"\btarget price\b",
]

PRESCRIPTIVE_RE = re.compile("|".join(PRESCRIPTIVE_PATTERNS), re.IGNORECASE)


@dataclass(frozen=True)
class GuardrailResult:
    ok: bool
    reasons: list[str]


def check_non_prescriptive(text: str) -> GuardrailResult:
    if PRESCRIPTIVE_RE.search(text):
        return GuardrailResult(ok=False, reasons=["Prescriptive/advice-like language detected"])
    return GuardrailResult(ok=True, reasons=[])


def require_citations_for_external_claims(insights: Iterable[dict]) -> GuardrailResult:
    """
    Minimal PoC rule:
    - every insight must have >= 1 source
    (later we’ll map claims to citations; this keeps PoC safe)
    """
    missing = []
    for i, ins in enumerate(insights):
        if not ins.get("sources"):
            missing.append(f"insight[{i}] missing sources")
    if missing:
        return GuardrailResult(ok=False, reasons=missing)
    return GuardrailResult(ok=True, reasons=[])
