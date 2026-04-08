from app.config import settings


def estimate_energy_saved_kwh(tokens_before: int, tokens_after: int) -> float:
    saved_tokens = max(tokens_before - tokens_after, 0)
    return (saved_tokens / 1000.0) * settings.kwh_per_1k_tokens


def estimate_co2_saved_g(energy_saved_kwh: float) -> float:
    return energy_saved_kwh * settings.grid_co2_g_per_kwh
