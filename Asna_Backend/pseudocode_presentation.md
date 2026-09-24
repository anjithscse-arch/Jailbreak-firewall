# Asna — Second Interim Presentation: Backend Gateway Pseudocode & Technical Explanation

**Student Name**: Asna  
**Module**: Backend API Gateway, Interception Pipeline & SQLite Telemetry  
**Project Title**: AI Prompt Injection and Jailbreak Detection Firewall  
**Base Paper**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation* (IEEE Access, Vol. 13, 2025)  

---

## 1. Formal Pseudocode (Algorithm 3)

```text
Algorithm 3: Asynchronous Security Gateway & Audit Logging Pipeline
Input  : HTTP POST Request to /check-prompt with JSON payload { "prompt": P }
Output : HTTP Response with JSON contract { "decision", "is_blocked", "reason", "severity", "latency_ms" }

Subroutine Initialize_Storage():
    1.  Open SQLite Database Connection: "firewall_logs.db"
    2.  Execute DDL:
            CREATE TABLE IF NOT EXISTS prompt_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                prompt TEXT NOT NULL,
                decision TEXT NOT NULL,
                is_blocked INTEGER NOT NULL,
                reason TEXT,
                severity TEXT NOT NULL,
                risk_score REAL NOT NULL,
                latency_ms REAL NOT NULL
            )

Endpoint Handler POST /check-prompt(Request):
    3.  if Request.prompt is empty or whitespace only then:
    4.      return HTTP_400_Bad_Request("Prompt must not be empty.")
    5.  end if

    6.  t_start ← High_Resolution_Timer()
    
    // Step 1: Direct synchronous call into Anjith's Layer-1 Rule Engine
    7.  rule_verdict ← Evaluate_Rules(Request.prompt)
    
    8.  t_elapsed_ms ← (High_Resolution_Timer() - t_start) * 1000

    9.  decision   ← rule_verdict.decision       // "BLOCK" or "PASS"
    10. is_blocked ← rule_verdict.is_blocked     // true or false
    11. reason     ← rule_verdict.primary_reason // e.g. "DIRECT_INSTRUCTION_OVERRIDE"
    12. severity   ← rule_verdict.max_severity   // "CRITICAL", "HIGH", "MEDIUM", "NONE"
    13. risk_score ← rule_verdict.risk_score     // 0.0 to 1.0

    // Step 2: Non-blocking asynchronous SQLite persistence
    14. try:
    15.     Insert_Audit_Record(
                timestamp = Current_UTC_ISO8601(),
                prompt = Request.prompt,
                decision = decision,
                is_blocked = (1 if is_blocked else 0),
                reason = reason,
                severity = severity,
                risk_score = risk_score,
                latency_ms = t_elapsed_ms
            )
    16. catch DatabaseError as err:
    17.     Log_Warning("Audit write skipped: " + err)
    18. end try

    // Step 3: Dispatch standardized response contract
    19. return HTTP_200_OK({
            "decision": decision,
            "is_blocked": is_blocked,
            "reason": reason,
            "severity": severity,
            "risk_score": risk_score,
            "layer": "RULE_ENGINE",
            "latency_ms": Round(t_elapsed_ms, 3)
        })

Endpoint Handler GET /logs(limit = 50):
    20. Query rows ← SELECT * FROM prompt_logs ORDER BY id DESC LIMIT limit
    21. return HTTP_200_OK(rows)
```

---

## 2. Step-by-Step Technical Explanation (For Presentation & Viva)

1. **Step 1: Input Validation & Sanitization Guard (Lines 3–5)**:
   - Rejects empty, truncated, or malformed JSON payloads immediately with an HTTP 400 Bad Request before running any pipeline operations, protecting the backend against denial-of-service attempts.

2. **Step 2: Low-Latency Defensive Layer Call (Lines 6–13)**:
   - Wires directly to **Anjith's Layer 1 Rule Engine** as a modular Python import.
   - Measures precise sub-millisecond execution time using high-resolution monotonic clocks (`time.perf_counter()`).
   - Obtains the structured verdict: `BLOCK` vs `PASS`, threat category reason, severity tier, and numeric risk score.

3. **Step 3: Fault-Tolerant SQLite Audit Trail (Lines 14–18)**:
   - Every user prompt, whether blocked or allowed, is recorded into `firewall_logs.db`.
   - Logging is wrapped in an isolated try-catch block so that any temporary disk I/O failure never drops the live security verdict for the user.

4. **Step 4: Standardized Endpoint Contract (Lines 19–21)**:
   - Emits a clean JSON response contract conforming strictly to OpenAPI / Swagger specifications.
   - Provides a separate `GET /logs` endpoint that enables **Aswathy's frontend** to fetch real-time inspection history dynamically.

---

## 3. Ready-to-Present Slide Points for Asna

### Slide: Backend Gateway Architecture & Request Interception
- **Framework**: High-performance FastAPI with asynchronous ASGI execution and Pydantic data validation.
- **Defensive Flow**: Proxies prompts directly into Layer 1 evaluation before touching any upstream LLM.
- **Contract Enforcement**: Standardized JSON contract returning verdict, threat reason, severity rating, and latency.
- **Audit Persistence**: Automatic SQLite logging capturing full audit trails (timestamp, prompt, risk score, execution latency).
- **Viva Defense Point**: *"By placing the firewall as an API gateway proxy, malicious prompts are halted at the boundary. If blocked, upstream token consumption and context poisoning are 100% prevented."*
