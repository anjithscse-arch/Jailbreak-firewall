"""Dataset record database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class DatasetRecord(Base):
    """Metadata tracking for uploaded or seeded prompt datasets."""
    __tablename__ = "dataset_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    filename = Column(String(255), nullable=False)
    row_count = Column(Integer, default=0, nullable=False)
    class_distribution = Column(Text, nullable=False)  # JSON string
    validation_status = Column(String(32), default="VALID", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
