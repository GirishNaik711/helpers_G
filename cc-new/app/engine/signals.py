#app/engine/signals.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from app.providers.base import ProviderResponse


@dataclass
class SignalBundle:
    kind: str  # "goal_portfolio" | "market_trend" | "positions_ticker" | "performance"
    facts: List[str]
    citations: list


def _dedupe_and_cap_citations(citations: list, cap: int = 5) -> list:
    seen = set()
    out = []
    for c in citations:
        key = (getattr(c, "source", None), getattr(c, "title", None), str(getattr(c, "url", "")))
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
        if len(out) >= cap:
            break
    return out


def build_positions_ticker_signals(
    provider_payloads: List[ProviderResponse],
    context: Dict[str, Any],
    focus_ticker: str,
) -> SignalBundle | None:
    facts: List[str] = []
    all_citations = []

    if not focus_ticker:
        return None

    # Pull provider items that are relevant to focus_ticker
    matched_items = []
    for p in provider_payloads:
        all_citations.extend(p.citations or [])
        for it in (p.items or []):
            sym = (it.extra or {}).get("symbol")
            if sym and sym.upper() == focus_ticker.upper():
                matched_items.append(it)
            else:
                # fallback: title/summary contains ticker
                blob = f"{it.title} {it.summary}".lower()
                if focus_ticker.lower() in blob:
                    matched_items.append(it)

    if matched_items:
        facts.append(f"User is viewing ticker {focus_ticker}.")
        facts.append(f"Recent context was found from {len(matched_items)} provider items for {focus_ticker}.")
        # Add up to 3 summaries as facts
        for it in matched_items[:3]:
            if it.summary:
                facts.append(it.summary)

    if not facts:
        return None

    citations = _dedupe_and_cap_citations(all_citations, cap=5)
    return SignalBundle(kind="positions_ticker", facts=facts, citations=citations)


def build_performance_signals(context: Dict[str, Any]) -> SignalBundle:
    """
    MVP: educational performance interpretation using only known context.
    No benchmark math yet.
    """
    facts: List[str] = []
    facts.append("This insight is for interpreting portfolio performance context (educational).")

    total = float(context.get("holdings_total_value") or 0)
    if total > 0:
        facts.append(f"Tracked holdings total value is approximately {total:.0f}.")
    top = context.get("top_holdings") or []
    if top:
        facts.append(f"Top holdings by value include: {', '.join([h['ticker'] for h in top if h.get('ticker')][:5])}.")
        if top[0].get("value") is not None and total > 0:
            pct = (float(top[0]["value"]) / total) * 100
            facts.append(f"Largest holding is about {pct:.0f}% of tracked holdings value.")

    div = context.get("dividend_profile") or {}
    if div.get("has_dividends"):
        facts.append(f"Weighted dividend yield across tracked holdings is ~{div.get('weighted_yield', 0)*100:.2f}%.")

    return SignalBundle(kind="performance", facts=facts, citations=[])

    
                

def build_goal_portfolio_signals(context: Dict[str, Any]) -> SignalBundle:
    """
    ONLY uses user payload-derived context (no external sources).
    Produces stronger 'goal + portfolio framing' facts for the LLM.
    """
    facts: List[str] = []

    # Goal progress framing
    if context.get("goal_progress_pct") is not None:
        facts.append(f"Retirement goal progress is {context['goal_progress_pct']:.0f}%.")

    if context.get("retirement_goal_year"):
        facts.append(f"Retirement goal year is {int(context['retirement_goal_year'])}.")

    # Wealth framing
    if context.get("total_investable_assets") is not None:
        facts.append(f"Total investable assets are approximately {context['total_investable_assets']:.0f}.")

    # Holdings framing
    top = context.get("top_holdings") or []
    if top:
        tickers = [h["ticker"] for h in top if h.get("ticker")]
        facts.append(f"Top holdings by value include: {', '.join(tickers[:5])}.")

        # Concentration
        total_holdings_value = float(context.get("holdings_total_value") or 0)
        if total_holdings_value > 0 and top[0].get("value") is not None:
            pct = (float(top[0]["value"]) / total_holdings_value) * 100
            facts.append(f"Largest holding is about {pct:.0f}% of tracked holdings value.")

    # Dividend profile
    div = context.get("dividend_profile") or {}
    if div.get("has_dividends"):
        facts.append(f"Weighted dividend yield across tracked holdings is ~{div.get('weighted_yield', 0)*100:.2f}%.")

    return SignalBundle(kind="goal_portfolio", facts=facts, citations=[])


