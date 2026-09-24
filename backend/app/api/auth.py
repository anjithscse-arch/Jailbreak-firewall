"""Authentication API router."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.dependencies import get_current_user
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse
from app.schemas.common import ApiResponse
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=ApiResponse[TokenResponse], summary="Admin login")
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate administrator and return JWT bearer token."""
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    token = create_access_token(data={"sub": user.username, "role": user.role})

    return ApiResponse(
        success=True,
        message="Authentication successful",
        data=TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            username=user.username,
            role=user.role,
        ),
    )


@router.get("/me", response_model=ApiResponse[UserResponse], summary="Current user profile")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Return profile data for the authenticated session."""
    return ApiResponse(
        success=True,
        message="Profile retrieved",
        data=UserResponse.from_orm(current_user),
    )
