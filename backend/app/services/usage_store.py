from dataclasses import dataclass


@dataclass
class UsageTotals:
    total_requests: int = 0
    total_tokens_before: int = 0
    total_tokens_after: int = 0
    total_energy_saved_kwh: float = 0.0
    total_co2_saved_g: float = 0.0


usage_totals = UsageTotals()


def record_usage(
    tokens_before: int,
    tokens_after: int,
    energy_saved_kwh: float,
    co2_saved_g: float,
) -> None:
    usage_totals.total_requests += 1
    usage_totals.total_tokens_before += tokens_before
    usage_totals.total_tokens_after += tokens_after
    usage_totals.total_energy_saved_kwh += energy_saved_kwh
    usage_totals.total_co2_saved_g += co2_saved_g
