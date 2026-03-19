"""GCS Engine configuration — signal weights, scoring thresholds, connector selection."""

from dataclasses import dataclass, field


@dataclass
class SignalWeight:
    name: str
    weight: float
    description: str


@dataclass
class GCSConfig:
    """Central configuration for the Growth Composite Score engine."""

    # Signal weights (must sum to 1.0 excluding disabled signals)
    signal_weights: list[SignalWeight] = field(default_factory=lambda: [
        SignalWeight("volume_growth", 0.25, "Monthly call volume trend (90-day)"),
        SignalWeight("sla_degradation", 0.20, "Service level agreement performance decline"),
        SignalWeight("service_concentration", 0.15, "Number of distinct services offered"),
        SignalWeight("bead_exposure", 0.15, "BEAD program funding status"),
        SignalWeight("utilization_headroom", 0.10, "Agent capacity vs current load"),
        SignalWeight("repeat_contacts", 0.10, "Percentage of repeat customer contacts"),
        SignalWeight("contract_proximity", 0.00, "Months until contract renewal (excluded without data)"),
        SignalWeight("seasonal_volatility", 0.05, "Coefficient of variation in weekly volumes"),
    ])

    # Scoring thresholds for composite score tiers
    tier_green: float = 70.0   # High growth opportunity
    tier_amber: float = 40.0   # Moderate opportunity
    # Below amber = red (low opportunity)

    # Composite score range
    score_min: float = 0.0
    score_max: float = 100.0

    # Per-signal score range
    signal_min: int = 0
    signal_max: int = 3

    @property
    def active_weights(self) -> list[SignalWeight]:
        """Returns only signals with non-zero weights."""
        return [sw for sw in self.signal_weights if sw.weight > 0]

    @property
    def total_weight(self) -> float:
        """Sum of active signal weights. Should be 1.0."""
        return sum(sw.weight for sw in self.active_weights)


# Singleton config instance
config = GCSConfig()
