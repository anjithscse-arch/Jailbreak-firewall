"""Common API response and pagination schemas."""

from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiErrorDetail(BaseModel):
    code: str = "ERROR"
    message: str
    details: Optional[Any] = None


class ApiResponse(BaseModel, Generic[T]):
    """Standardized API response envelope."""
    success: bool = True
    data: Optional[T] = None
    message: str = "Operation completed successfully"
    error: Optional[ApiErrorDetail] = None


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_count: int
    total_pages: int


class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    pagination: PaginationMeta
