"""Integration test - end-to-end pipeline validation."""

import yaml

from src.backtest import run_backtest
from src.classifier import classify_event
from src.emitter import render_yaml
from src.fixtures.loader import FixtureStore
from src.models import BacktestResult, PlaybookConfig
from src.playbook import generate_playbook
from src.reaction_engine import compute_reaction_profile


def test_full_pipeline():
    """End-to-end: FixtureStore -> classify -> profile -> playbook -> yaml -> backtest."""
    store = FixtureStore()

    # Get events
    events = store.get_events()
    assert len(events) >= 10

    # Classify
    classified = [classify_event(e) for e in events]
    assert len(classified) == len(events)

    # Group by raw_type for profiles
    type_groups: dict[str, list[str]] = {}
    for c in classified:
        ref = store.get_event_ref_for_event(c.event)
        if ref:
            type_groups.setdefault(c.event.raw_type, []).append(ref)

    # Generate playbooks
    config = PlaybookConfig()
    playbooks = []
    for c in classified:
        refs = type_groups.get(c.event.raw_type, [])
        if not refs:
            continue
        profile = compute_reaction_profile(c.event.raw_type, store, refs)
        if profile.sample_size == 0:
            continue
        playbook = generate_playbook(c, profile, config)
        playbooks.append(playbook)

    assert len(playbooks) > 0

    # Render YAML and verify parseable
    for pb in playbooks:
        yaml_str = render_yaml(pb)
        parsed = yaml.safe_load(yaml_str)
        assert "event" in parsed
        assert "strategy" in parsed
        assert "historical" in parsed

    # Run backtest
    result = run_backtest(playbooks, store)
    assert isinstance(result, BacktestResult)
    assert len(result.equity_curve) > 1
    assert result.aggregate_hit_rate >= 0.0
    assert result.aggregate_hit_rate <= 1.0
    assert result.aggregate_max_drawdown >= 0.0
