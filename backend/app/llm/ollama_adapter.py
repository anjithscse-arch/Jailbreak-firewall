"""Ollama local LLM adapter."""

import httpx
from typing import List, Dict, Any, Optional
from app.llm.base import LLMAdapter
from app.config import settings
from app.core.exceptions import LLMProviderException


class OllamaAdapter(LLMAdapter):
    """Integrates with locally hosted Ollama instances (e.g., llama3.2, mistral, phi)."""

    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        target_model = model or settings.OLLAMA_MODEL
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": target_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    raise LLMProviderException(
                        f"Ollama returned HTTP {resp.status_code}: {resp.text[:200]}",
                        provider="ollama"
                    )
                data = resp.json()
                content = data.get("message", {}).get("content", "")
                return {
                    "provider": "ollama",
                    "model": target_model,
                    "content": content,
                    "usage": {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                    }
                }
        except httpx.ConnectError:
            raise LLMProviderException(
                f"Could not connect to Ollama at {self.base_url}. Ensure Ollama is running.",
                provider="ollama"
            )
        except httpx.TimeoutException:
            raise LLMProviderException(
                f"Ollama request timed out after {settings.LLM_TIMEOUT_SECONDS} seconds.",
                provider="ollama"
            )
        except Exception as e:
            if isinstance(e, LLMProviderException):
                raise
            raise LLMProviderException(str(e), provider="ollama")
