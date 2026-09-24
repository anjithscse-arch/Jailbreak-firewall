"""Logging Service managing persistent security audit logs and detection events."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.config import settings
from app.core.security import hash_prompt, redact_prompt
from app.models.prompt_record import PromptRecord
from app.models.detection_event import DetectionEvent


class LoggingService:
    """Records immutable security events and audit records."""

    def record_prompt_transaction(
        self,
        db: Session,
        request_id: str,
        prompt: str,
        decision: str,
        attack_category: str,
        confidence: float,
        risk_score: float,
        detected_by: str,
        processing_time_ms: float,
        rule_result: Dict[str, Any],
        ml_result: Dict[str, Any],
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_called: bool = False,
        llm_response: Optional[str] = None,
    ) -> PromptRecord:
        """Persist prompt transaction and associated detection events."""
        # Prompt sanitization according to privacy policy
        redacted = prompt if settings.LOG_FULL_PROMPTS else redact_prompt(prompt, max_chars=300)
        p_hash = hash_prompt(prompt)

        record = PromptRecord(
            request_id=request_id,
            conversation_id=conversation_id,
            user_id=user_id,
            original_prompt_hash=p_hash,
            redacted_prompt=redacted,
            prompt_length=len(prompt),
            decision=decision,
            attack_category=attack_category,
            confidence=confidence,
            risk_score=risk_score,
            detected_by=detected_by,
            processing_time_ms=processing_time_ms,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_called=llm_called,
            llm_response=llm_response,
            created_at=datetime.now(timezone.utc),
        )

        db.add(record)

        # Record rule match events
        for r in rule_result.get("matches", []):
            event = DetectionEvent(
                request_id=request_id,
                rule_id=r.get("rule_id"),
                detection_layer="RULE_ENGINE",
                category=r.get("category", attack_category),
                severity=r.get("severity", "MEDIUM"),
                confidence=r.get("score", 0.0),
                reason=f"Matched deterministic rule '{r.get('name')}'",
                matched_text_hash=hash_prompt(r.get("matched_text", "")) if r.get("matched_text") else None,
                matched_text_redacted=r.get("matched_text"),
                created_at=datetime.now(timezone.utc),
            )
            db.add(event)

        # Record ML detection event if flagged
        if ml_result and ml_result.get("label") != "BENIGN":
            event = DetectionEvent(
                request_id=request_id,
                rule_id=ml_result.get("model_version"),
                detection_layer="ML_CLASSIFIER",
                category=ml_result.get("label", attack_category),
                severity="HIGH" if ml_result.get("confidence", 0) >= 0.80 else "MEDIUM",
                confidence=ml_result.get("confidence", 0.0),
                reason=f"ML Classifier predicted {ml_result.get('label')} with confidence {ml_result.get('confidence')}",
                matched_text_hash=None,
                matched_text_redacted=None,
                created_at=datetime.now(timezone.utc),
            )
            db.add(event)

        db.commit()
        db.refresh(record)
        return record

    def get_logs(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        decision: Optional[str] = None,
        category: Optional[str] = None,
        detected_by: Optional[str] = None,
        search: Optional[str] = None,
        min_confidence: Optional[float] = None,
        max_confidence: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Fetch paginated audit log entries with multi-attribute filtering."""
        query = db.query(PromptRecord)

        if decision:
            query = query.filter(PromptRecord.decision == decision.upper())
        if category:
            query = query.filter(PromptRecord.attack_category == category.upper())
        if detected_by:
            query = query.filter(PromptRecord.detected_by == detected_by.upper())
        if search:
            query = query.filter(PromptRecord.redacted_prompt.ilike(f"%{search}%"))
        if min_confidence is not None:
            query = query.filter(PromptRecord.confidence >= min_confidence)
        if max_confidence is not None:
            query = query.filter(PromptRecord.confidence <= max_confidence)
        if start_date:
            query = query.filter(PromptRecord.created_at >= start_date)
        if end_date:
            query = query.filter(PromptRecord.created_at <= end_date)

        total_count = query.count()
        total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1

        items = (
            query.order_by(desc(PromptRecord.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            }
        }

    def get_log_by_request_id(self, db: Session, request_id: str) -> Optional[Dict[str, Any]]:
        """Fetch single audit log with linked detection events."""
        record = db.query(PromptRecord).filter(PromptRecord.request_id == request_id).first()
        if not record:
            return None

        events = db.query(DetectionEvent).filter(DetectionEvent.request_id == request_id).all()
        return {
            "record": record,
            "events": events,
        }

    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Calculate high-level telemetry on stored logs."""
        total = db.query(func.count(PromptRecord.id)).scalar() or 0
        allowed = db.query(func.count(PromptRecord.id)).filter(PromptRecord.decision == "ALLOW").scalar() or 0
        blocked = db.query(func.count(PromptRecord.id)).filter(PromptRecord.decision == "BLOCK").scalar() or 0
        review = db.query(func.count(PromptRecord.id)).filter(PromptRecord.decision == "REVIEW").scalar() or 0
        avg_lat = db.query(func.avg(PromptRecord.processing_time_ms)).scalar() or 0.0

        # Layer counts
        layer_rows = (
            db.query(PromptRecord.detected_by, func.count(PromptRecord.id))
            .group_by(PromptRecord.detected_by)
            .all()
        )
        layer_counts = {r[0]: r[1] for r in layer_rows}

        # Category counts
        cat_rows = (
            db.query(PromptRecord.attack_category, func.count(PromptRecord.id))
            .group_by(PromptRecord.attack_category)
            .all()
        )
        category_counts = {r[0]: r[1] for r in cat_rows}

        return {
            "total_logs": total,
            "allowed_count": allowed,
            "blocked_count": blocked,
            "review_count": review,
            "avg_latency_ms": round(float(avg_lat), 2),
            "layer_counts": layer_counts,
            "category_counts": category_counts,
        }


logging_service = LoggingService()
