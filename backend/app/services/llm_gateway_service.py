"""LLM Gateway Router selecting and executing upstream model calls."""

import time
from typing import List, Dict, Any, Optional
from app.config import settings
from app.llm.base import LLMAdapter
from app.llm.mock_adapter import MockAdapter
from app.llm.ollama_adapter import OllamaAdapter
from app.llm.openai_adapter import OpenAICompatibleAdapter
from app.llm.rest_adapter import GenericRESTAdapter


class LLMGatewayService:
    """Dispatches approved prompts to configured or overridden upstream LLMs."""

    def __init__(self):
        self._adapters: Dict[str, LLMAdapter] = {
            "mock": MockAdapter(),
            "ollama": OllamaAdapter(),
            "openai": OpenAICompatibleAdapter(),
            "rest": GenericRESTAdapter(),
        }

    def get_adapter(self, provider_name: Optional[str] = None) -> LLMAdapter:
        """Select adapter instance by name or fallback to system default."""
        target = (provider_name or settings.LLM_PROVIDER).lower()
        if target not in self._adapters:
            return self._adapters["mock"]
        return self._adapters[target]

    async def call_llm(
        self,
        prompt: str,
        messages: Optional[List[Dict[str, str]]] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        """Execute upstream inference and track latency."""
        start_time = time.perf_counter()
        adapter = self.get_adapter(provider)

        # Build conversation format if only raw prompt is given
        if not messages:
            messages = [{"role": "user", "content": prompt}]

        res = await adapter.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        res["latency_ms"] = round(elapsed_ms, 2)
        return res


llm_gateway_service = LLMGatewayService()
