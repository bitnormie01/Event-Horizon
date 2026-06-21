"""Tests for the event classifier."""

from src.classifier import classify_event
from src.models import EventCategory, ImpactLevel, MacroEvent


def test_fomc_high():
    event = MacroEvent(
        name="FOMC Rate Decision",
        date="2024-01-31T19:00:00Z",
        raw_type="federal_reserve",
        description="Federal Reserve rate decision",
    )
    result = classify_event(event)
    assert result.category == EventCategory.FOMC
    assert result.impact == ImpactLevel.HIGH


def test_cpi_high():
    event = MacroEvent(
        name="CPI Release",
        date="2024-02-13T13:30:00Z",
        raw_type="inflation",
        description="US Consumer Price Index",
    )
    result = classify_event(event)
    assert result.category == EventCategory.CPI
    assert result.impact == ImpactLevel.HIGH


def test_employment_medium():
    event = MacroEvent(
        name="Non-Farm Payrolls",
        date="2024-03-08T13:30:00Z",
        raw_type="employment",
        description="US jobs report",
    )
    result = classify_event(event)
    assert result.category == EventCategory.EMPLOYMENT
    assert result.impact == ImpactLevel.MEDIUM


def test_crypto_high():
    event = MacroEvent(
        name="Bitcoin Spot ETF Deadline",
        date="2024-01-10T16:00:00Z",
        raw_type="etf_deadline",
        description="SEC Bitcoin spot ETF approval",
    )
    result = classify_event(event)
    assert result.category == EventCategory.CRYPTO_SPECIFIC
    assert result.impact == ImpactLevel.HIGH


def test_other_low():
    event = MacroEvent(
        name="Random Conference",
        date="2024-05-01T10:00:00Z",
        raw_type="conference",
        description="Annual blockchain conference",
    )
    result = classify_event(event)
    assert result.category == EventCategory.OTHER
    assert result.impact == ImpactLevel.LOW
