"""Alpha Vantage market data provider."""
from __future__ import annotations

import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """Fetch stock price data from Alpha Vantage API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self) -> None:
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        if self.api_key:
            logger.debug("AlphaVantageClient initialized with API key")
        else:
            logger.warning("ALPHAVANTAGE_API_KEY not set - market data will be unavailable")

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def get_price_data(self, tickers: list[str]) -> list[dict]:
        """Fetch recent price data for given tickers."""
        logger.info(f"Fetching price data for tickers: {tickers}")

        if not self.api_key:
            logger.error("Alpha Vantage API key not configured")
            return [{"error": "Alpha Vantage API key not configured"}]

        results = []
        for symbol in tickers[:5]:  # Limit to 5 tickers
            symbol = symbol.strip().upper()
            if not symbol:
                continue

            logger.debug(f"Fetching data for symbol: {symbol}")
            try:
                params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": symbol,
                    "outputsize": "compact",
                    "apikey": self.api_key,
                }
                r = httpx.get(self.BASE_URL, params=params, timeout=15)
                logger.debug(f"Alpha Vantage response for {symbol}: status={r.status_code}")

                if r.status_code != 200:
                    logger.error(f"Alpha Vantage error for {symbol}: {r.status_code} - {r.text}")

                r.raise_for_status()
                data = r.json()

                # Check for API error messages
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage API error for {symbol}: {data['Error Message']}")
                    results.append({"symbol": symbol, "error": data["Error Message"]})
                    continue

                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit note: {data['Note']}")
                    results.append({"symbol": symbol, "error": "Rate limit reached"})
                    continue

                series = data.get("Time Series (Daily)", {})
                if not series:
                    logger.warning(f"No time series data for {symbol}")
                    results.append({"symbol": symbol, "error": "No data available"})
                    continue

                dates = sorted(series.keys(), reverse=True)[:5]
                closes = [float(series[d]["4. close"]) for d in dates]
                min_c, max_c = min(closes), max(closes)
                latest = closes[0]
                prev = closes[1] if len(closes) > 1 else closes[0]
                change_pct = ((latest - prev) / prev * 100) if prev else 0

                result = {
                    "symbol": symbol,
                    "latest_price": round(latest, 2),
                    "change_pct": round(change_pct, 2),
                    "range_low": round(min_c, 2),
                    "range_high": round(max_c, 2),
                    "summary": f"{symbol} recently traded between ${min_c:.2f} and ${max_c:.2f}"
                }
                logger.debug(f"Fetched data for {symbol}: {result}")
                results.append(result)

            except httpx.HTTPStatusError as e:
                logger.exception(f"HTTP error fetching {symbol}: {e}")
                results.append({"symbol": symbol, "error": str(e)})
            except httpx.RequestError as e:
                logger.exception(f"Request error fetching {symbol}: {e}")
                results.append({"symbol": symbol, "error": str(e)})
            except Exception as e:
                logger.exception(f"Unexpected error fetching {symbol}: {e}")
                results.append({"symbol": symbol, "error": str(e)})

        logger.info(f"Completed fetching data for {len(results)} tickers")
        return results
