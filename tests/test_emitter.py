"""Tests for the strategy emitter."""

import yaml

from src.emitter import render_markdown, render_yaml
from src.models import (
    ClassifiedEvent,
    EventCategory,
    ImpactLevel,
    MacroEvent,
    Playbook,
    PlaybookConfig,
    ReactionProfile,
)


def _make_playbook() -> Playbook:
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
        median_24h=0.04,
        median_7d=0.06,
        hit_rate_direction=0.7,
        conditional_profiles={},
    )
    config = PlaybookConfig()
    return Playbook(
        event=event,
        profile=profile,
        config=config,
        direction="bullish",
        entry_timing="6h before event",
        confirmation="Price moves in expected direction within 4h post-event",
        holding_period="7d",
        stop_loss=0.01,
        invalidation="Price moves against position before event",
    )


def test_yaml_parseable():
    """render_yaml produces valid, parseable YAML."""
    playbook = _make_playbook()
    output = render_yaml(playbook)
    parsed = yaml.safe_load(output)
    assert parsed["event"]["name"] == "FOMC Rate Decision"
    assert parsed["strategy"]["direction"] == "bullish"
    assert parsed["historical"]["sample_size"] == 10


def test_markdown_has_sections():
    """render_markdown includes all required sections."""
    playbook = _make_playbook()
    output = render_markdown(playbook)
    assert "## Event" in output
    assert "## Direction" in output
    assert "## Entry" in output
    assert "## Confirmation" in output
    assert "## Holding Period" in output
    assert "## Stop Loss" in output
    assert "## Invalidation" in output
    assert "## Historical Hit Rate" in output
