"""ModelMetadata database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from app.database import Base


class ModelMetadata(Base):
    """Trained classifier artifact registry and performance metrics."""
    __tablename__ = "model_metadata"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_name = Column(String(128), nullable=False)
    model_type = Column(String(64), nullable=False)  # tfidf-logreg | transformer
    version = Column(String(64), unique=True, nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    trained_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    artifact_path = Column(String(255), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
