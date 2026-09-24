"""Generic REST LLM adapter."""

import httpx
from typing import List, Dict, Any, Optional
from app.llm.base import LLMAdapter
from app.config import settings
from app.core.exceptions import LLMProviderException


class GenericRESTAdapter(LLMAdapter):
    """Integrates with custom enterprise REST prediction endpoints."""

    def __init__(self, endpoint_url: str = settings.REST_LLM_URL):
        self.endpoint_url = endpoint_url

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        if not self.endpoint_url:
            raise LLMProviderException(
                "REST_LLM_URL is not configured for generic REST adapter.",
                provider="rest"
            )

        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                resp = await client.post(self.endpoint_url, json=payload)
                if resp.status_code != 200:
                    raise LLMProviderException(
                        f"Custom REST LLM returned HTTP {resp.status_code}: {resp.text[:200]}",
                        provider="rest"
                    )
                data = resp.json()
                content = data.get("content") or data.get("response") or str(data)
                return {
                    "provider": "rest",
                    "model": model or "custom-rest",
                    "content": content,
                    "usage": data.get("usage", {}),
                }
        except Exception as e:
            if isinstance(e, LLMProviderException):
                raise
            raise LLMProviderException(str(e), provider="rest")
