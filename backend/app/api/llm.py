"""LLM Gateway Chat endpoint with mandatory firewall interception."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.firewall import ChatRequest, ChatResponse, ChatMessage, AnalyzePromptRequest
from app.services.firewall_service import firewall_service

router = APIRouter(prefix="/api/llm", tags=["LLM Gateway"])


@router.post("/chat", response_model=ChatResponse, summary="Secure chat with LLM")
async def chat_gateway(request: ChatRequest, db: Session = Depends(get_db)):
    """Inspect user conversation via firewall before conditionally routing to upstream LLM."""
    # Find latest user message to inspect
    user_prompt = ""
    for m in reversed(request.messages):
        if m.role == "user":
            user_prompt = m.content
            break

    if not user_prompt:
        raise HTTPException(status_code=400, detail="No user message found in conversation payload.")

    # 1. Inspect prompt through the firewall
    firewall_req = AnalyzePromptRequest(
        prompt=user_prompt,
        forward_to_llm=True,  # Will only call LLM if ALLOW verdict is reached
        llm_provider=request.provider,
        llm_model=request.model,
    )
    firewall_verdict = await firewall_service.analyze_prompt(firewall_req, db=db)

    # 2. Enforce strict isolation: If BLOCKED or REVIEW, never return LLM response
    if firewall_verdict.decision in ("BLOCK", "REVIEW"):
        return ChatResponse(
            firewall=firewall_verdict,
            message=ChatMessage(
                role="assistant",
                content=firewall_verdict.blocked_message or "Prompt was blocked by security firewall."
            ),
            blocked=True,
        )

    # 3. If ALLOWED, return assistant response from upstream LLM
    return ChatResponse(
        firewall=firewall_verdict,
        message=ChatMessage(
            role="assistant",
            content=firewall_verdict.llm_response or "Prompt verified safe."
        ),
        blocked=False,
    )
