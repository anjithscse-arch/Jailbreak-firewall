"""Firewall analysis request and response schemas."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AnalyzePromptRequest(BaseModel):
    """Payload for single prompt security evaluation."""
    prompt: str = Field(..., min_length=1, max_length=10000, description="User prompt to inspect")
    conversation_id: Optional[str] = Field(None, max_length=64)
    user_id: Optional[str] = Field(None, max_length=64)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    forward_to_llm: bool = Field(False, description="Forward to LLM if classified as safe")
    llm_provider: Optional[str] = Field(None, description="Override default LLM provider")
    llm_model: Optional[str] = Field(None, description="Override default LLM model")


class MatchedRuleSchema(BaseModel):
    rule_id: str
    name: str
    category: str
    severity: str
    score: float
    description: str
    matched_text: Optional[str] = None


class TopFeatureSchema(BaseModel):
    feature: str
    weight: float
    direction: str = "attack"  # "attack" or "benign"


class MLResultSchema(BaseModel):
    label: str
    confidence: float
    probabilities: Optional[Dict[str, float]] = None
    top_features: List[TopFeatureSchema] = Field(default_factory=list)
    model_version: Optional[str] = None


class ExplanationSchema(BaseModel):
    summary: str
    reasons: List[str] = Field(default_factory=list)
    evidence: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    recommended_action: str


class LLMResponseDetail(BaseModel):
    provider: str
    model: str
    content: str
    latency_ms: float
    usage: Optional[Dict[str, Any]] = Field(default_factory=dict)
    knowledge_context: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class AnalyzePromptResponse(BaseModel):
    """Primary response returned by the firewall."""
    request_id: str
    decision: str  # ALLOW | BLOCK | REVIEW
    is_attack: bool
    attack_category: str
    confidence: float
    risk_score: float
    processing_time_ms: float
    detected_by: str  # RULE_ENGINE | ML_CLASSIFIER | BOTH | NONE
    normalized_prompt: Optional[str] = None
    matched_rules: List[MatchedRuleSchema] = Field(default_factory=list)
    ml_result: Optional[MLResultSchema] = None
    explanation: ExplanationSchema
    llm_response: Optional[str] = None
    llm_metadata: Optional[LLMResponseDetail] = None
    blocked_message: Optional[str] = None
    created_at: str


class BatchAnalyzeRequest(BaseModel):
    prompts: List[str] = Field(..., min_length=1, max_length=50)


class BatchAnalyzeResponse(BaseModel):
    total: int
    allowed: int
    blocked: int
    review: int
    processing_time_ms: float
    results: List[AnalyzePromptResponse]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1)
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 512


class ChatResponse(BaseModel):
    firewall: AnalyzePromptResponse
    message: Optional[ChatMessage] = None
    blocked: bool
