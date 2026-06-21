"""Playbook generator - produces event-driven strategy playbooks."""

from __future__ import annotations

from src.models import (
    ClassifiedEvent,
    ImpactLevel,
    Playbook,
    PlaybookConfig,
    ReactionProfile,
)


def generate_playbook(
    event: ClassifiedEvent,
    profile: ReactionProfile,
    config: PlaybookConfig,
) -> Playbook:
    """Generate a strategy playbook from a classified event and its reaction profile.

    Determines direction (bullish/bearish/straddle) from median_1h.
    Sets pre-entry hours based on impact level.
    Computes stop_loss from median adverse move * multiplier.
    Selects best holding window (4h vs 24h vs 7d).
    """
    # Direction
    if profile.median_1h > 0.005:
        direction = "bullish"
    elif profile.median_1h < -0.005:
        direction = "bearish"
    else:
        direction = "straddle"

    # Entry timing based on impact
    if event.impact == ImpactLevel.HIGH:
        pre_entry_hours = config.pre_entry_hours_high
    else:
        pre_entry_hours = config.pre_entry_hours_medium
    entry_timing = f"{pre_entry_hours}h before event"

    # Confirmation window
    confirmation = (
        f"Price moves in expected direction within {config.confirmation_window_hours}h post-event"
    )

    # Select best holding period by absolute return
    windows = {
        "4h": abs(profile.median_4h),
        "24h": abs(profile.median_24h),
        "7d": abs(profile.median_7d),
    }
    best_window = max(windows, key=lambda k: windows[k])
    holding_period = best_window

    # Stop loss: 2x median adverse move
    if direction == "bullish":
        adverse_move = abs(min(profile.median_1h, profile.median_4h, 0.0))
    elif direction == "bearish":
        adverse_move = abs(max(profile.median_1h, profile.median_4h, 0.0))
    else:
        adverse_move = max(abs(profile.median_1h), abs(profile.median_4h))

    # Ensure minimum stop loss
    if adverse_move < 0.005:
        adverse_move = 0.005

    stop_loss = adverse_move * config.stop_loss_multiplier

    # Invalidation
    invalidation = (
        f"Price moves against position by >{stop_loss:.1%} before event, "
        f"or stop-loss hit before event fires"
    )

    return Playbook(
        event=event,
        profile=profile,
        config=config,
        direction=direction,
        entry_timing=entry_timing,
        confirmation=confirmation,
        holding_period=holding_period,
        stop_loss=stop_loss,
        invalidation=invalidation,
    )
