from fastapi import APIRouter, Depends, Request

from app.auth import require_api_key
from app.models import OptimizeRequest, OptimizeResponse, SustainabilityMetrics, UsageResponse
from app.services.carbon import estimate_co2_saved_g, estimate_energy_saved_kwh
from app.services.compressor import compress_prompt
from app.services.deduplicator import deduplicate_lines
from app.services.quality_guard import pick_context_safe_output
from app.services.rate_limiter import enforce_ip_rate_limit
from app.services.relevance import filter_relevant_sentences
from app.services.tokenizer import count_tokens
from app.services.usage_store import record_usage, usage_totals

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "elysium-api",
        "version": "0.1.0",
    }


@router.post("/optimize", response_model=OptimizeResponse)
def optimize(
    payload: OptimizeRequest,
    request: Request,
    _api_key: str = Depends(require_api_key),
) -> OptimizeResponse:
    enforce_ip_rate_limit(request)

    source = payload.prompt.strip()
    tokens_before = count_tokens(source)

    stage_1 = deduplicate_lines(source, payload.mode)
    stage_2 = filter_relevant_sentences(stage_1, payload.mode)
    stage_3 = compress_prompt(stage_2, payload.mode)

    candidate_order = {
        "eco": [stage_3, stage_2, stage_1, source],
        "balanced": [stage_2, stage_3, stage_1, source],
        "high_quality": [stage_1, stage_2, stage_3, source],
    }[payload.mode]

    optimized = pick_context_safe_output(
        source=source,
        candidates=candidate_order,
        mode=payload.mode,
    )

    tokens_after = count_tokens(optimized)
    reduction_pct = 0.0
    if tokens_before > 0:
        reduction_pct = ((tokens_before - tokens_after) / tokens_before) * 100
        reduction_pct = max(round(reduction_pct, 2), 0.0)

    energy_saved_kwh = round(estimate_energy_saved_kwh(tokens_before, tokens_after), 8)
    co2_saved_g = round(estimate_co2_saved_g(energy_saved_kwh), 6)

    record_usage(
        tokens_before=tokens_before,
        tokens_after=tokens_after,
        energy_saved_kwh=energy_saved_kwh,
        co2_saved_g=co2_saved_g,
    )

    return OptimizeResponse(
        optimized_prompt=optimized,
        tokens_before=tokens_before,
        tokens_after=tokens_after,
        token_reduction_pct=reduction_pct,
        sustainability=SustainabilityMetrics(
            energy_saved_kwh=energy_saved_kwh,
            co2_saved_g=co2_saved_g,
        ),
    )


@router.get("/usage", response_model=UsageResponse)
def usage(request: Request, _api_key: str = Depends(require_api_key)) -> UsageResponse:
    enforce_ip_rate_limit(request)

    saved_tokens = usage_totals.total_tokens_before - usage_totals.total_tokens_after
    return UsageResponse(
        total_requests=usage_totals.total_requests,
        total_tokens_before=usage_totals.total_tokens_before,
        total_tokens_after=usage_totals.total_tokens_after,
        total_tokens_saved=max(saved_tokens, 0),
        total_energy_saved_kwh=round(usage_totals.total_energy_saved_kwh, 8),
        total_co2_saved_g=round(usage_totals.total_co2_saved_g, 6),
    )
