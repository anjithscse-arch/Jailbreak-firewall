"""Audit logging API router."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.prompt_record import PromptRecord
from app.models.user import User
from app.dependencies import get_admin_user
from app.schemas.logs import (
    PromptRecordResponse,
    LogDetailResponse,
    LogStatisticsResponse,
    DetectionEventSchema,
)
from app.schemas.common import ApiResponse, PaginatedData
from app.services.logging_service import logging_service

router = APIRouter(prefix="/api/logs", tags=["Audit Logs"])


@router.get("", response_model=ApiResponse[PaginatedData[PromptRecordResponse]], summary="Query audit logs")
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    decision: Optional[str] = None,
    category: Optional[str] = None,
    detected_by: Optional[str] = None,
    search: Optional[str] = None,
    min_confidence: Optional[float] = None,
    max_confidence: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Retrieve filtered, paginated security audit records."""
    res = logging_service.get_logs(
        db=db,
        page=page,
        page_size=page_size,
        decision=decision,
        category=category,
        detected_by=detected_by,
        search=search,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        start_date=start_date,
        end_date=end_date,
    )
    return ApiResponse(
        success=True,
        data=PaginatedData(
            items=res["items"],
            pagination=res["pagination"]
        ),
    )


@router.get("/statistics", response_model=ApiResponse[LogStatisticsResponse], summary="Log statistics")
async def get_log_statistics(db: Session = Depends(get_db)):
    """Fetch high-level aggregation statistics across audit records."""
    stats = logging_service.get_statistics(db)
    return ApiResponse(success=True, data=LogStatisticsResponse(**stats))


@router.get("/{request_id}", response_model=ApiResponse[LogDetailResponse], summary="Get log details")
async def get_log_detail(request_id: str, db: Session = Depends(get_db)):
    """Fetch detailed log including linked detection events for a request ID."""
    res = logging_service.get_log_by_request_id(db, request_id)
    if not res:
        raise HTTPException(status_code=404, detail=f"Audit record for '{request_id}' not found.")

    record = res["record"]
    events = [DetectionEventSchema.from_orm(e) for e in res["events"]]

    detail = LogDetailResponse(
        id=record.id,
        request_id=record.request_id,
        conversation_id=record.conversation_id,
        user_id=record.user_id,
        original_prompt_hash=record.original_prompt_hash,
        redacted_prompt=record.redacted_prompt,
        prompt_length=record.prompt_length,
        decision=record.decision,
        attack_category=record.attack_category,
        confidence=record.confidence,
        risk_score=record.risk_score,
        detected_by=record.detected_by,
        processing_time_ms=record.processing_time_ms,
        llm_provider=record.llm_provider,
        llm_model=record.llm_model,
        llm_called=record.llm_called,
        llm_response=record.llm_response,
        created_at=record.created_at,
        events=events,
    )

    return ApiResponse(success=True, data=detail)


@router.delete("/{request_id}", response_model=ApiResponse[bool], summary="Delete log entry")
async def delete_log(
    request_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Delete a specific audit log entry (Admin only)."""
    record = db.query(PromptRecord).filter(PromptRecord.request_id == request_id).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Log record '{request_id}' not found.")

    db.delete(record)
    db.commit()
    return ApiResponse(success=True, message="Log entry deleted successfully", data=True)
