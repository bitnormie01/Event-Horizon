"""Data models for Event Horizon."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class EventCategory(Enum):
    """Standardized macro event categories."""

    FOMC = "FOMC"
    CPI = "CPI"
    EMPLOYMENT = "EMPLOYMENT"
    CRYPTO_SPECIFIC = "CRYPTO_SPECIFIC"
    OTHER = "OTHER"


class ImpactLevel(Enum):
    """Expected market impact level."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass(frozen=True)
class MacroEvent:
    """A raw macro event from the calendar."""

    name: str
    date: str
    raw_type: str
    description: str


@dataclass(frozen=True)
class ClassifiedEvent:
    """An event with assigned category and impact level."""

    event: MacroEvent
    category: EventCategory
    impact: ImpactLevel


@dataclass(frozen=True)
class ReactionProfile:
    """Historical price reaction profile for an event type."""

    event_type: str
    sample_size: int
    median_1h: float
    median_4h: float
    median_24h: float
    median_7d: float
    hit_rate_direction: float
    conditional_profiles: dict[str, dict[str, float]] = field(default_factory=dict)


@dataclass(frozen=True)
class PlaybookConfig:
    """Configuration parameters for playbook generation."""

    pre_entry_hours_high: int = 6
    pre_entry_hours_medium: int = 2
    confirmation_window_hours: int = 4
    stop_loss_multiplier: float = 2.0
    max_drawdown_stop: float = 0.10


@dataclass(frozen=True)
class Playbook:
    """A generated event-driven strategy playbook."""

    event: ClassifiedEvent
    profile: ReactionProfile
    config: PlaybookConfig
    direction: str
    entry_timing: str
    confirmation: str
    holding_period: str
    stop_loss: float
    invalidation: str


@dataclass(frozen=True)
class BacktestResult:
    """Results from backtesting playbooks against historical data."""

    per_type_results: dict[str, dict[str, float]]
    aggregate_hit_rate: float
    aggregate_avg_return: float
    aggregate_max_drawdown: float
    equity_curve: list[float] = field(default_factory=list)
