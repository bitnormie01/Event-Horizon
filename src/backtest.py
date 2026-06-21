"""Backtest engine - replays playbooks against historical fixture data."""

from __future__ import annotations

from src.fixtures.loader import FixtureStore
from src.models import BacktestResult, Playbook


def run_backtest(
    playbooks: list[Playbook],
    fixture_store: FixtureStore,
) -> BacktestResult:
    """Replay playbooks against historical events and compute aggregate metrics.

    For each playbook, applies the median_24h return for the event type to simulate
    trades. Tracks equity curve, computes per-type results, aggregate hit rate,
    avg return, and max drawdown.
    """
    per_type_results: dict[str, dict[str, float]] = {}
    all_returns: list[float] = []
    all_hits: list[bool] = []
    equity = 1.0
    equity_curve: list[float] = [equity]

    for playbook in playbooks:
        event_type = playbook.profile.event_type
        direction = playbook.direction

        # Get the median 24h return for this event type
        trade_return = playbook.profile.median_24h

        # For bearish direction, we profit from negative moves
        if direction == "bearish":
            trade_return = -trade_return
        elif direction == "straddle":
            trade_return = abs(trade_return)

        # Apply stop loss
        if trade_return < -playbook.stop_loss:
            trade_return = -playbook.stop_loss

        # Track results
        all_returns.append(trade_return)
        all_hits.append(trade_return > 0)

        # Update equity
        equity *= (1 + trade_return)
        equity_curve.append(equity)

        # Accumulate per-type results
        if event_type not in per_type_results:
            per_type_results[event_type] = {
                "count": 0,
                "total_return": 0.0,
                "hits": 0,
            }
        per_type_results[event_type]["count"] += 1
        per_type_results[event_type]["total_return"] += trade_return
        if trade_return > 0:
            per_type_results[event_type]["hits"] += 1

    # Compute aggregate metrics
    aggregate_hit_rate = sum(all_hits) / len(all_hits) if all_hits else 0.0
    aggregate_avg_return = sum(all_returns) / len(all_returns) if all_returns else 0.0

    # Compute max drawdown from equity curve
    peak = equity_curve[0]
    max_drawdown = 0.0
    for val in equity_curve:
        if val > peak:
            peak = val
        drawdown = (peak - val) / peak if peak > 0 else 0.0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    # Finalize per-type results
    for event_type in per_type_results:
        count = per_type_results[event_type]["count"]
        per_type_results[event_type]["avg_return"] = (
            per_type_results[event_type]["total_return"] / count if count > 0 else 0.0
        )
        per_type_results[event_type]["hit_rate"] = (
            per_type_results[event_type]["hits"] / count if count > 0 else 0.0
        )

    return BacktestResult(
        per_type_results=per_type_results,
        aggregate_hit_rate=aggregate_hit_rate,
        aggregate_avg_return=aggregate_avg_return,
        aggregate_max_drawdown=max_drawdown,
        equity_curve=equity_curve,
    )
