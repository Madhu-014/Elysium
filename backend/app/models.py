from typing import Literal

from pydantic import BaseModel, Field


Mode = Literal["eco-max", "optimal", "precision"]


class OptimizeRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=60000)
    mode: Mode = "optimal"
    max_output_tokens: int | None = Field(default=None, ge=1, le=32000)


class SustainabilityMetrics(BaseModel):
    energy_saved_kwh: float
    co2_saved_g: float


class OptimizeResponse(BaseModel):
    optimized_prompt: str
    tokens_before: int
    tokens_after: int
    token_reduction_pct: float
    sustainability: SustainabilityMetrics


class UsageResponse(BaseModel):
    total_requests: int
    total_tokens_before: int
    total_tokens_after: int
    total_tokens_saved: int
    total_energy_saved_kwh: float
    total_co2_saved_g: float
