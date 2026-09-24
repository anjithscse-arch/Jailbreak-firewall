"""DetectionEvent database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from app.database import Base


class DetectionEvent(Base):
    """Specific rule match or ML detection event associated with a request."""
    __tablename__ = "detection_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    request_id = Column(String(64), index=True, nullable=False)
    rule_id = Column(String(64), nullable=True)
    detection_layer = Column(String(32), nullable=False)  # RULE_ENGINE | ML_CLASSIFIER
    category = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL, INFO
    confidence = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    matched_text_hash = Column(String(64), nullable=True)
    matched_text_redacted = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
