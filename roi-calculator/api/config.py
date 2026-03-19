"""ISPN ROI Calculator configuration."""

from decimal import Decimal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SKILL_NAME: str = "roi-calculator"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"

    # ISPN Financial Constants
    BLENDED_RATE: Decimal = Decimal("21.00")
    MULTIPLIER: Decimal = Decimal("1.35")
    UTILIZATION_TARGET: Decimal = Decimal("0.60")
    INDUSTRY_TURNOVER: Decimal = Decimal("0.35")
    TRAINING_RAMP_WEEKS: int = 6
    AFTER_HOURS_PREMIUM: Decimal = Decimal("1.50")
    MANAGEMENT_OVERHEAD: Decimal = Decimal("0.15")
    QA_MONITORING_OVERHEAD: Decimal = Decimal("0.08")

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
