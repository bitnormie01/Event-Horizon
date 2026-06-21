"""Tests for the backtest engine."""

from src.backtest import run_backtest
from src.fixtures.loader import FixtureStore
from src.models import (
    BacktestResult,
    ClassifiedEvent,
    EventCategory,
    ImpactLevel,
    MacroEvent,
    Playbook,
    PlaybookConfig,
    ReactionProfile,
)


class FakeStore(FixtureStore):
    """Fake store for backtest testing."""

    def __init__(self):
        super().__init__()


def _make_playbook(direction: str = "bullish", median_24h: float = 0.04) -> Playbook:
    event = ClassifiedEvent(
        event=MacroEvent(
            name="FOMC Rate Decision",
            date="2024-01-31T19:00:00Z",
            raw_type="federal_reserve",
            description="Fed rate decision",
        ),
        category=EventCategory.FOMC,
        impact=ImpactLevel.HIGH,
    )
    profile = ReactionProfile(
        event_type="FOMC",
        sample_size=10,
        median_1h=0.02,
        median_4h=0.03,
        median_24h=median_24h,
        median_7d=0.06,
        hit_rate_direction=0.7,
        conditional_profiles={},
    )
    config = PlaybookConfig()
    return Playbook(
        event=event,
        profile=profile,
        config=config,
        direction=direction,
        entry_timing="6h before event",
        confirmation="Price moves in expected direction within 4h post-event",
        holding_period="7d",
        stop_loss=0.05,
        invalidation="Price moves against position before event",
    )


def test_backtest_result():
    """run_backtest returns a valid BacktestResult."""
    store = FakeStore()
    playbooks = [_make_playbook(), _make_playbook()]
    result = run_backtest(playbooks, store)
    assert isinstance(result, BacktestResult)
    assert len(result.equity_curve) == 3  # initial + 2 trades
    assert result.aggregate_avg_return > 0


def test_aggregate_hit_rate_in_range():
    """Aggregate hit rate is between 0 and 1."""
    store = FakeStore()
    playbooks = [
        _make_playbook(direction="bullish", median_24h=0.04),
        _make_playbook(direction="bearish", median_24h=-0.02),
    ]
    result = run_backtest(playbooks, store)
    assert 0.0 <= result.aggregate_hit_rate <= 1.0
