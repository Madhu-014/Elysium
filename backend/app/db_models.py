from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, LargeBinary
from app.db import Base

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    tokens_before = Column(Integer, default=0)
    tokens_after = Column(Integer, default=0)
    energy_saved_kwh = Column(Float, default=0.0)
    co2_saved_g = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PromptCache(Base):
    __tablename__ = "prompt_cache"

    id = Column(Integer, primary_key=True, index=True)
    prompt_hash = Column(String, unique=True, index=True)
    mode = Column(String, index=True)
    optimized_prompt = Column(String)
    embedding_blob = Column(LargeBinary, nullable=True)
    tokens_before = Column(Integer, default=0)
    tokens_after = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
