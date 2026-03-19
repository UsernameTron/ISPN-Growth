"""Signal scorers for the GCS Engine. Each returns int 0-3."""

from src.signals.volume_growth import score_volume_growth
from src.signals.sla_degradation import score_sla_degradation
from src.signals.service_concentration import score_service_concentration
from src.signals.bead_exposure import score_bead_exposure
from src.signals.utilization_headroom import score_utilization_headroom
from src.signals.repeat_contacts import score_repeat_contacts
from src.signals.contract_proximity import score_contract_proximity
from src.signals.seasonal_volatility import score_seasonal_volatility

__all__ = [
    "score_volume_growth",
    "score_sla_degradation",
    "score_service_concentration",
    "score_bead_exposure",
    "score_utilization_headroom",
    "score_repeat_contacts",
    "score_contract_proximity",
    "score_seasonal_volatility",
]
