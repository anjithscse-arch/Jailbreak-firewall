"""Base interface for model-agnostic LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMAdapter(ABC):
    """Abstract base class for upstream Large Language Model adapters."""

    @abstractmethod
    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        """Send approved conversation to the upstream LLM and return structured completion."""
        pass
