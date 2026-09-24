"""Metrics and benchmark evaluation API router."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.metrics import (
    MetricsSummaryResponse,
    TimelinePoint,
    CategoryDistributionItem,
    EvaluationResultResponse,
    EvaluateRequest,
)
from app.schemas.common import ApiResponse
from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/api/metrics", tags=["Metrics & Evaluation"])


@router.get("/summary", response_model=ApiResponse[MetricsSummaryResponse], summary="Firewall summary metrics")
async def get_summary(db: Session = Depends(get_db)):
    """Return executive KPI counters and model performance summaries."""
    summary = metrics_service.get_summary(db)
    return ApiResponse(success=True, data=MetricsSummaryResponse(**summary))


@router.get("/timeline", response_model=ApiResponse[List[TimelinePoint]], summary="Request traffic timeline")
async def get_timeline(db: Session = Depends(get_db)):
    """Return hourly request traffic metrics for visual plotting."""
    timeline = metrics_service.get_timeline(db)
    return ApiResponse(success=True, data=[TimelinePoint(**t) for t in timeline])


@router.get("/categories", response_model=ApiResponse[List[CategoryDistributionItem]], summary="Threat category distribution")
async def get_categories(db: Session = Depends(get_db)):
    """Return attack category breakdown for pie / bar charts."""
    dist = metrics_service.get_categories(db)
    return ApiResponse(success=True, data=[CategoryDistributionItem(**d) for d in dist])


@router.post("/evaluate", response_model=ApiResponse[EvaluationResultResponse], summary="Run comparative evaluation")
async def trigger_evaluation(req: EvaluateRequest = EvaluateRequest()):
    """Run empirical benchmark comparing Rule-Only, ML-Only, and Combined Two-Layer Firewall."""
    result = metrics_service.run_evaluation()
    return ApiResponse(
        success=True,
        message="Evaluation benchmark completed successfully",
        data=EvaluationResultResponse(**result)
    )
