"""PromptRecord audit log model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from app.database import Base


class PromptRecord(Base):
    """Audit log record for processed prompts."""
    __tablename__ = "prompt_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(64), unique=True, index=True, nullable=False)
    conversation_id = Column(String(64), index=True, nullable=True)
    user_id = Column(String(64), index=True, nullable=True)
    original_prompt_hash = Column(String(64), index=True, nullable=False)
    redacted_prompt = Column(Text, nullable=False)
    prompt_length = Column(Integer, nullable=False)
    decision = Column(String(16), index=True, nullable=False)  # ALLOW, BLOCK, REVIEW
    attack_category = Column(String(64), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    detected_by = Column(String(32), index=True, nullable=False)  # RULE_ENGINE, ML_CLASSIFIER, BOTH, NONE
    processing_time_ms = Column(Float, nullable=False)
    llm_provider = Column(String(32), nullable=True)
    llm_model = Column(String(64), nullable=True)
    llm_called = Column(Boolean, default=False, nullable=False)
    llm_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True, nullable=False)
