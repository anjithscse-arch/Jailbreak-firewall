"""Mock LLM Adapter for zero-cost, local, offline testing and demonstrations."""

import asyncio
from typing import List, Dict, Any, Optional
from app.llm.base import LLMAdapter


class MockAdapter(LLMAdapter):
    """Simulates an upstream LLM response with zero external network dependency."""

    async def generate(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = "demo-firewall-llm",
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        # Small artificial delay to simulate realistic LLM response latency
        await asyncio.sleep(0.05)

        last_user_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_message = m.get("content", "")
                break

        snippet = last_user_message[:50].strip()
        simulated_text = (
            f"Hello! I am the demo model operating behind the AI Prompt Firewall. "
            f"Your request ('{snippet}...') was vetted and found safe to process. "
            f"Here is a helpful, constructive answer to assist with your educational or development task."
        )

        return {
            "provider": "mock",
            "model": model or "demo-firewall-llm",
            "content": simulated_text,
            "usage": {
                "prompt_tokens": len(last_user_message.split()),
                "completion_tokens": len(simulated_text.split()),
                "total_tokens": len(last_user_message.split()) + len(simulated_text.split()),
            }
        }
