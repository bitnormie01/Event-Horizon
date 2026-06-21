"""Data ingress clients for live CMC API integration.

These clients wrap CoinMarketCap API endpoints for live-mode operation.
In fixture mode (default), FixtureStore is used instead and these clients
are not invoked. No CMC credentials are required for fixture mode.

To use live mode, set the CMC_API_KEY environment variable.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass

from src.models import MacroEvent

_BASE_URL = "https://pro-api.coinmarketcap.com"


@dataclass(frozen=True)
class TokenQuote:
    """A token price quote from CMC."""

    symbol: str
    price_usd: float
    volume_24h: float
    percent_change_24h: float
    market_cap: float
    last_updated: str


@dataclass(frozen=True)
class NewsItem:
    """A news item from CMC."""

    title: str
    date: str
    summary: str


def _api_get(api_key: str, path: str, params: dict[str, str] | None = None) -> dict:
    """Make a GET request to the CMC API."""
    url = f"{_BASE_URL}{path}"
    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query}"
    req = urllib.request.Request(
        url,
        headers={"X-CMC_PRO_API_KEY": api_key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


class EventClient:
    """Wraps CMC API for event-related data.

    The CMC standard API does not expose a dedicated macro-events endpoint,
    so this client uses global metrics and market data as proxy signals.
    For fixture mode, FixtureStore provides the event calendar directly.
    """

    def __init__(self) -> None:
        self._api_key = os.environ.get("CMC_API_KEY", "")

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_upcoming_events(self) -> list[MacroEvent]:
        """Return macro events. Live CMC API does not have a dedicated events endpoint.

        Returns an empty list -- the fixture store should be used for event data.
        When CMC MCP's get_upcoming_macro_events becomes available, this method
        will be wired to call it.
        """
        return []

    def get_global_metrics(self) -> dict | None:
        """Fetch global crypto market metrics as context for event analysis."""
        if not self.is_available:
            return None
        try:
            data = _api_get(self._api_key, "/v1/global-metrics/quotes/latest")
            return data.get("data", {})
        except Exception:
            return None


class QuoteClient:
    """Wraps CMC API get_crypto_quotes_latest.

    Returns TokenQuote for requested symbols.
    """

    def __init__(self) -> None:
        self._api_key = os.environ.get("CMC_API_KEY", "")

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_quote(self, symbol: str = "BTC") -> TokenQuote | None:
        """Fetch latest quote for a token from CMC API."""
        if not self.is_available:
            return None
        try:
            data = _api_get(
                self._api_key,
                "/v1/cryptocurrency/quotes/latest",
                {"symbol": symbol},
            )
            coin_data = data.get("data", {}).get(symbol)
            if not coin_data:
                return None
            usd = coin_data["quote"]["USD"]
            return TokenQuote(
                symbol=symbol,
                price_usd=usd["price"],
                volume_24h=usd["volume_24h"],
                percent_change_24h=usd["percent_change_24h"],
                market_cap=usd["market_cap"],
                last_updated=usd["last_updated"],
            )
        except Exception:
            return None

    def get_quotes_multi(self, symbols: list[str]) -> list[TokenQuote]:
        """Fetch latest quotes for multiple tokens."""
        if not self.is_available:
            return []
        try:
            data = _api_get(
                self._api_key,
                "/v1/cryptocurrency/quotes/latest",
                {"symbol": ",".join(symbols)},
            )
            results = []
            for sym in symbols:
                coin_data = data.get("data", {}).get(sym)
                if coin_data:
                    usd = coin_data["quote"]["USD"]
                    results.append(
                        TokenQuote(
                            symbol=sym,
                            price_usd=usd["price"],
                            volume_24h=usd["volume_24h"],
                            percent_change_24h=usd["percent_change_24h"],
                            market_cap=usd["market_cap"],
                            last_updated=usd["last_updated"],
                        )
                    )
            return results
        except Exception:
            return []


class NewsClient:
    """Wraps CMC API for crypto news.

    Returns list of NewsItem for event context.
    Note: The standard CMC API may not have a dedicated news endpoint;
    this client uses the content/posts endpoint if available, otherwise
    returns an empty list.
    """

    def __init__(self) -> None:
        self._api_key = os.environ.get("CMC_API_KEY", "")

    @property
    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_latest_news(self, limit: int = 10) -> list[NewsItem]:
        """Fetch latest crypto news from CMC API.

        Returns an empty list if the news endpoint is not available
        or CMC_API_KEY is not set.
        """
        if not self.is_available:
            return []
        try:
            data = _api_get(
                self._api_key,
                "/v1/content/latest",
                {"limit": str(limit)},
            )
            items = []
            for article in data.get("data", []):
                items.append(
                    NewsItem(
                        title=article.get("title", ""),
                        date=article.get("created_at", ""),
                        summary=article.get("subtitle", article.get("title", "")),
                    )
                )
            return items
        except Exception:
            return []
