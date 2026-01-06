#app.core.safety.py

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


DEFAULT_BANNED_PATTERNS: list[re.Pattern] = [
    re.compile(r"\b(buy|sell|short|long)\b", re.IGNORECASE),
    re.compile(r"\b(allocate|reallocate|rebalance|shift\s+\d+%|move\s+\d+%)\b", re.IGNORECASE),
    re.compile(r"\b(you should|we recommend|do this now|must)\b", re.IGNORECASE),
]


@dataclass(frozen=True)
class SafetyResult:
    ok: bool
    reasons: list[str]


def check_non_advisory(texts: Iterable[str]) -> SafetyResult:
    reasons: list[str] = []
    for t in texts:
        for pat in DEFAULT_BANNED_PATTERNS:
            if pat.search(t or ""):
                reasons.append(f"Blocked pattern: {pat.pattern}")
    return SafetyResult(ok=(len(reasons) == 0), reasons=reasons)


def enforce_non_advisory_or_raise(texts: Iterable[str]) -> None:
    res = check_non_advisory(texts)
    if not res.ok:
        raise ValueError("Non-advisory policy violation: " + "; ".join(res.reasons))