def build_market_trend_signals(
    provider_payloads: List[ProviderResponse],
    context: Dict[str, Any],
) -> SignalBundle | None:
    """
    Aggregates Benzinga + AlphaVantage into a single 'dynamic market insight' signal bundle.
    """
    facts: List[str] = []
    all_citations = []

    tickers = set(context.get("tickers") or [])

    # Aggregate Benzinga: simple theme counts (no made-up %)
    benz_items = []
    for p in provider_payloads:
        all_citations.extend(p.citations or [])
        if p.provider == "benzinga":
            benz_items.extend(p.items or [])

    if benz_items:
        facts.append(f"Benzinga returned {len(benz_items)} recent items related to tickers the user holds.")
        # theme hints via keywords
        text_blobs = " ".join([(i.title or "") + " " + (i.summary or "") for i in benz_items]).lower()
        for theme, keywords in [
            ("dividends/income", ["dividend", "yield", "income"]),
            ("ETFs/index exposure", ["etf", "index", "s&p", "vanguard"]),
            ("earnings", ["earnings", "guidance", "revenue"]),
            ("rates/macro", ["rates", "fed", "inflation"]),
        ]:
            if any(k in text_blobs for k in keywords):
                facts.append(f"Recent coverage mentions themes around {theme}.")

        # ticker presence
        mentioned = []
        for t in list(tickers)[:10]:
            if t.lower() in text_blobs:
                mentioned.append(t)
        if mentioned:
            facts.append(f"Tickers referenced in recent items include: {', '.join(mentioned[:5])}.")

    # Aggregate AlphaVantage: price context (range/move)
    av_items = []
    for p in provider_payloads:
        if p.provider == "alphavantage":
            av_items.extend(p.items or [])

    if av_items:
        facts.append(f"Alpha Vantage provided recent price context for {len(av_items)} held tickers.")
        for i in av_items[:3]:
            # i.summary already contains the computed range in your provider
            if i.summary:
                facts.append(i.summary)

    citations = _dedupe_and_cap_citations(all_citations, cap=5)

    if not facts:
        return None

    return SignalBundle(kind="market_trend", facts=facts, citations=citations)

def build_inactive_activation_signals(context: Dict[str, Any]) -> SignalBundle:
    facts: List[str] = []
    facts.append("User archetype is INACTIVE (low recent engagement).")

    if context.get("holdings_count", 0) == 0:
        facts.append("User currently has no tracked positions.")
        facts.append("Educational note: funding an account means adding cash; investing means owning positions like stocks or funds.")
        facts.append("Educational note: diversification refers to spreading exposure across multiple holdings to reduce concentration risk.")
    else:
        holdings_count = context.get("holdings_count")
        facts.append(f"User has {holdings_count} tracked positions.")
        facts.append("Educational note: returning after inactivity often starts with a quick check of goal progress and what you currently hold.")
        facts.append("Educational note: concentration means a large share of tracked value sits in one holding; diversification is spreading exposure across multiple holdings.")

    return SignalBundle(kind="inactive_activation", facts=facts, citations=[])

def build_everyday_performance_signals(context: Dict[str, Any]) -> SignalBundle:
    facts: List[str] = []
    facts.append("User archetype is EVERYDAY (active, non-advanced).")
    facts.append("This insight is educational: how some investors interpret performance versus benchmarks like broad indexes.")
    if context.get("goal_progress_pct") is not None:
        facts.append(f"Retirement goal progress is {context['goal_progress_pct']:.0f}%.")

    top = context.get("top_holdings") or []
    if top:
        facts.append(f"Top holdings by value include: {', '.join([h['ticker'] for h in top if h.get('ticker')][:5])}.")
    return SignalBundle(kind="everyday_performance", facts=facts, citations=[])


def build_everyday_positions_signals(context: Dict[str, Any], focus_ticker: str | None) -> SignalBundle:
    facts: List[str] = []
    facts.append("User archetype is EVERYDAY (active, non-advanced).")
    if focus_ticker:
        facts.append(f"User is viewing ticker {focus_ticker}.")
        facts.append("Educational note: investors often look for what changed (news, earnings, rates) and how it relates to their goals and risk tolerance.")
    else:
        facts.append("User is viewing their positions list.")
        facts.append("Educational note: reviewing concentration and understanding each holding’s role can help interpret day-to-day moves.")
    return SignalBundle(kind="everyday_positions", facts=facts, citations=[])


def build_advanced_performance_signals(context: Dict[str, Any]) -> SignalBundle:
    facts: List[str] = []
    facts.append("User archetype is ADVANCED (experienced investor).")
    facts.append("Educational note: advanced investors often review performance drivers, concentration, and risk exposure across holdings.")
    top = context.get("top_holdings") or []
    if top:
        facts.append(f"Top holdings by value include: {', '.join([h['ticker'] for h in top if h.get('ticker')][:5])}.")
    total = float(context.get("holdings_total_value") or 0)
    if total > 0 and top and top[0].get("value") is not None:
        pct = (float(top[0]["value"]) / total) * 100
        facts.append(f"Largest holding is about {pct:.0f}% of tracked holdings value (concentration signal).")
    return SignalBundle(kind="advanced_performance", facts=facts, citations=[])


def build_advanced_positions_signals(context: Dict[str, Any], focus_ticker: str | None) -> SignalBundle:
    facts: List[str] = []
    facts.append("User archetype is ADVANCED (experienced investor).")
    if focus_ticker:
        facts.append(f"User is viewing ticker {focus_ticker}.")
        facts.append("Educational note: advanced review often includes catalysts (earnings/macro), volatility context, and scenario thinking.")
    else:
        facts.append("User is viewing positions list.")
        facts.append("Educational note: advanced review often includes concentration checks and factor/style exposure awareness.")
    return SignalBundle(kind="advanced_positions", facts=facts, citations=[])


  