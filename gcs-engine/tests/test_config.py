"""Tests for GCS Engine configuration."""

from src.config import GCSConfig, config


def test_default_config_weights_sum_to_one():
    """Active signal weights must sum to 1.0."""
    assert abs(config.total_weight - 1.0) < 0.001


def test_eight_signals_defined():
    """All 8 signals must be defined."""
    assert len(config.signal_weights) == 8


def test_active_weights_exclude_zero():
    """contract_proximity (weight=0) should be excluded from active weights."""
    active_names = [sw.name for sw in config.active_weights]
    assert "contract_proximity" not in active_names
    assert len(config.active_weights) == 7


def test_tier_thresholds():
    """Green > amber > 0."""
    assert config.tier_green > config.tier_amber > 0


def test_signal_range():
    """Each signal scores 0-3."""
    assert config.signal_min == 0
    assert config.signal_max == 3
