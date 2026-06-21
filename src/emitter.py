"""Strategy emitter - renders playbooks as YAML and Markdown."""

from __future__ import annotations

import yaml

from src.models import Playbook


def render_yaml(playbook: Playbook) -> str:
    """Serialize a playbook to YAML format."""
    data = {
        "event": {
            "name": playbook.event.event.name,
            "date": playbook.event.event.date,
            "category": playbook.event.category.value,
            "impact": playbook.event.impact.value,
        },
        "strategy": {
            "direction": playbook.direction,
            "entry_timing": playbook.entry_timing,
            "confirmation": playbook.confirmation,
            "holding_period": playbook.holding_period,
            "stop_loss": round(playbook.stop_loss, 4),
            "invalidation": playbook.invalidation,
        },
        "historical": {
            "sample_size": playbook.profile.sample_size,
            "median_1h": round(playbook.profile.median_1h, 4),
            "median_4h": round(playbook.profile.median_4h, 4),
            "median_24h": round(playbook.profile.median_24h, 4),
            "median_7d": round(playbook.profile.median_7d, 4),
            "hit_rate_direction": round(playbook.profile.hit_rate_direction, 4),
        },
    }
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def render_markdown(playbook: Playbook) -> str:
    """Render a playbook as a Markdown strategy card."""
    lines = [
        f"# Strategy Card: {playbook.event.event.name}",
        "",
        "## Event",
        f"- **Name:** {playbook.event.event.name}",
        f"- **Date:** {playbook.event.event.date}",
        f"- **Category:** {playbook.event.category.value}",
        f"- **Impact:** {playbook.event.impact.value}",
        "",
        "## Direction",
        f"- **Signal:** {playbook.direction}",
        "",
        "## Entry",
        f"- **Timing:** {playbook.entry_timing}",
        "",
        "## Confirmation",
        f"- {playbook.confirmation}",
        "",
        "## Holding Period",
        f"- **Window:** {playbook.holding_period}",
        "",
        "## Stop Loss",
        f"- **Level:** {playbook.stop_loss:.2%}",
        "",
        "## Invalidation",
        f"- {playbook.invalidation}",
        "",
        "## Historical Hit Rate",
        f"- **Sample Size:** {playbook.profile.sample_size}",
        f"- **Hit Rate:** {playbook.profile.hit_rate_direction:.0%}",
        f"- **Median 1h:** {playbook.profile.median_1h:+.2%}",
        f"- **Median 24h:** {playbook.profile.median_24h:+.2%}",
        "",
    ]
    return "\n".join(lines)
