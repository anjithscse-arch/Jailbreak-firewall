"""Complete database initialization, admin seeding, and model readiness script."""

import json
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.database import init_db, SessionLocal
from app.models.user import User
from app.models.dataset_record import DatasetRecord
from app.models.model_metadata import ModelMetadata
from app.core.security import hash_password
from app.seed.seed_rules import seed_rules
from app.seed.seed_dataset import save_seed_datasets
from app.ml.train import train_model
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def seed_admin(db: Session):
    """Ensure default administrator account exists."""
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        hashed = hash_password("admin123")
        admin = User(
            username="admin",
            password_hash=hashed,
            role="admin",
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
        db.add(admin)
        db.commit()
        logger.info("Created default administrator account ('admin' / 'admin123').")
    else:
        logger.info("Administrator account already present.")


def seed_datasets_record(db: Session):
    """Ensure starter prompt dataset is registered."""
    dataset_rec = db.query(DatasetRecord).filter(DatasetRecord.name == "starter_dataset").first()
    if not dataset_rec:
        paths = save_seed_datasets()
        rec = DatasetRecord(
            name="starter_dataset",
            filename="prompts.csv",
            row_count=650,
            class_distribution=json.dumps({"ATTACK": 550, "BENIGN": 100}),
            validation_status="VALID",
            created_at=datetime.now(timezone.utc),
        )
        db.add(rec)
        db.commit()
        logger.info("Registered starter dataset catalog record.")


def seed_model_metadata(db: Session):
    """Ensure active ML model record exists in DB."""
    active_meta = db.query(ModelMetadata).filter(ModelMetadata.active == True).first()
    artifacts_dir = settings.ARTIFACTS_DIR
    meta_json = artifacts_dir / "model_metadata.json"

    if not meta_json.exists():
        logger.info("Training initial ML model artifact...")
        metadata = train_model()
    else:
        with open(meta_json, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    if not active_meta:
        record = ModelMetadata(
            model_name=metadata.get("model_name", "TFIDF-LogReg-Firewall-Classifier"),
            model_type=metadata.get("model_type", "tfidf-logreg"),
            version=metadata.get("version", "v1"),
            accuracy=metadata.get("accuracy"),
            precision=metadata.get("macro_precision"),
            recall=metadata.get("macro_recall"),
            f1_score=metadata.get("macro_f1"),
            artifact_path=str(artifacts_dir),
            active=True,
            trained_at=datetime.now(timezone.utc),
        )
        db.add(record)
        db.commit()
        logger.info("Registered model metadata in database.")


def seed_all():
    """Execute complete end-to-end database initialization."""
    init_db()
    db: Session = SessionLocal()
    try:
        seed_admin(db)
        seed_rules(db)
        seed_datasets_record(db)
        seed_model_metadata(db)
        logger.info("Seed sequence completed successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
