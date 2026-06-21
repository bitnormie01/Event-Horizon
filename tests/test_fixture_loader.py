"""Tests for the fixture store loader."""

from src.fixtures.loader import FixtureStore
from src.models import MacroEvent


def test_get_events_count():
    """FixtureStore returns at least 10 events."""
    store = FixtureStore()
    events = store.get_events()
    assert len(events) >= 10
    assert all(isinstance(e, MacroEvent) for e in events)


def test_get_event_outcomes():
    """FixtureStore returns outcome labels for all events."""
    store = FixtureStore()
    outcomes = store.get_event_outcomes()
    assert len(outcomes) >= 10
    assert all(isinstance(v, str) for v in outcomes.values())


def test_get_price_around_event():
    """FixtureStore returns price data for a known event_ref."""
    store = FixtureStore()
    prices = store.get_price_around_event("fomc_2024_01")
    assert len(prices) == 7
    offsets = [p["offset_hours"] for p in prices]
    assert -24 in offsets
    assert 0 in offsets
    assert 168 in offsets
