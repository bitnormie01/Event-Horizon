"""Tests for the data ingress clients."""

from src.data_ingress import EventClient, NewsClient, QuoteClient


def test_event_client_no_key():
    """EventClient returns empty list without CMC_API_KEY."""
    client = EventClient()
    events = client.get_upcoming_events()
    assert events == []


def test_quote_client_no_key():
    """QuoteClient returns None without CMC_API_KEY."""
    client = QuoteClient()
    quote = client.get_quote("BTC")
    assert quote is None


def test_news_client_no_key():
    """NewsClient returns empty list without CMC_API_KEY."""
    client = NewsClient()
    news = client.get_latest_news()
    assert news == []


def test_event_client_availability():
    """EventClient reports not available without API key."""
    client = EventClient()
    assert client.is_available is False


def test_quote_client_availability():
    """QuoteClient reports not available without API key."""
    client = QuoteClient()
    assert client.is_available is False


def test_news_client_availability():
    """NewsClient reports not available without API key."""
    client = NewsClient()
    assert client.is_available is False
