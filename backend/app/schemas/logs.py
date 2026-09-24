"""Audit logs schemas."""

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


class DetectionEventSchema(BaseModel):
    id: int
    rule_id: Optional[str]
    detection_layer: str
    category: str
    severity: str
    confidence: float
    reason: str
    matched_text_redacted: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PromptRecordResponse(BaseModel):
    id: int
    request_id: str
    conversation_id: Optional[str]
    user_id: Optional[str]
    original_prompt_hash: str
    redacted_prompt: str
    prompt_length: int
    decision: str
    attack_category: str
    confidence: float
    risk_score: float
    detected_by: str
    processing_time_ms: float
    llm_provider: Optional[str]
    llm_model: Optional[str]
    llm_called: bool
    created_at: datetime

    class Config:
        from_attributes = True


class LogDetailResponse(PromptRecordResponse):
    llm_response: Optional[str] = None
    events: List[DetectionEventSchema] = []


class LogStatisticsResponse(BaseModel):
    total_logs: int
    allowed_count: int
    blocked_count: int
    review_count: int
    avg_latency_ms: float
    layer_counts: dict
    category_counts: dict
