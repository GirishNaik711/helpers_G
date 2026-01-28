"""FastAPI application with financial insights endpoints."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llm import AnthropicLLM
from market_data import AlphaVantageClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Financial Insights API", version="1.0.0")


# --- Request/Response Models ---

class GenerateRequest(BaseModel):
    account_id: str
    tickers: list[str]


class InsightResponse(BaseModel):
    account_id: str
    headline: str
    explanation: str
    personal_relevance: str


class ZeroBalanceRequest(BaseModel):
    account_id: str
    last_activity_date: Optional[str] = None


class ZeroBalanceResponse(BaseModel):
    account_id: str
    message: str
    suggestions: list[dict]


# --- Helper Functions ---

def load_static_tickers() -> list[dict]:
    """Load top tickers from static file."""
    static_file = Path("static_top_tickers.txt")
    if not static_file.exists():
        logger.warning(f"Static tickers file not found at {static_file.absolute()}")
        return []

    entries = []
    with static_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split("|")]
            entries.append({
                "symbol": parts[0].upper(),
                "name": parts[1] if len(parts) > 1 else parts[0],
                "change": parts[2] if len(parts) > 2 else "",
                "note": parts[3] if len(parts) > 3 else "strong recent momentum"
            })
    logger.debug(f"Loaded {len(entries)} static tickers")
    return entries


def calculate_inactive_months(last_activity: str | None) -> int | None:
    """Calculate months of inactivity."""
    if not last_activity:
        return None
    try:
        last_dt = datetime.fromisoformat(last_activity.replace("Z", "+00:00"))
        days = (datetime.now(last_dt.tzinfo) - last_dt).days
        return max(1, days // 30)
    except Exception as e:
        logger.warning(f"Failed to parse last_activity_date '{last_activity}': {e}")
        return None


# --- Endpoints ---

@app.post("/generate", response_model=InsightResponse)
def generate_insight(request: GenerateRequest):
    """Generate personalized insights for users with holdings."""
    logger.info(f"[/generate] account_id={request.account_id}, tickers={request.tickers}")

    if not request.tickers:
        logger.warning(f"[/generate] No tickers provided for account {request.account_id}")
        raise HTTPException(status_code=400, detail="No tickers provided")

    try:
        # Fetch market data
        logger.debug(f"[/generate] Fetching market data for tickers: {request.tickers}")
        market_client = AlphaVantageClient()
        market_data = market_client.get_price_data(request.tickers)
        logger.debug(f"[/generate] Market data received: {market_data}")

        # Generate insight using LLM
        logger.debug("[/generate] Calling Anthropic LLM...")
        llm = AnthropicLLM()
        insight = llm.generate_insight(request.tickers, market_data)
        logger.info(f"[/generate] Insight generated successfully for {request.account_id}")
        logger.debug(f"[/generate] Insight content: {insight}")

        return InsightResponse(
            account_id=request.account_id,
            headline=insight.get("headline", ""),
            explanation=insight.get("explanation", ""),
            personal_relevance=insight.get("personal_relevance", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"[/generate] Error generating insight for {request.account_id}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/zero_balance_suggestion", response_model=ZeroBalanceResponse)
def zero_balance_suggestion(request: ZeroBalanceRequest):
    """Generate suggestions for zero-balance/dormant users using static top tickers."""
    logger.info(f"[/zero_balance_suggestion] account_id={request.account_id}")

    entries = load_static_tickers()
    if not entries:
        logger.error("[/zero_balance_suggestion] Static tickers file not found or empty")
        raise HTTPException(status_code=500, detail="Static tickers file not found")

    top_3 = entries[:3]

    # Build personalized message
    months = calculate_inactive_months(request.last_activity_date)
    if months:
        month_label = "months" if months > 1 else "month"
        header = (
            f"We noticed you haven't been active for about {months} {month_label}. "
            "Here are three stocks that have been performing well recently to help you get back into the flow."
        )
    else:
        header = (
            "Welcome back! Here are three stocks that have been performing well recently "
            "to help you get back into the flow."
        )

    suggestions = []
    for e in top_3:
        suggestions.append({
            "symbol": e["symbol"],
            "name": e["name"],
            "change": e["change"],
            "note": e["note"],
            "display": f"{e['symbol']} ({e['name']}) - {e['note']} {e['change']}"
        })

    logger.info(f"[/zero_balance_suggestion] Returning {len(suggestions)} suggestions")
    return ZeroBalanceResponse(
        account_id=request.account_id,
        message=header,
        suggestions=suggestions
    )


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
