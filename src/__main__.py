"""CLI entry point for Event Horizon."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.backtest import run_backtest
from src.classifier import classify_event
from src.emitter import render_markdown, render_yaml
from src.fixtures.loader import FixtureStore
from src.models import ImpactLevel, PlaybookConfig
from src.playbook import generate_playbook
from src.reaction_engine import compute_reaction_profile


def _impact_threshold(value: str) -> ImpactLevel:
    mapping = {"high": ImpactLevel.HIGH, "medium": ImpactLevel.MEDIUM, "low": ImpactLevel.LOW}
    if value.lower() not in mapping:
        raise argparse.ArgumentTypeError(f"Invalid impact level: {value}")
    return mapping[value.lower()]


def _impact_meets_threshold(impact: ImpactLevel, threshold: ImpactLevel) -> bool:
    order = {ImpactLevel.HIGH: 3, ImpactLevel.MEDIUM: 2, ImpactLevel.LOW: 1}
    return order[impact] >= order[threshold]


def run(args: argparse.Namespace) -> None:
    """Execute the full Event Horizon pipeline."""
    # Load data
    store = FixtureStore()

    print(f"\n{'='*60}")
    print("EVENT HORIZON - Macro Event Strategy Generator")
    print(f"{'='*60}")

    if args.mode == "live":
        from src.data_ingress import EventClient, QuoteClient

        event_client = EventClient()
        quote_client = QuoteClient()
        if quote_client.is_available:
            print("\n  [LIVE] CMC API key detected. Fetching live market data...")
            btc_quote = quote_client.get_quote("BTC")
            if btc_quote:
                print(f"  [LIVE] BTC Price: ${btc_quote.price_usd:,.2f}")
                print(f"  [LIVE] 24h Change: {btc_quote.percent_change_24h:+.2f}%")
                print(f"  [LIVE] Volume 24h: ${btc_quote.volume_24h:,.0f}")
                print(f"  [LIVE] Market Cap: ${btc_quote.market_cap:,.0f}")
            global_metrics = event_client.get_global_metrics()
            if global_metrics:
                quote = global_metrics.get("quote", {}).get("USD", {})
                print(f"  [LIVE] Total Crypto Market Cap: ${quote.get('total_market_cap', 0):,.0f}")
                print(f"  [LIVE] BTC Dominance: {global_metrics.get('btc_dominance', 0):.1f}%")
            print("  [LIVE] Using fixture events + live market context")
        else:
            print("\n  CMC_API_KEY not set. Using fixture mode.")

    # Get events
    events = store.get_events()
    print(f"\nLoaded {len(events)} macro events")
    print(f"\n{'-'*60}")
    print("UPCOMING EVENT CALENDAR")
    print(f"{'-'*60}")
    for e in events:
        print(f"  {e.date[:10]}  {e.name}")

    # Classify events
    classified = [classify_event(e) for e in events]

    # Filter by impact threshold
    threshold = args.min_impact
    filtered = [c for c in classified if _impact_meets_threshold(c.impact, threshold)]
    print(f"\n{len(filtered)} events meet minimum impact threshold ({threshold.value})")

    # Group by raw_type for reaction profiles
    type_groups: dict[str, list[str]] = {}
    for c in filtered:
        raw_type = c.event.raw_type
        ref = store.get_event_ref_for_event(c.event)
        if ref:
            type_groups.setdefault(raw_type, []).append(ref)

    # Compute reaction profiles and generate playbooks
    config = PlaybookConfig()
    playbooks = []

    for c in filtered:
        raw_type = c.event.raw_type
        refs = type_groups.get(raw_type, [])
        if not refs:
            continue
        profile = compute_reaction_profile(raw_type, store, refs)
        if profile.sample_size == 0:
            continue
        playbook = generate_playbook(c, profile, config)
        playbooks.append(playbook)

    print(f"\nGenerated {len(playbooks)} strategy playbooks")

    # Display top playbook
    if playbooks:
        top = playbooks[0]
        print(f"\n{'-'*60}")
        print("TOP STRATEGY CARD")
        print(f"{'-'*60}")
        print(render_markdown(top))

        # Output YAML
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            for i, pb in enumerate(playbooks):
                yaml_path = output_dir / f"playbook_{i+1}.yaml"
                yaml_path.write_text(render_yaml(pb))
            print(f"  Playbooks written to {output_dir}/")

    # Run backtest
    result = run_backtest(playbooks, store)
    print(f"\n{'-'*60}")
    print("BACKTEST RESULTS")
    print(f"{'-'*60}")
    print(f"  Aggregate Hit Rate:   {result.aggregate_hit_rate:.0%}")
    print(f"  Aggregate Avg Return: {result.aggregate_avg_return:+.2%}")
    print(f"  Max Drawdown:         {result.aggregate_max_drawdown:.2%}")
    print(f"  Equity Curve Points:  {len(result.equity_curve)}")

    if result.per_type_results:
        print(f"\n  Per-Type Breakdown:")
        for etype, metrics in result.per_type_results.items():
            print(f"    {etype}: hit_rate={metrics.get('hit_rate', 0):.0%}, avg_return={metrics.get('avg_return', 0):+.2%}")

    print(f"\n{'='*60}")
    print("Event Horizon analysis complete.")
    print(f"{'='*60}\n")


def main() -> None:
    """CLI argument parser and dispatcher."""
    parser = argparse.ArgumentParser(
        prog="event_horizon",
        description="Event Horizon - CMC macro event-driven strategy generator",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run the full pipeline")
    run_parser.add_argument(
        "--mode",
        choices=["fixture", "live"],
        default="fixture",
        help="Data source mode (default: fixture)",
    )
    run_parser.add_argument(
        "--min-impact",
        type=_impact_threshold,
        default=ImpactLevel.MEDIUM,
        help="Minimum event impact to include (default: medium)",
    )
    run_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to write playbook YAML files",
    )

    args = parser.parse_args()
    if args.command == "run":
        run(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
