"""Supervised ML model training script for prompt injection and jailbreak detection."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

from app.config import settings
from app.ml.preprocessing import batch_preprocess_for_ml
from app.seed.seed_dataset import save_seed_datasets

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def train_model() -> Dict[str, Any]:
    """Train the two-layer ML classifier on the prompt dataset and serialize artifacts."""
    data_dir = settings.DATA_DIR
    csv_path = data_dir / "prompts.csv"

    # Generate starter dataset if missing
    if not csv_path.exists():
        logger.info(f"Dataset not found at {csv_path}. Generating seed dataset...")
        save_seed_datasets()

    df = pd.read_csv(csv_path)
    logger.info(f"Loaded {len(df)} prompt samples from {csv_path}")

    # Clean & normalize texts
    df["processed_text"] = batch_preprocess_for_ml(df["text"].tolist())

    # Split dataset based on seeded 'split' column (train/val/test)
    train_mask = df["split"].isin(["train", "val"])
    test_mask = df["split"] == "test"

    train_texts = df.loc[train_mask, "processed_text"].tolist()
    train_labels = df.loc[train_mask, "label"].tolist()

    test_texts = df.loc[test_mask, "processed_text"].tolist()
    test_labels = df.loc[test_mask, "label"].tolist()

    logger.info(f"Training on {len(train_texts)} samples, testing on {len(test_texts)} samples")

    # Encode multiclass labels
    label_encoder = LabelEncoder()
    y_train = label_encoder.fit_transform(train_labels)
    y_test = label_encoder.transform(test_labels)

    # Hybrid Word + Character N-Gram Feature Union
    word_vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_features=12000,
        sublinear_tf=True
    )

    char_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=2,
        max_features=15000,
        sublinear_tf=True
    )

    vectorizer = FeatureUnion([
        ("word", word_vectorizer),
        ("char", char_vectorizer),
    ])

    logger.info("Fitting TF-IDF FeatureUnion (Word 1-2 & Char 3-5 n-grams)...")
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)

    # Train calibrated multiclass Logistic Regression with balanced weighting
    classifier = LogisticRegression(
        C=3.0,
        max_iter=1000,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42
    )

    logger.info("Fitting Logistic Regression classifier...")
    classifier.fit(X_train, y_train)

    # Evaluation
    y_pred = classifier.predict(X_test)
    y_prob = classifier.predict_proba(X_test)

    acc = float(accuracy_score(y_test, y_pred))
    macro_prec = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    macro_rec = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    weighted_f1 = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test, y_pred).tolist()
    labels = label_encoder.classes_.tolist()
    clf_report = classification_report(y_test, y_pred, target_names=labels, output_dict=True, zero_division=0)

    # Extract top distinctive features per class for explainability cache
    feature_names = []
    for name, trans in vectorizer.transformer_list:
        sub_features = [f"{name}:{feat}" for feat in trans.get_feature_names_out()]
        feature_names.extend(sub_features)

    feature_importance: Dict[str, list] = {}
    for idx, class_name in enumerate(labels):
        coefs = classifier.coef_[idx]
        top_indices = np.argsort(coefs)[-15:][::-1]
        feature_importance[class_name] = [
            {"feature": feature_names[i], "weight": round(float(coefs[i]), 4)}
            for i in top_indices
        ]

    # Model metadata
    version = f"tfidf-logreg-v1.{datetime.now(timezone.utc).strftime('%Y%m%d')}"
    metadata = {
        "model_name": "TFIDF-LogReg-Firewall-Classifier",
        "model_type": "tfidf-logreg",
        "version": version,
        "n_samples": len(df),
        "n_features": len(feature_names),
        "classes": labels,
        "accuracy": round(acc, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "macro_f1": round(macro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }

    # Save artifacts
    artifacts_dir = settings.ARTIFACTS_DIR
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(vectorizer, artifacts_dir / "vectorizer.joblib")
    joblib.dump(classifier, artifacts_dir / "classifier.joblib")
    joblib.dump(label_encoder, artifacts_dir / "label_encoder.joblib")

    with open(artifacts_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(artifacts_dir / "confusion_matrix.json", "w", encoding="utf-8") as f:
        json.dump({"classes": labels, "matrix": cm}, f, indent=2)

    with open(artifacts_dir / "classification_report.json", "w", encoding="utf-8") as f:
        json.dump(clf_report, f, indent=2)

    with open(artifacts_dir / "feature_importance.json", "w", encoding="utf-8") as f:
        json.dump(feature_importance, f, indent=2)

    logger.info(f"Model successfully trained and saved to {artifacts_dir}")
    logger.info(f"Accuracy: {acc:.4f} | Macro F1: {macro_f1:.4f} | Weighted F1: {weighted_f1:.4f}")

    return metadata


if __name__ == "__main__":
    train_model()
