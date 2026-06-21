# Event Horizon

Event Horizon is a Track 2 strategy skill that turns macro and crypto-specific event evidence into event-driven trading playbooks. It is deterministic by default: fixture events are classified, historical price reactions are measured around each event type, playbook rules are generated, and the resulting strategies are replayed against bundled fixture prices.

The project is designed for judging without credentials or capital. It produces readable terminal output plus YAML playbooks that make each strategy card easy to inspect.

## What It Does

- Reads a fixture event calendar containing FOMC, CPI, employment, ETF, halving, network upgrade, and token unlock events.
- Classifies events into `FOMC`, `CPI`, `EMPLOYMENT`, `CRYPTO_SPECIFIC`, or `OTHER`, with `HIGH`, `MEDIUM`, or `LOW` impact.
- Computes historical reaction profiles from fixture prices at 1h, 4h, 24h, and 7d after the event.
- Generates playbooks with direction, entry timing, confirmation, holding period, stop loss, invalidation, sample size, median returns, and hit-rate context.
- Replays generated playbooks through a fixture-backed backtest and prints aggregate plus per-event-type metrics.

## Track 2 Fit

Track 2 asks for strategy skills grounded in CMC-style market intelligence. Event Horizon fits that track by converting event and market evidence into explicit, testable strategy rules rather than trade execution. The output is a playbook, not an order: it explains the setup, the evidence, the risk boundary, and the replay result.

## Evidence Inputs

- `fixtures/events.json` contains 12 dated event records with names, raw types, descriptions, outcome labels, and event refs.
- `fixtures/prices.json` contains price paths around each event at offsets such as -24h, -6h, 0h, 1h, 4h, 24h, and 168h.
- `fixtures/news.json` contains event-linked news summaries for context. The current scoring pipeline is driven by the event and price fixtures.

Fixture mode is the default and needs no network access or API key.

## Quick Start

Run these commands from this directory:

```powershell
python -m pip install -e ".[dev]"
python -m src run --mode fixture --output-dir output
python -m pytest tests -v
```

The CLI uses `python -m src`, which is Windows-safe and does not rely on shell-specific executable wrappers.

Useful options:

```powershell
python -m src run --mode fixture --min-impact high --output-dir output
python -m src run --mode fixture --min-impact medium
```

## Generated Outputs

When `--output-dir output` is provided, Event Horizon writes one YAML file per generated playbook:

- `output/playbook_1.yaml`
- `output/playbook_2.yaml`
- through `output/playbook_12.yaml` for the bundled fixture set

Each YAML playbook has three top-level sections:

- `event`: event name, date, category, and impact
- `strategy`: direction, entry timing, confirmation rule, holding period, stop loss, and invalidation
- `historical`: sample size, median reaction windows, and direction hit rate

The CLI also prints the top strategy card in Markdown-style text and a backtest summary with aggregate hit rate, average return, max drawdown, equity-curve count, and per-type breakdowns.

## CMC And Live Mode Boundary

Fixture mode is the complete judging path. Live mode is intentionally limited and read-only:

```powershell
python -m src run --mode live --output-dir output
```

If `CMC_API_KEY` is set, live mode fetches CMC quote/global-market context, including BTC quote data and global crypto metrics. The event calendar still comes from fixtures because the standard CMC API path used here does not provide a dedicated macro-events endpoint. If no key is present, the CLI falls back to fixture behavior.

Live mode does not place trades, sign transactions, use wallets, or allocate funds.

## Project Map

- `src/__main__.py` wires the command-line pipeline and output directory handling.
- `src/fixtures/loader.py` loads event, price, and news fixture data.
- `src/classifier.py` applies keyword rules for event category and impact.
- `src/reaction_engine.py` computes median post-event returns and direction hit rate.
- `src/playbook.py` turns classified events and reaction profiles into strategy playbooks.
- `src/emitter.py` renders playbooks as parseable YAML and Markdown strategy cards.
- `src/backtest.py` replays playbooks against fixture price reactions.
- `src/data_ingress.py` contains the optional read-only CMC quote, global metrics, and news clients.
- `tests/` covers the loader, classifier, reaction engine, playbook generation, emitter, CLI, data ingress, backtest, and full integration path.

## Verification

```powershell
python -m pytest tests -v
```

The integration test validates the full fixture pipeline: load fixtures, classify events, compute profiles, generate playbooks, parse emitted YAML, and run the backtest. CLI coverage runs `python -m src run --mode fixture` in a subprocess.

## Safety Constraints

- No live trading.
- No wallet execution.
- No private keys.
- No capital required.
- No order placement or brokerage integration.
- Fixture mode is offline and deterministic.
- Live mode, when configured, is read-only market-context retrieval.
