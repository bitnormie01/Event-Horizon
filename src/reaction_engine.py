"""Reaction engine - computes historical reaction profiles for event types."""

from __future__ import annotations

from statistics import median

from src.fixtures.loader import FixtureStore
from src.models import ReactionProfile


def _compute_return(prices: list[dict], from_offset: int, to_offset: int) -> float | None:
    """Compute percentage return between two offset_hours in a price series."""
    from_price = None
    to_price = None
    for p in prices:
        if p["offset_hours"] == from_offset:
            from_price = p["price"]
        if p["offset_hours"] == to_offset:
            to_price = p["price"]
    if from_price is None or to_price is None or from_price == 0:
        return None
    return (to_price - from_price) / from_price


def compute_reaction_profile(
    event_type: str,
    fixture_store: FixtureStore,
    event_refs: list[str],
) -> ReactionProfile:
    """Compute the historical reaction profile for a set of events.

    For each event_ref, gets price series and computes returns at 1h, 4h, 24h, 7d
    offsets from event time (offset_hours=0). Aggregates into median values.
    Computes hit_rate_direction as fraction where 24h return direction matches 1h direction.
    """
    returns_1h: list[float] = []
    returns_4h: list[float] = []
    returns_24h: list[float] = []
    returns_7d: list[float] = []

    for ref in event_refs:
        prices = fixture_store.get_price_around_event(ref)
        if not prices:
            continue

        r1 = _compute_return(prices, 0, 1)
        r4 = _compute_return(prices, 0, 4)
        r24 = _compute_return(prices, 0, 24)
        r7d = _compute_return(prices, 0, 168)

        if r1 is not None:
            returns_1h.append(r1)
        if r4 is not None:
            returns_4h.append(r4)
        if r24 is not None:
            returns_24h.append(r24)
        if r7d is not None:
            returns_7d.append(r7d)

    sample_size = len(returns_1h)
    if sample_size == 0:
        return ReactionProfile(
            event_type=event_type,
            sample_size=0,
            median_1h=0.0,
            median_4h=0.0,
            median_24h=0.0,
            median_7d=0.0,
            hit_rate_direction=0.0,
            conditional_profiles={},
        )

    med_1h = median(returns_1h)
    med_4h = median(returns_4h) if returns_4h else 0.0
    med_24h = median(returns_24h) if returns_24h else 0.0
    med_7d = median(returns_7d) if returns_7d else 0.0

    # Hit rate: fraction where 24h return direction matches 1h direction
    hits = 0
    total = 0
    for r1, r24 in zip(returns_1h, returns_24h):
        if r1 == 0.0:
            continue
        total += 1
        if (r1 > 0 and r24 > 0) or (r1 < 0 and r24 < 0):
            hits += 1

    hit_rate = hits / total if total > 0 else 0.0

    return ReactionProfile(
        event_type=event_type,
        sample_size=sample_size,
        median_1h=med_1h,
        median_4h=med_4h,
        median_24h=med_24h,
        median_7d=med_7d,
        hit_rate_direction=hit_rate,
        conditional_profiles={},
    )
