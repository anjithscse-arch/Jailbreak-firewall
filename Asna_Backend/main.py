"""Minimal FastAPI Firewall Backend Service.

Developer: Asna
Module: Backend API Gateway & Endpoint Wiring
Project: AI Prompt Injection and Jailbreak Detection Firewall

Features:
- /check-prompt endpoint: Validates incoming prompts against Anjith's Rule Engine
- /logs endpoint: Retrieves past inspection logs from SQLite
- /health endpoint: Service health check
"""

import os
import sys
import time
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure Anjith_Rule_Engine can be imported
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
RULE_ENGINE_DIR = os.path.join(PROJECT_ROOT, "Anjith_Rule_Engine")
if RULE_ENGINE_DIR not in sys.path:
    sys.path.insert(0, RULE_ENGINE_DIR)

from rules import evaluate_rules
import database

# Initialize FastAPI application
app = FastAPI(
    title="Prompt Injection Firewall API",
    description="Minimal Gateway API inspecting prompts via Layer 1 Rule Engine and SQLite logging.",
    version="1.0.0"
)

# Enable CORS for local frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Request and Response Contracts
# =============================================================================

class CheckPromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Raw user prompt string to be inspected")


class CheckPromptResponse(BaseModel):
    decision: str = Field(..., description="Firewall verdict: 'BLOCK' or 'PASS'")
    is_blocked: bool = Field(..., description="True if prompt was intercepted and blocked")
    reason: Optional[str] = Field(None, description="Primary attack category or rule that triggered")
    severity: str = Field(..., description="Severity level: CRITICAL, HIGH, MEDIUM, or NONE")
    risk_score: float = Field(..., description="Calculated threat risk score between 0.0 and 1.0")
    layer: str = Field(default="RULE_ENGINE", description="Defensive security layer making decision")
    latency_ms: float = Field(..., description="Processing latency in milliseconds")


class LogEntry(BaseModel):
    id: int
    timestamp: str
    prompt: str
    decision: str
    is_blocked: int
    reason: Optional[str]
    severity: str
    risk_score: float
    latency_ms: float


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/health", tags=["System"])
def health_check():
    """Returns service health status."""
    return {"status": "ok", "service": "Prompt Injection Firewall", "version": "1.0.0"}


@app.post("/check-prompt", response_model=CheckPromptResponse, tags=["Inspection"])
def check_prompt(req: CheckPromptRequest):
    """Inspects a prompt against Anjith's Layer 1 Rule Engine and logs to SQLite.
    
    - Input: `{"prompt": "string"}`
    - Output: `{"decision": "BLOCK" | "PASS", "is_blocked": bool, "reason": str, ...}`
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt must not be empty.")

    t0 = time.perf_counter()

    # 1. Wire directly to Anjith's Rule Engine
    rule_result = evaluate_rules(req.prompt)

    latency_ms = (time.perf_counter() - t0) * 1000

    decision = rule_result["decision"]
    is_blocked = rule_result["is_blocked"]
    reason = rule_result["primary_reason"]
    severity = rule_result["max_severity"]
    risk_score = rule_result["risk_score"]

    # 2. Log request into SQLite audit table
    try:
        database.log_request(
            prompt=req.prompt,
            decision=decision,
            is_blocked=is_blocked,
            reason=reason,
            severity=severity,
            risk_score=risk_score,
            latency_ms=latency_ms
        )
    except Exception as e:
        # Logging failure should not crash prompt inspection
        print(f"Warning: Failed to log request to SQLite: {e}")

    return CheckPromptResponse(
        decision=decision,
        is_blocked=is_blocked,
        reason=reason,
        severity=severity,
        risk_score=risk_score,
        layer="RULE_ENGINE",
        latency_ms=round(latency_ms, 3)
    )


@app.get("/logs", response_model=List[LogEntry], tags=["Audit"])
def get_logs(limit: int = 50):
    """Retrieves recent prompt inspection logs from SQLite."""
    logs = database.get_recent_logs(limit=limit)
    return logs


if __name__ == "__main__":
    import uvicorn
    print("[*] Starting Asna's FastAPI Firewall Backend on http://127.0.0.1:8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
