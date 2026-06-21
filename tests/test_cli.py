"""Tests for the CLI entry point."""

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_fixture_mode():
    """CLI runs successfully in fixture mode via subprocess."""
    result = subprocess.run(
        [sys.executable, "-m", "src", "run", "--mode", "fixture"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
        timeout=30,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert "EVENT HORIZON" in result.stdout
    assert "BACKTEST RESULTS" in result.stdout
    assert "Aggregate Hit Rate" in result.stdout
