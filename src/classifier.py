"""Event classifier - categorizes macro events by type and assigns impact."""

from __future__ import annotations

from src.models import (
    ClassifiedEvent,
    EventCategory,
    ImpactLevel,
    MacroEvent,
)

_CLASSIFICATION_RULES: list[tuple[list[str], EventCategory, ImpactLevel]] = [
    (["fomc", "federal reserve", "fed rate", "rate decision"], EventCategory.FOMC, ImpactLevel.HIGH),
    (["cpi", "inflation", "consumer price"], EventCategory.CPI, ImpactLevel.HIGH),
    (["payroll", "employment", "jobs report", "non-farm", "nfp"], EventCategory.EMPLOYMENT, ImpactLevel.MEDIUM),
    (["etf", "halving", "etf deadline"], EventCategory.CRYPTO_SPECIFIC, ImpactLevel.HIGH),
    (["upgrade", "fork", "token burn", "token unlock", "unlock"], EventCategory.CRYPTO_SPECIFIC, ImpactLevel.MEDIUM),
]


def classify_event(event: MacroEvent) -> ClassifiedEvent:
    """Classify a macro event by category and impact using keyword matching.

    Matches against event name, raw_type, and description (case-insensitive).
    """
    searchable = f"{event.name} {event.raw_type} {event.description}".lower()

    for keywords, category, impact in _CLASSIFICATION_RULES:
        if any(kw in searchable for kw in keywords):
            return ClassifiedEvent(event=event, category=category, impact=impact)

    return ClassifiedEvent(event=event, category=EventCategory.OTHER, impact=ImpactLevel.LOW)
