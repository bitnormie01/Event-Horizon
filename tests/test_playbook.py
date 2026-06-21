"""Tests for the playbook generator."""

from src.models import (
    ClassifiedEvent,
    EventCategory,
    ImpactLevel,
    MacroEvent,
    Playbook,
    PlaybookConfig,
    ReactionProfile,
)
from src.playbook import generate_playbook


def _make_event(impact: ImpactLevel = ImpactLevel.HIGH) -> ClassifiedEvent:
    return ClassifiedEvent(
        event=MacroEvent(
            name="FOMC Rate Decision",
            date="2024-01-31T19:00:00Z",
            raw_type="federal_reserve",
            description="Fed rate decision",
        ),
        category=EventCategory.FOMC,
        impact=impact,
    )


def _make_profile(median_1h: float = 0.02) -> ReactionProfile:
    return ReactionProfile(
        event_type="FOMC",
        sample_size=10,
        median_1h=median_1h,
        median_4h=0.03,
        median_24h=0.04,
        median_7d=0.06,
        hit_rate_direction=0.7,
        conditional_profiles={},
    )


def test_playbook_generated():
    """generate_playbook returns a valid Playbook."""
    event = _make_event()
    profile = _make_profile()
    config = PlaybookConfig()
    result = generate_playbook(event, profile, config)
    assert isinstance(result, Playbook)
    assert result.event == event
    assert result.profile == profile


def test_direction_bullish_for_positive_median():
    """Direction is bullish when median_1h is positive."""
    event = _make_event()
    profile = _make_profile(median_1h=0.02)
    config = PlaybookConfig()
    result = generate_playbook(event, profile, config)
    assert result.direction == "bullish"


def test_entry_timing_reflects_impact():
    """High-impact events get 6h pre-entry, medium gets 2h."""
    profile = _make_profile()
    config = PlaybookConfig()

    high_event = _make_event(ImpactLevel.HIGH)
    result_high = generate_playbook(high_event, profile, config)
    assert "6h" in result_high.entry_timing

    med_event = _make_event(ImpactLevel.MEDIUM)
    result_med = generate_playbook(med_event, profile, config)
    assert "2h" in result_med.entry_timing


def test_stop_loss_set():
    """Stop loss is a positive float."""
    event = _make_event()
    profile = _make_profile()
    config = PlaybookConfig()
    result = generate_playbook(event, profile, config)
    assert result.stop_loss > 0
