"""Comparative evaluation pipeline comparing Rule Engine, ML Classifier, and Combined Two-Layer Firewall."""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from app.config import settings
from app.core.enums import AttackCategory, FirewallDecision
from app.services.preprocessing_service import preprocessing_service
from app.services.rule_engine_service import rule_engine_service
from app.services.ml_classifier_service import ml_classifier_service

logger = logging.getLogger(__name__)


def evaluate_pipeline(test_csv_path: Path = None) -> Dict[str, Any]:
    """Run empirical benchmark across Rule-Only, ML-Only, and Combined Two-Layer Firewall."""
    if test_csv_path is None:
        test_csv_path = settings.DATA_DIR / "evaluation_prompts.csv"
        if not test_csv_path.exists():
            test_csv_path = settings.DATA_DIR / "prompts.csv"

    df = pd.read_csv(test_csv_path)
    logger.info(f"Evaluating firewall on {len(df)} samples from {test_csv_path}")

    # Ground truth: 1 for attack, 0 for benign
    y_true_binary = (df["label"] != AttackCategory.BENIGN.value).astype(int).tolist()
    y_true_category = df["label"].tolist()

    rule_preds = []
    rule_latencies = []

    ml_preds = []
    ml_latencies = []

    combined_preds = []
    combined_latencies = []

    for _, row in df.iterrows():
        raw_text = str(row["text"])

        # 1. Preprocessing
        t0 = time.perf_counter()
        prep = preprocessing_service.preprocess(raw_text)

        # 2. Rule Engine Only
        t_rule_0 = time.perf_counter()
        rule_res = rule_engine_service.detect(
            original_text=raw_text,
            normalized_text=prep["normalized_text"],
            metadata=prep
        )
        t_rule_ms = (time.perf_counter() - t_rule_0) * 1000.0
        rule_latencies.append(t_rule_ms)
        rule_is_attack = 1 if rule_res["is_blocking"] or rule_res["max_score"] >= 0.70 else 0
        rule_preds.append(rule_is_attack)

        # 3. ML Classifier Only
        t_ml_0 = time.perf_counter()
        ml_res = ml_classifier_service.predict(prep["normalized_text"])
        t_ml_ms = (time.perf_counter() - t_ml_0) * 1000.0
        ml_latencies.append(t_ml_ms)
        ml_is_attack = 1 if ml_res["label"] != AttackCategory.BENIGN.value and ml_res["confidence"] >= 0.60 else 0
        ml_preds.append(ml_is_attack)

        # 4. Combined Two-Layer Decision
        t_comb_ms = (time.perf_counter() - t0) * 1000.0
        combined_latencies.append(t_comb_ms)

        # Aggregation formula
        rule_score = rule_res["max_score"]
        ml_score = ml_res["confidence"] if ml_res["label"] != AttackCategory.BENIGN.value else (1.0 - ml_res["confidence"])
        bonus = 0.05 if (rule_res["top_category"] == ml_res["label"] and rule_res["top_category"] != AttackCategory.BENIGN.value) else 0.0
        obf_bonus = 0.05 if len(prep.get("obfuscation_indicators", [])) > 0 else 0.0

        risk_score = min(1.0, max(rule_score, ml_score) + bonus + obf_bonus)
        comb_is_attack = 1 if (rule_res["is_blocking"] or risk_score >= 0.70) else 0
        combined_preds.append(comb_is_attack)

    def compute_layer_metrics(y_true, y_pred, latencies) -> Dict[str, Any]:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        acc = float(accuracy_score(y_true, y_pred))
        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        return {
            "total_evaluated": len(y_true),
            "true_positives": int(tp),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "false_positive_rate": round(fpr, 4),
            "false_negative_rate": round(fnr, 4),
            "avg_latency_ms": round(float(np.mean(latencies)), 2),
            "p95_latency_ms": round(float(np.percentile(latencies, 95)), 2),
        }

    rule_metrics = compute_layer_metrics(y_true_binary, rule_preds, rule_latencies)
    ml_metrics = compute_layer_metrics(y_true_binary, ml_preds, ml_latencies)
    combined_metrics = compute_layer_metrics(y_true_binary, combined_preds, combined_latencies)

    # Confusion matrix breakdown
    cm_data = {
        "labels": ["BENIGN", "ATTACK"],
        "rule_only": confusion_matrix(y_true_binary, rule_preds, labels=[0, 1]).tolist(),
        "ml_only": confusion_matrix(y_true_binary, ml_preds, labels=[0, 1]).tolist(),
        "combined": confusion_matrix(y_true_binary, combined_preds, labels=[0, 1]).tolist(),
    }

    report = {
        "dataset_samples": len(df),
        "rule_only": rule_metrics,
        "ml_only": ml_metrics,
        "combined": combined_metrics,
        "confusion_matrix": cm_data,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }

    reports_dir = settings.REPORTS_DIR
    reports_dir.mkdir(parents=True, exist_ok=True)

    with open(reports_dir / "evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Evaluation report written to {reports_dir / 'evaluation_report.json'}")
    return report


if __name__ == "__main__":
    evaluate_pipeline()
