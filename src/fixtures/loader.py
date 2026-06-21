"""Fixture store for loading event, price, and news data from JSON files."""

from __future__ import annotations

import json
from pathlib import Path

from src.models import MacroEvent


class FixtureStore:
    """Loads and provides access to fixture data files."""

    def __init__(self, fixtures_dir: Path | None = None) -> None:
        if fixtures_dir is None:
            fixtures_dir = Path(__file__).resolve().parent.parent.parent / "fixtures"
        self._fixtures_dir = fixtures_dir
        self._events_data: list[dict] | None = None
        self._prices_data: list[dict] | None = None
        self._news_data: list[dict] | None = None

    def _load_events(self) -> list[dict]:
        if self._events_data is None:
            path = self._fixtures_dir / "events.json"
            self._events_data = json.loads(path.read_text())
        return self._events_data

    def _load_prices(self) -> list[dict]:
        if self._prices_data is None:
            path = self._fixtures_dir / "prices.json"
            self._prices_data = json.loads(path.read_text())
        return self._prices_data

    def _load_news(self) -> list[dict]:
        if self._news_data is None:
            path = self._fixtures_dir / "news.json"
            self._news_data = json.loads(path.read_text())
        return self._news_data

    def get_events(self) -> list[MacroEvent]:
        """Return all macro events from the fixture calendar."""
        raw = self._load_events()
        return [
            MacroEvent(
                name=e["name"],
                date=e["date"],
                raw_type=e["raw_type"],
                description=e["description"],
            )
            for e in raw
        ]

    def get_event_outcomes(self) -> dict[str, str]:
        """Return mapping of event_ref to outcome_label."""
        raw = self._load_events()
        return {e["event_ref"]: e["outcome_label"] for e in raw}

    def get_price_around_event(self, event_ref: str) -> list[dict]:
        """Return price points for a given event reference."""
        raw = self._load_prices()
        for entry in raw:
            if entry["event_ref"] == event_ref:
                return entry["prices"]
        return []

    def get_price_series(self) -> list[dict]:
        """Return flattened price series across all events for backtest."""
        raw = self._load_prices()
        return raw

    def get_event_refs_by_type(self, raw_type: str) -> list[str]:
        """Return event_refs for events matching a given raw_type."""
        raw = self._load_events()
        return [e["event_ref"] for e in raw if e["raw_type"] == raw_type]

    def get_event_ref_for_event(self, event: MacroEvent) -> str | None:
        """Return event_ref for a given MacroEvent by matching name and date."""
        raw = self._load_events()
        for e in raw:
            if e["name"] == event.name and e["date"] == event.date:
                return e["event_ref"]
        return None
