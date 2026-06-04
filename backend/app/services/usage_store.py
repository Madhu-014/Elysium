from dataclasses import dataclass
from sqlalchemy import func
from app.db import SessionLocal
from app.db_models import UsageRecord

@dataclass
class UsageTotals:
    total_requests: int = 0
    total_tokens_before: int = 0
    total_tokens_after: int = 0
    total_energy_saved_kwh: float = 0.0
    total_co2_saved_g: float = 0.0

def get_usage_totals() -> UsageTotals:
    with SessionLocal() as db:
        result = db.query(
            func.count(UsageRecord.id),
            func.sum(UsageRecord.tokens_before),
            func.sum(UsageRecord.tokens_after),
            func.sum(UsageRecord.energy_saved_kwh),
            func.sum(UsageRecord.co2_saved_g)
        ).first()

        if not result or result[0] == 0:
            return UsageTotals()

        return UsageTotals(
            total_requests=result[0] or 0,
            total_tokens_before=result[1] or 0,
            total_tokens_after=result[2] or 0,
            total_energy_saved_kwh=result[3] or 0.0,
            total_co2_saved_g=result[4] or 0.0,
        )

def record_usage(
    tokens_before: int,
    tokens_after: int,
    energy_saved_kwh: float,
    co2_saved_g: float,
) -> None:
    with SessionLocal() as db:
        record = UsageRecord(
            tokens_before=tokens_before,
            tokens_after=tokens_after,
            energy_saved_kwh=energy_saved_kwh,
            co2_saved_g=co2_saved_g
        )
        db.add(record)
        db.commit()
