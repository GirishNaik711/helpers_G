from __future__ import annotations

INSIGHT_HYPOTHESIS_SYSTEM = """You propose insight THEMES only for a wealth app content concierge.
Do not provide advice, recommendations, or predictions.
Return concise JSON only as specified."""

INSIGHT_HYPOTHESIS_USER = """Given this user context, propose 3-5 insight themes (no factual claims).
UserContext (summary):
- Portfolio tickers: {tickers}
- Top holdings: {top_holdings}
- Goal types: {goal_types}
- Inactivity flag: {inactive}

Output JSON:
{{
  "themes": ["..."]
}}
"""

INSIGHT_SYNTHESIS_SYSTEM = """You generate 2-3 educational, non-prescriptive insights.
You MUST ground external statements only in the provided sources.
Do not fabricate numbers or claims.
Return JSON only as specified."""

INSIGHT_SYNTHESIS_USER = """Create 2-3 insights following this structure:
- headline (single takeaway)
- explanation (2-3 short sentences)
- personal_relevance (why it matters for this user's portfolio/goals/inactivity)
Do NOT use prescriptive language.

UserContext:
{user_context}

MarketData:
{market_data}

NewsItems:
{news_items}

Output JSON:
{{
  "insights": [
    {{
      "headline": "...",
      "explanation": "...",
      "personal_relevance": "..."
    }}
  ]
}}
"""
