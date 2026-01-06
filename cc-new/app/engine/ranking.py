#app.engine.ranking.py
from __future__ import annotations

from typing import List, Tuple


def rank_candidates(
    candidates: List[Tuple[str, str, list]],
    limit: int,
) -> List[Tuple[str, str, list]]:
    """
    MVP ranking:
    - De-duplicate by headline
    - Preserve order (providers already sorted by recency)
    """
    seen = set()
    ranked = []

    for h, e, c in candidates:
        if h in seen:
            continue
        seen.add(h)
        ranked.append((h, e, c))
        if len(ranked) >= limit:
            break

    return ranked
