"""OpenAI-compatible cloud LLM adapter."""

import httpx
from typing import List, Dict, Any, Optional
from app.llm.base import LLMAdapter
from app.config import settings
from app.core.exceptions import LLMProviderException


class OpenAICompatibleAdapter(LLMAdapter):
    """Integrates with OpenAI, Azure OpenAI, Groq, Together, vLLM, or any OpenAI-compatible endpoint."""

    def __init__(
        self,
        base_url: str = settings.OPENAI_BASE_URL,
        api_key: str = settings.OPENAI_API_KEY
    ):
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.api_key = api_key or ""

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise LLMProviderException(
                "OPENAI_API_KEY is not configured on the firewall gateway.",
                provider="openai"
            )

        target_model = model or settings.OPENAI_MODEL or "gpt-4o-mini"
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": target_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise LLMProviderException(
                        f"OpenAI API returned HTTP {resp.status_code}: {resp.text[:200]}",
                        provider="openai"
                    )
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return {
                    "provider": "openai",
                    "model": target_model,
                    "content": content,
                    "usage": data.get("usage", {}),
                }
        except httpx.TimeoutException:
            raise LLMProviderException(
                f"OpenAI API request timed out after {settings.LLM_TIMEOUT_SECONDS} seconds.",
                provider="openai"
            )
        except Exception as e:
            if isinstance(e, LLMProviderException):
                raise
            raise LLMProviderException(str(e), provider="openai")
