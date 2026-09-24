"""Rule management API endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models.rule import DetectionRule
from app.models.user import User
from app.dependencies import get_admin_user
from app.schemas.rules import (
    RuleCreateRequest,
    RuleUpdateRequest,
    RuleResponse,
    RuleTestRequest,
    RuleTestResponse,
)
from app.schemas.common import ApiResponse
from app.services.rule_engine_service import rule_engine_service

router = APIRouter(prefix="/api/rules", tags=["Rules"])


@router.get("", response_model=ApiResponse[List[RuleResponse]], summary="List detection rules")
async def list_rules(
    category: Optional[str] = None,
    severity: Optional[str] = None,
    enabled: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Retrieve detection rules with optional category, severity, and text filters."""
    query = db.query(DetectionRule)
    if category:
        query = query.filter(DetectionRule.category == category.upper())
    if severity:
        query = query.filter(DetectionRule.severity == severity.upper())
    if enabled is not None:
        query = query.filter(DetectionRule.enabled == enabled)
    if search:
        query = query.filter(
            (DetectionRule.name.ilike(f"%{search}%")) | (DetectionRule.rule_code.ilike(f"%{search}%"))
        )

    rules = query.order_by(DetectionRule.rule_code.asc()).all()
    return ApiResponse(success=True, data=rules)


@router.post("", response_model=ApiResponse[RuleResponse], summary="Create new detection rule")
async def create_rule(
    rule_in: RuleCreateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Create a new deterministic rule in Layer 1."""
    existing = db.query(DetectionRule).filter(DetectionRule.rule_code == rule_in.rule_code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Rule with code '{rule_in.rule_code}' already exists.")

    rule = DetectionRule(
        rule_code=rule_in.rule_code,
        name=rule_in.name,
        description=rule_in.description,
        category=rule_in.category,
        pattern_type=rule_in.pattern_type,
        pattern=rule_in.pattern,
        severity=rule_in.severity,
        weight=rule_in.weight,
        enabled=rule_in.enabled,
        case_sensitive=rule_in.case_sensitive,
        created_by=admin.username,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    # Invalidate in-memory rule cache
    rule_engine_service.reload_rules()

    return ApiResponse(success=True, message="Rule created successfully", data=rule)


@router.get("/{rule_id}", response_model=ApiResponse[RuleResponse], summary="Get rule details")
async def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Retrieve rule details by ID."""
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found.")
    return ApiResponse(success=True, data=rule)


@router.put("/{rule_id}", response_model=ApiResponse[RuleResponse], summary="Update detection rule")
async def update_rule(
    rule_id: int,
    rule_update: RuleUpdateRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Modify attributes of an existing detection rule."""
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found.")

    update_data = rule_update.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(rule, field, val)

    db.commit()
    db.refresh(rule)
    rule_engine_service.reload_rules()

    return ApiResponse(success=True, message="Rule updated successfully", data=rule)


@router.delete("/{rule_id}", response_model=ApiResponse[bool], summary="Delete detection rule")
async def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Delete a detection rule."""
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found.")

    db.delete(rule)
    db.commit()
    rule_engine_service.reload_rules()

    return ApiResponse(success=True, message="Rule deleted successfully", data=True)


@router.patch("/{rule_id}/toggle", response_model=ApiResponse[RuleResponse], summary="Toggle rule state")
async def toggle_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Enable or disable a detection rule dynamically."""
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule with ID '{rule_id}' not found.")

    rule.enabled = not rule.enabled
    db.commit()
    db.refresh(rule)
    rule_engine_service.reload_rules()

    status_str = "enabled" if rule.enabled else "disabled"
    return ApiResponse(success=True, message=f"Rule successfully {status_str}", data=rule)


@router.post("/test", response_model=ApiResponse[RuleTestResponse], summary="Test rule pattern")
async def test_rule_pattern(req: RuleTestRequest):
    """Evaluate candidate pattern against a test prompt without saving."""
    res = rule_engine_service.test_pattern(
        prompt=req.prompt,
        pattern_type=req.pattern_type,
        pattern=req.pattern,
        case_sensitive=req.case_sensitive,
    )
    return ApiResponse(success=True, data=RuleTestResponse(**res))
