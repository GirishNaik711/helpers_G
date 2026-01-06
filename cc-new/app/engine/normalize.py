#app/engine/normalize.py
from __future__ import annotations
from datetime import date
from typing import Dict, Any

from app.api.schemas import PipelinePayload


def _calculate_age(dob: date | None) -> int | None:
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def normalize_pipeline_payload(payload: PipelinePayload) -> Dict[str, Any]:
    """
    Converts pipeline payload → normalized context used by insight engine
    """

    tickers = [h.ticker for h in payload.holdings_snapshots]

    total_value = sum(h.current_market_value for h in payload.holdings_snapshots)
    top_holdings = sorted(
        payload.holdings_snapshots,
        key=lambda h: h.current_market_value,
        reverse=True,
    )

    dividend_weighted_yield = (
        sum(h.current_market_value * h.dividend_yield_pct for h in payload.holdings_snapshots)
        / total_value
        if total_value > 0
        else 0
    )

    retirement_goal = next(
        (g for g in payload.goals if g.goal_type.lower() == "retirement"),
        None,
    )

    return {
        "customer_id": payload.user.customer_id,
        "age": _calculate_age(payload.user.date_of_birth),
        "retirement_goal_year": (
            payload.user.retirement_goal_date.year
            if payload.user.retirement_goal_date
            else None
        ),
        "goal_progress_pct": retirement_goal.progress_pct if retirement_goal else None,
        "tickers": tickers,
        "top_holdings": [
            {
                "ticker": h.ticker,
                "value": h.current_market_value,
                "category": h.category,
                "dividend_yield_pct": h.dividend_yield_pct,
            }
            for h in top_holdings[:5]
        ],
        "dividend_profile": {
            "weighted_yield": dividend_weighted_yield,
            "has_dividends": dividend_weighted_yield > 0,
        },
        "inactivity_flag": payload.activity_summary.inactivity_flag,
        "preferred_format": payload.preferences.preferred_insight_format,
    }
