"""Custom domain exceptions and error schemas."""

from typing import Optional, Any, Dict


class FirewallException(Exception):
    """Base exception for firewall domain errors."""
    def __init__(
        self,
        message: str,
        code: str = "FIREWALL_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class ValidationException(FirewallException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class AuthenticationException(FirewallException):
    def __init__(self, message: str = "Invalid credentials or authentication token"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_REQUIRED",
            status_code=401
        )


class AuthorizationException(FirewallException):
    def __init__(self, message: str = "Access denied: insufficient privileges"):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403
        )


class ResourceNotFoundException(FirewallException):
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' was not found.",
            code="NOT_FOUND",
            status_code=404
        )


class LLMProviderException(FirewallException):
    def __init__(self, message: str, provider: str):
        super().__init__(
            message=f"LLM Provider '{provider}' error: {message}",
            code="LLM_PROVIDER_ERROR",
            status_code=503,
            details={"provider": provider}
        )
