"""Processor and database seeder for the JailbreakTracer research paper dataset.

Paper: 'JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation'
Authors: Md. Faiyaz Abdullah Sayeedi, Maaz Bin Hossain, Md. Kamrul Hassan, et al.
Venue: IEEE Access, 2025.
DOI: 10.1109/ACCESS.2025.3579996
Repository: https://github.com/faiyazabdullah/JailbreakTracer
"""

import logging
from pathlib import Path
import pandas as pd
from sqlalchemy.orm import Session

from app.database import SessionLocal, init_db
from app.models.dataset_record import DatasetRecord
from app.services.dataset_service import dataset_service

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
JBT_DIR = DATA_DIR / "jailbreaktracer"


def prepare_benchmark_dataset():
    """Extract and compile a balanced, representative benchmark dataset from the paper."""
    jb_path = JBT_DIR / "jailbreak_prompts_2023_05_07.csv"
    reg_path = JBT_DIR / "regular_prompts_2023_05_07.csv"

    if not jb_path.exists() or not reg_path.exists():
        logger.error("JailbreakTracer source files not found in %s", JBT_DIR)
        return None

    # Load jailbreak prompts
    df_jb = pd.read_csv(jb_path)
    df_jb_clean = pd.DataFrame({
        "text": df_jb["prompt"].astype(str).str.strip(),
        "prompt": df_jb["prompt"].astype(str).str.strip(),
        "label": "JAILBREAK",
        "source": "JailbreakTracer-IEEEAccess-InTheWild"
    })
    # Filter out empty, extremely short, or excessive (>8000 chars) rows
    df_jb_clean = df_jb_clean[df_jb_clean["text"].str.len().between(10, 8000)].drop_duplicates(subset=["text"])

    # Load benign prompts
    df_reg = pd.read_csv(reg_path)
    df_reg_clean = pd.DataFrame({
        "text": df_reg["prompt"].astype(str).str.strip(),
        "prompt": df_reg["prompt"].astype(str).str.strip(),
        "label": "BENIGN",
        "source": "JailbreakTracer-IEEEAccess-Regular"
    })
    df_reg_clean = df_reg_clean[df_reg_clean["text"].str.len().between(10, 8000)].drop_duplicates(subset=["text"])

    # Sample a balanced 1,000-prompt benchmark dataset (500 jailbreaks + 500 benign)
    n_samples_each = min(500, len(df_jb_clean), len(df_reg_clean))
    df_jb_sample = df_jb_clean.sample(n=n_samples_each, random_state=42)
    df_reg_sample = df_reg_clean.sample(n=n_samples_each, random_state=42)

    combined_df = pd.concat([df_jb_sample, df_reg_sample], ignore_index=True)
    combined_df = combined_df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    output_csv = DATA_DIR / "jailbreaktracer_benchmark.csv"
    combined_df.to_csv(output_csv, index=False)
    logger.info("Saved compiled JailbreakTracer benchmark dataset to %s (%d rows)", output_csv, len(combined_df))

    return output_csv


def register_jailbreaktracer_dataset(db: Session, csv_path: Path):
    """Register the JailbreakTracer dataset in the firewall's SQLite catalog."""
    val_report = dataset_service.validate_csv(csv_path)
    status_str = "VALID" if val_report["is_valid"] else "INVALID"

    import json
    existing = db.query(DatasetRecord).filter(DatasetRecord.name == "JailbreakTracer-IEEE-Access-Corpus").first()
    if existing:
        existing.row_count = val_report["row_count"]
        existing.class_distribution = json.dumps(val_report["class_distribution"])
        existing.validation_status = status_str
        db.commit()
        logger.info("Updated existing DatasetRecord for JailbreakTracer.")
        return existing

    record = dataset_service.register_dataset(
        db=db,
        name="JailbreakTracer-IEEE-Access-Corpus",
        filename=csv_path.name,
        row_count=val_report["row_count"],
        distribution=val_report["class_distribution"],
        status=status_str,
    )
    logger.info("Registered new DatasetRecord ID=%d for JailbreakTracer.", record.id)
    return record


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.info("Processing JailbreakTracer dataset...")
    csv_path = prepare_benchmark_dataset()
    if csv_path:
        db = SessionLocal()
        try:
            register_jailbreaktracer_dataset(db, csv_path)
            print("Successfully processed and registered JailbreakTracer dataset!")
        finally:
            db.close()


if __name__ == "__main__":
    main()
