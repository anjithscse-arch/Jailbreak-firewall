"""Detection rule database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from app.database import Base


class DetectionRule(Base):
    """Dynamic rule for Layer 1 deterministic firewall analysis."""
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rule_code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(64), index=True, nullable=False)
    pattern_type = Column(String(32), nullable=False)  # keyword, phrase, regex, structural, obfuscation
    pattern = Column(Text, nullable=False)
    severity = Column(String(32), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    weight = Column(Float, default=1.0, nullable=False)
    enabled = Column(Boolean, default=True, index=True, nullable=False)
    case_sensitive = Column(Boolean, default=False, nullable=False)
    created_by = Column(String(64), default="system", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
