"""Metrics Service calculating live telemetry, category distribution, and evaluation benchmarks."""

import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.models.prompt_record import PromptRecord
from app.models.model_metadata import ModelMetadata
from app.ml.evaluate import evaluate_pipeline


class MetricsService:
    """Aggregates security metrics and telemetry for administrative reporting."""

    def get_summary(self, db: Session) -> Dict[str, Any]:
        """Compile executive firewall summary metrics."""
        total = db.query(func.count(PromptRecord.id)).scalar() or 0
        allowed = db.query(func.count(PromptRecord.id)).filter(PromptRecord.decision == "ALLOW").scalar() or 0
        blocked = db.query(func.count(PromptRecord.id)).filter(PromptRecord.decision == "BLOCK").scalar() or 0
        review = db.query(func.count(PromptRecord.id)).filter(PromptRecord.decision == "REVIEW").scalar() or 0
        avg_lat = db.query(func.avg(PromptRecord.processing_time_ms)).scalar() or 0.0

        rule_detected = (
            db.query(func.count(PromptRecord.id))
            .filter(PromptRecord.detected_by.in_(["RULE_ENGINE", "BOTH"]))
            .scalar()
            or 0
        )
        ml_detected = (
            db.query(func.count(PromptRecord.id))
            .filter(PromptRecord.detected_by.in_(["ML_CLASSIFIER", "BOTH"]))
            .scalar()
            or 0
        )

        attack_rate = round((blocked / total) * 100, 2) if total > 0 else 0.0
        rule_rate = round((rule_detected / total) * 100, 2) if total > 0 else 0.0
        ml_rate = round((ml_detected / total) * 100, 2) if total > 0 else 0.0

        # Read latest ML evaluation metrics from metadata or report
        meta = (
            db.query(ModelMetadata)
            .filter(ModelMetadata.active == True)
            .order_by(ModelMetadata.id.desc())
            .first()
        )

        acc = meta.accuracy if meta else None
        prec = meta.precision if meta else None
        rec = meta.recall if meta else None
        f1 = meta.f1_score if meta else None
        fpr = None
        fnr = None

        # Check for cached evaluation report
        eval_report_file = settings.REPORTS_DIR / "evaluation_report.json"
        if eval_report_file.exists():
            try:
                with open(eval_report_file, "r", encoding="utf-8") as f:
                    eval_data = json.load(f)
                    comb = eval_data.get("combined", {})
                    if not acc:
                        acc = comb.get("accuracy")
                    if not prec:
                        prec = comb.get("precision")
                    if not rec:
                        rec = comb.get("recall")
                    if not f1:
                        f1 = comb.get("f1")
                    fpr = comb.get("false_positive_rate")
                    fnr = comb.get("false_negative_rate")
            except Exception:
                pass

        return {
            "total_requests": total,
            "allowed_requests": allowed,
            "blocked_requests": blocked,
            "review_requests": review,
            "attack_rate": attack_rate,
            "average_latency_ms": round(float(avg_lat), 2),
            "rule_detection_rate": rule_rate,
            "ml_detection_rate": ml_rate,
            "false_positive_rate": fpr,
            "false_negative_rate": fnr,
            "model_accuracy": acc,
            "model_precision": prec,
            "model_recall": rec,
            "model_f1": f1,
        }

    def get_timeline(self, db: Session, hours: int = 24) -> List[Dict[str, Any]]:
        """Generate time-series request buckets."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(hours=hours)

        records = (
            db.query(PromptRecord)
            .filter(PromptRecord.created_at >= start_time)
            .order_by(PromptRecord.created_at.asc())
            .all()
        )

        # Bucket by hour
        buckets: Dict[str, Dict[str, Any]] = {}
        for i in range(hours):
            bucket_dt = start_time + timedelta(hours=i)
            key = bucket_dt.strftime("%H:00")
            buckets[key] = {
                "timestamp": key,
                "total": 0,
                "allowed": 0,
                "blocked": 0,
                "review": 0,
                "latencies": [],
            }

        for r in records:
            key = r.created_at.strftime("%H:00")
            if key in buckets:
                buckets[key]["total"] += 1
                if r.decision == "ALLOW":
                    buckets[key]["allowed"] += 1
                elif r.decision == "BLOCK":
                    buckets[key]["blocked"] += 1
                else:
                    buckets[key]["review"] += 1
                buckets[key]["latencies"].append(r.processing_time_ms)

        timeline = []
        for key, data in buckets.items():
            lats = data.pop("latencies")
            data["avg_latency_ms"] = round(float(sum(lats) / len(lats)), 2) if lats else 0.0
            timeline.append(data)

        return timeline

    def get_categories(self, db: Session) -> List[Dict[str, Any]]:
        """Compute distribution of threat categories in database."""
        total = db.query(func.count(PromptRecord.id)).scalar() or 0
        rows = (
            db.query(PromptRecord.attack_category, func.count(PromptRecord.id))
            .group_by(PromptRecord.attack_category)
            .all()
        )

        return [
            {
                "category": r[0],
                "count": r[1],
                "percentage": round((r[1] / total) * 100, 2) if total > 0 else 0.0,
            }
            for r in rows
        ]

    def run_evaluation(self) -> Dict[str, Any]:
        """Trigger empirical evaluation benchmark across all layers."""
        return evaluate_pipeline()


metrics_service = MetricsService()
