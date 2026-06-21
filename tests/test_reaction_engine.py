"""Tests for the reaction engine."""

from src.fixtures.loader import FixtureStore
from src.models import ReactionProfile
from src.reaction_engine import compute_reaction_profile


class FakeStore(FixtureStore):
    """Fake fixture store with controlled price data for testing."""

    def __init__(self):
        super().__init__()

    def get_price_around_event(self, event_ref: str) -> list[dict]:
        if event_ref == "bullish_event_1":
            return [
                {"offset_hours": -24, "price": 100.0},
                {"offset_hours": -6, "price": 101.0},
                {"offset_hours": 0, "price": 100.0},
                {"offset_hours": 1, "price": 102.0},
                {"offset_hours": 4, "price": 103.0},
                {"offset_hours": 24, "price": 105.0},
                {"offset_hours": 168, "price": 110.0},
            ]
        if event_ref == "bullish_event_2":
            return [
                {"offset_hours": -24, "price": 200.0},
                {"offset_hours": -6, "price": 201.0},
                {"offset_hours": 0, "price": 200.0},
                {"offset_hours": 1, "price": 204.0},
                {"offset_hours": 4, "price": 206.0},
                {"offset_hours": 24, "price": 210.0},
                {"offset_hours": 168, "price": 220.0},
            ]
        return []


def test_profile_returns_result():
    """compute_reaction_profile returns a valid ReactionProfile."""
    store = FakeStore()
    profile = compute_reaction_profile(
        "test_type", store, ["bullish_event_1", "bullish_event_2"]
    )
    assert isinstance(profile, ReactionProfile)
    assert profile.event_type == "test_type"
    assert profile.sample_size == 2


def test_median_1h_positive_for_bullish_event():
    """Median 1h return is positive for bullish events."""
    store = FakeStore()
    profile = compute_reaction_profile(
        "test_type", store, ["bullish_event_1", "bullish_event_2"]
    )
    assert profile.median_1h > 0
    assert profile.median_4h > 0
    assert profile.median_24h > 0
    assert profile.median_7d > 0
    assert profile.hit_rate_direction == 1.0
