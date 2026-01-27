# app/engine/normalize.py

from __future__ import annotations
from datetime import date
from typing import Any, Dict
from datetime import datetime
from app.api.schemas import PipelinePayload


def _compute_inactivity_flag(last_login_at: datetime | None) -> bool:
    """Returns True if last login > 6 months ago"""
    if not last_login_at:
        return True
    from datetime import timedelta, timezone
    
    # Make both timezone-aware for comparison
    now = datetime.now(timezone.utc)
    if last_login_at.tzinfo is None:
        last_login_at = last_login_at.replace(tzinfo=timezone.utc)
    
    six_months_ago = now - timedelta(days=180)
    return last_login_at < six_months_ago

def _calculate_age(dob: date | None) -> int | None:
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def _tier(total_assets: float | None) -> str | None:
    if total_assets is None:
        return None
    if total_assets < 250_000:
        return "UNDER_250K"
    if total_assets < 1_000_000:
        return "FROM_250K_TO_1M"
    return "OVER_1M"

def _archetype(payload: PipelinePayload) -> str:
    
    
    lvl = (payload.user.investment_experience_level or "").strip().lower()
    if lvl =="advanced":
        return "ADVANCED"
    
    return "EVERYDAY"

def normalize_pipeline_payload(payload: PipelinePayload) -> Dict[str, Any]:
    """
    Converts pipeline payload -> normalized context used by the insight engine.
    """
    tickers = [h.ticker for h in payload.holdings_snapshots]

    total_value = sum(h.current_market_value for h in payload.holdings_snapshots)
    top_holdings = sorted(
        payload.holdings_snapshots,
        key=lambda h: h.current_market_value,
        reverse=True,
    )

    dividend_weighted_yield = (
        sum(h.current_market_value * h.dividend_yield_pct for h in payload.holdings_snapshots) / total_value
        if total_value > 0
        else 0
    )

    retirement_goal = next(
        (g for g in payload.goals if (g.goal_type or "").lower() == "retirement"),
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
        "holdings_total_value": total_value,
        "total_investable_assets": payload.wealth_snapshot.total_investable_assets,
        "dividend_profile": {
            "weighted_yield": dividend_weighted_yield,
            "has_dividends": dividend_weighted_yield > 0,
        },
        "inactivity_flag": _compute_inactivity_flag(payload.activity_summary.last_login_at),
        "preferred_format": payload.preferences.preferred_insight_format,
        "tier": _tier(payload.wealth_snapshot.total_investable_assets),
        "archetype": _archetype(payload),
        "holdings_count": len(payload.holdings_snapshots),
        "has_positions": len(payload.holdings_snapshots) > 0,
        }
