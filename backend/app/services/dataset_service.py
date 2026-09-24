"""Dataset Service managing prompt dataset validation, uploads, and cataloging."""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.core.enums import AttackCategory
from app.core.exceptions import ValidationException, ResourceNotFoundException
from app.models.dataset_record import DatasetRecord


class DatasetService:
    """Validates and catalogues datasets for training and academic evaluation."""

    REQUIRED_COLUMNS = {"text", "label"}
    VALID_CATEGORIES = set(AttackCategory._value2member_map_.keys())

    def validate_csv(self, file_path: Path) -> Dict[str, Any]:
        """Validate dataset structure, schema compliance, and class balance."""
        if not file_path.exists() or not file_path.suffix.lower() == ".csv":
            raise ValidationException("File must be a valid CSV document.")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValidationException(f"Failed to parse CSV file: {str(e)}")

        missing_cols = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise ValidationException(f"Missing mandatory columns: {', '.join(missing_cols)}")

        # Check for empty rows
        if len(df) == 0:
            raise ValidationException("Dataset CSV contains zero data rows.")

        missing_texts = df["text"].isna().sum()
        missing_labels = df["label"].isna().sum()
        duplicates = df.duplicated(subset=["text"]).sum()

        invalid_labels = []
        for label in df["label"].unique():
            if str(label) not in self.VALID_CATEGORIES:
                invalid_labels.append(str(label))

        # Check prompt lengths
        max_len = df["text"].astype(str).str.len().max()
        long_prompts = (df["text"].astype(str).str.len() > 10000).sum()

        # Class distribution
        distribution = df["label"].value_counts().to_dict()

        is_valid = (
            missing_texts == 0
            and missing_labels == 0
            and len(invalid_labels) == 0
            and long_prompts == 0
        )

        return {
            "is_valid": is_valid,
            "row_count": len(df),
            "missing_values": int(missing_texts + missing_labels),
            "duplicate_prompts": int(duplicates),
            "invalid_labels": invalid_labels,
            "max_prompt_length": int(max_len),
            "excessive_length_count": int(long_prompts),
            "class_distribution": distribution,
        }

    def register_dataset(
        self,
        db: Session,
        name: str,
        filename: str,
        row_count: int,
        distribution: Dict[str, int],
        status: str = "VALID",
    ) -> DatasetRecord:
        """Create or update database tracking record for a dataset."""
        existing = db.query(DatasetRecord).filter(DatasetRecord.name == name).first()
        dist_json = json.dumps(distribution)

        if existing:
            existing.filename = filename
            existing.row_count = row_count
            existing.class_distribution = dist_json
            existing.validation_status = status
            db.commit()
            db.refresh(existing)
            return existing

        record = DatasetRecord(
            name=name,
            filename=filename,
            row_count=row_count,
            class_distribution=dist_json,
            validation_status=status,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def list_datasets(self, db: Session) -> List[DatasetRecord]:
        """List all catalogued datasets."""
        return db.query(DatasetRecord).all()

    def delete_dataset(self, db: Session, dataset_id: int) -> bool:
        """Remove a dataset entry from tracking."""
        record = db.query(DatasetRecord).filter(DatasetRecord.id == dataset_id).first()
        if not record:
            raise ResourceNotFoundException("Dataset", dataset_id)
        db.delete(record)
        db.commit()
        return True


dataset_service = DatasetService()
