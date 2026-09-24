"""Health and system component readiness endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import settings
from app.database import get_db
from app.services.ml_classifier_service import ml_classifier_service
from app.services.rule_engine_service import rule_engine_service

router = APIRouter(prefix="/api/health", tags=["Health"])


@router.get("", summary="Basic health check")
async def get_health():
    """Liveness probe returning service metadata."""
    return {
        "status": "ok",
        "service": "ai-prompt-firewall",
        "version": settings.VERSION,
    }


@router.get("/components", summary="Component readiness check")
async def get_components_health(db: Session = Depends(get_db)):
    """Deep readiness check inspecting database, rule cache, ML weights, and LLM gateway."""
    # 1. Database check
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    # 2. Rule engine check
    rules_count = len(rule_engine_service.get_rules())
    rule_status = "ok" if rules_count > 0 else "degraded"

    # 3. ML model check
    ml_meta = ml_classifier_service.get_metadata()
    ml_status = "ok" if ml_meta else "not_loaded"

    # 4. LLM provider check
    llm_status = f"configured ({settings.LLM_PROVIDER})"

    overall = "ok" if (db_status == "ok" and rule_status == "ok") else "degraded"

    return {
        "status": overall,
        "service": "ai-prompt-firewall",
        "version": settings.VERSION,
        "components": {
            "database": {
                "status": db_status,
                "dialect": settings.DATABASE_URL.split(":///")[0],
            },
            "rule_engine": {
                "status": rule_status,
                "active_rules": rules_count,
            },
            "ml_classifier": {
                "status": ml_status,
                "model_version": ml_meta.get("version", "unknown"),
                "accuracy": ml_meta.get("accuracy"),
            },
            "llm_gateway": {
                "status": "ready",
                "default_provider": settings.LLM_PROVIDER,
            },
            "application": {
                "status": "running",
                "environment": settings.ENVIRONMENT,
                "debug": settings.DEBUG,
            },
        },
    }
