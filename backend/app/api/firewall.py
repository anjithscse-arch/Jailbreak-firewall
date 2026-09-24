"""Firewall inspection API endpoints."""

import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.schemas.firewall import (
    AnalyzePromptRequest,
    AnalyzePromptResponse,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)
from app.services.firewall_service import firewall_service

router = APIRouter(prefix="/api/firewall", tags=["Firewall"])


@router.post("/analyze", response_model=AnalyzePromptResponse, summary="Analyze prompt security")
async def analyze_prompt(request: AnalyzePromptRequest, db: Session = Depends(get_db)):
    """Evaluate prompt against Layer 1 rules and Layer 2 ML classifier."""
    return await firewall_service.analyze_prompt(request, db=db)


@router.post("/analyze-batch", response_model=BatchAnalyzeResponse, summary="Batch prompt security inspection")
async def analyze_prompt_batch(request: BatchAnalyzeRequest, db: Session = Depends(get_db)):
    """Evaluate multiple prompts in a single request."""
    if len(request.prompts) > settings.MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum limit of {settings.MAX_BATCH_SIZE} prompts."
        )

    start_time = time.perf_counter()
    results = []
    allowed_cnt = 0
    blocked_cnt = 0
    review_cnt = 0

    for p in request.prompts:
        single_req = AnalyzePromptRequest(prompt=p, forward_to_llm=False)
        res = await firewall_service.analyze_prompt(single_req, db=db)
        results.append(res)
        if res.decision == "ALLOW":
            allowed_cnt += 1
        elif res.decision == "BLOCK":
            blocked_cnt += 1
        else:
            review_cnt += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return BatchAnalyzeResponse(
        total=len(request.prompts),
        allowed=allowed_cnt,
        blocked=blocked_cnt,
        review=review_cnt,
        processing_time_ms=round(elapsed_ms, 2),
        results=results,
    )
