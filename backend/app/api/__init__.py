"""API package router aggregation."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.firewall import router as firewall_router
from app.api.llm import router as llm_router
from app.api.rules import router as rules_router
from app.api.logs import router as logs_router
from app.api.metrics import router as metrics_router
from app.api.datasets import router as datasets_router
from app.api.models import router as models_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(firewall_router)
api_router.include_router(llm_router)
api_router.include_router(rules_router)
api_router.include_router(logs_router)
api_router.include_router(metrics_router)
api_router.include_router(datasets_router)
api_router.include_router(models_router)

__all__ = ["api_router"]
