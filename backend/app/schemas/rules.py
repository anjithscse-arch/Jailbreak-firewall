"""Rule management schemas."""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class RuleCreateRequest(BaseModel):
    rule_code: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=3, max_length=128)
    description: str = Field(..., min_length=5)
    category: str = Field(...)
    pattern_type: str = Field(..., description="keyword, phrase, regex, structural, obfuscation, template, unicode")
    pattern: str = Field(..., min_length=1)
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    weight: float = Field(1.0, ge=0.1, le=5.0)
    enabled: bool = True
    case_sensitive: bool = False


class RuleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    pattern_type: Optional[str] = None
    pattern: Optional[str] = None
    severity: Optional[str] = None
    weight: Optional[float] = None
    enabled: Optional[bool] = None
    case_sensitive: Optional[bool] = None


class RuleResponse(BaseModel):
    id: int
    rule_code: str
    name: str
    description: str
    category: str
    pattern_type: str
    pattern: str
    severity: str
    weight: float
    enabled: bool
    case_sensitive: bool
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RuleTestRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    pattern_type: str
    pattern: str
    case_sensitive: bool = False


class RuleTestResponse(BaseModel):
    matched: bool
    matched_text: Optional[str] = None
    latency_ms: float
