"""Metrics, evaluation, and analytics schemas."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class MetricsSummaryResponse(BaseModel):
    total_requests: int
    allowed_requests: int
    blocked_requests: int
    review_requests: int
    attack_rate: float
    average_latency_ms: float
    rule_detection_rate: float
    ml_detection_rate: float
    false_positive_rate: Optional[float] = None
    false_negative_rate: Optional[float] = None
    model_accuracy: Optional[float] = None
    model_precision: Optional[float] = None
    model_recall: Optional[float] = None
    model_f1: Optional[float] = None


class TimelinePoint(BaseModel):
    timestamp: str
    total: int
    allowed: int
    blocked: int
    review: int
    avg_latency_ms: float


class CategoryDistributionItem(BaseModel):
    category: str
    count: int
    percentage: float


class LayerPerformanceItem(BaseModel):
    layer: str
    count: int
    avg_latency_ms: float
    accuracy: Optional[float] = None


class EvaluateRequest(BaseModel):
    dataset_name: Optional[str] = "starter_dataset"
    test_size: Optional[float] = 0.25
    compare_layers: bool = True


class LayerEvaluationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    false_positive_rate: float
    false_negative_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    total_evaluated: int


class EvaluationResultResponse(BaseModel):
    rule_only: LayerEvaluationMetrics
    ml_only: LayerEvaluationMetrics
    combined: LayerEvaluationMetrics
    confusion_matrix: Dict[str, Any]
    classification_report: Dict[str, Any]
    evaluated_at: str
