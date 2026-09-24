"""Security utilities for hashing, JWT token handling, and prompt sanitization."""

import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import bcrypt
from jose import jwt, JWTError

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_prompt(prompt: str) -> str:
    """Produce a deterministic SHA-256 hash of a prompt for audit deduplication without storing raw content."""
    return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()


# Regex patterns for sensitive tokens to redact
SECRET_PATTERNS = [
    re.compile(r"sk-[a-zA-Z0-9_-]{20,}", re.IGNORECASE),                    # OpenAI-like API keys
    re.compile(r"ghp_[a-zA-Z0-9]{20,}", re.IGNORECASE),                     # GitHub tokens
    re.compile(r"(?:bearer\s+)?[a-zA-Z0-9_\-\.]{50,}", re.IGNORECASE),      # Long JWTs/keys
    re.compile(r"(?:password|passwd|pwd|secret)\s*[:=]\s*[^\s]+", re.I),     # Key-value secrets
]


def redact_prompt(prompt: str, max_chars: int = 150) -> str:
    """Sanitize and safely truncate prompt text for audit logging."""
    if not prompt:
        return ""

    sanitized = prompt
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)

    sanitized = sanitized.strip()
    if len(sanitized) > max_chars:
        return sanitized[:max_chars] + "... [TRUNCATED]"
    return sanitized


def redact_matched_text(text: str, max_chars: int = 60) -> str:
    """Safely redact matched phrase for security event reporting."""
    if not text:
        return ""
    clean = text.strip().replace("\n", " ")
    if len(clean) > max_chars:
        return clean[:max_chars] + "..."
    return clean
