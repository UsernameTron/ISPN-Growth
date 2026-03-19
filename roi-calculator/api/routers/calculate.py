"""ROI calculation endpoints."""

from fastapi import APIRouter

from api.config import settings
from api.models.requests import ROICalculationRequest
from api.models.responses import ROICalculationResponse
from api.services.cost_model import calculate_roi

router = APIRouter(tags=["calculator"])


@router.post("/calculate", response_model=ROICalculationResponse)
async def calculate(request: ROICalculationRequest):
    """Compute full ROI comparison between in-house and ISPN outsourced support."""
    return calculate_roi(request)


@router.get("/defaults")
async def get_defaults():
    """Return smart defaults for optional fields."""
    return {
        "services_internet": True,
        "services_voice": False,
        "services_video": False,
        "services_managed_wifi": False,
        "after_hours_coverage": True,
        "turnover_rate": float(settings.INDUSTRY_TURNOVER),
    }
