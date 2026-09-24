"""Continuous Learning service implementing the adaptive feedback loop in the architecture.

Extracts newly logged attacks from the Security Database (PromptRecord),
augments the training corpus, retrains the Layer 2 ML Classifier,
and hot-reloads the active model.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import joblib
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from app.config import settings
from app.models.prompt_record import PromptRecord
from app.models.model_metadata import ModelMetadata
from app.services.ml_classifier_service import ml_classifier_service

logger = logging.getLogger(__name__)


class ContinuousLearningService:
    """Manages the retraining loop from newly logged attacks in the Security Database."""

    def retrain_from_security_database(self, db: Session) -> Dict[str, Any]:
        """Fetch captured attacks, retrain the classifier, and hot-reload."""
        # 1. Fetch captured attacks from database
        blocked_records = (
            db.query(PromptRecord)
            .filter(PromptRecord.decision == "BLOCK")
            .filter(PromptRecord.redacted_prompt.isnot(None))
            .all()
        )

        new_attack_samples = []
        for r in blocked_records:
            prompt_text = r.redacted_prompt.strip()
            if len(prompt_text) > 10:
                cat = r.attack_category or "JAILBREAK"
                if cat == "BENIGN":
                    cat = "JAILBREAK"
                new_attack_samples.append({
                    "text": prompt_text,
                    "label": cat,
                    "split": "train"
                })

        logger.info(f"Retrieved {len(new_attack_samples)} logged attack samples from Security Database.")

        # 2. Load base datasets
        data_dir = settings.DATA_DIR
        seed_csv = data_dir / "prompts.csv"
        jbt_csv = data_dir / "jailbreaktracer_benchmark.csv"

        dfs_to_combine = []
        if seed_csv.exists():
            df_s = pd.read_csv(seed_csv)[["text", "label", "split"]]
            dfs_to_combine.append(df_s)

        if jbt_csv.exists():
            df_j = pd.read_csv(jbt_csv)[["text", "label"]]
            df_j["split"] = "train"
            # 20% test split
            test_idx = df_j.sample(frac=0.2, random_state=42).index
            df_j.loc[test_idx, "split"] = "test"
            dfs_to_combine.append(df_j)

        if new_attack_samples:
            df_new = pd.DataFrame(new_attack_samples).drop_duplicates(subset=["text"])
            dfs_to_combine.append(df_new)

        if not dfs_to_combine:
            raise ValueError("No training data available for continuous learning.")

        combined_df = pd.concat(dfs_to_combine, ignore_index=True)
        combined_df["processed_text"] = combined_df["text"].astype(str).str.lower().str.strip()

        train_mask = combined_df["split"] == "train"
        test_mask = combined_df["split"] == "test"

        X_train = combined_df.loc[train_mask, "processed_text"]
        y_train = combined_df.loc[train_mask, "label"]
        X_test = combined_df.loc[test_mask, "processed_text"]
        y_test = combined_df.loc[test_mask, "label"]

        # 3. Label Encoding
        label_encoder = LabelEncoder()
        y_train_enc = label_encoder.fit_transform(y_train)
        y_test_enc = label_encoder.transform(y_test)

        # 4. Feature Extraction (Word + Character Boundary n-grams)
        union = FeatureUnion([
            ("word_ngram", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=12000, sublinear_tf=True)),
            ("char_ngram", TfidfVectorizer(ngram_range=(3, 5), analyzer="char", min_df=3, max_features=18000, sublinear_tf=True))
        ])
        X_train_vec = union.fit_transform(X_train)
        X_test_vec = union.transform(X_test)

        # 5. Classifier Training
        clf = LogisticRegression(C=2.5, max_iter=1000, class_weight="balanced", random_state=42, solver="lbfgs")
        clf.fit(X_train_vec, y_train_enc)

        # 6. Evaluation
        y_pred = clf.predict(X_test_vec)
        acc = accuracy_score(y_test_enc, y_pred)
        prec = precision_score(y_test_enc, y_pred, average="macro", zero_division=0)
        rec = recall_score(y_test_enc, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test_enc, y_pred, average="macro", zero_division=0)

        # 7. Serialize Artifacts
        artifacts_dir = settings.BASE_DIR / "app" / "ml" / "artifacts"
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        joblib.dump(clf, artifacts_dir / "classifier.joblib")
        joblib.dump(union, artifacts_dir / "vectorizer.joblib")
        joblib.dump(label_encoder, artifacts_dir / "label_encoder.joblib")

        now_iso = datetime.now(timezone.utc).isoformat()
        version_tag = f"adaptive-v{int(datetime.now().timestamp())}"

        meta = {
            "model_name": "TFIDF-LogReg-Adaptive-Firewall",
            "model_type": "tfidf-logreg-adaptive",
            "version": version_tag,
            "n_samples": len(combined_df),
            "n_features": X_train_vec.shape[1],
            "classes": list(label_encoder.classes_),
            "accuracy": round(float(acc), 4),
            "macro_precision": round(float(prec), 4),
            "macro_recall": round(float(rec), 4),
            "macro_f1": round(float(f1), 4),
            "trained_at": now_iso,
            "new_attacks_incorporated": len(new_attack_samples),
            "dataset_source": "Seed + JailbreakTracer + Security Database"
        }

        with open(artifacts_dir / "model_metadata.json", "w") as f:
            json.dump(meta, f, indent=2)

        # 8. Reload in-memory model service
        ml_classifier_service.reload()

        # 9. Record in DB
        db_record = ModelMetadata(
            model_name=meta["model_name"],
            model_type=meta["model_type"],
            version=version_tag,
            accuracy=meta["accuracy"],
            precision=meta["macro_precision"],
            recall=meta["macro_recall"],
            f1_score=meta["macro_f1"],
            artifact_path="app/ml/artifacts",
            active=True,
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        logger.info(f"Continuous learning loop completed. Updated model accuracy: {acc:.4f}, F1: {f1:.4f}")
        return meta


continuous_learning_service = ContinuousLearningService()
