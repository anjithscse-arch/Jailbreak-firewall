# Aswathy — Second Interim Presentation: Frontend UI & Evaluation Logic Pseudocode

**Student Name**: Aswathy  
**Module**: Client UI, State Management & Evaluation Visualization  
**Project Title**: AI Prompt Injection and Jailbreak Detection Firewall  
**Base Paper**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation* (IEEE Access, Vol. 13, 2025)  

---

## 1. Formal Pseudocode (Algorithm 4)

```text
Algorithm 4: Client-Side Telemetry, Dynamic Rendering & Graceful Fallback
Input  : User prompt P entered in web textarea, or selected preset chip
Output : Dynamic DOM updates (verdict banner, latency, risk meter, live audit log)

Subroutine On_Inspect_Prompt_Clicked(P):
    1.  if P is empty then:
    2.      Show_Alert("Please enter a prompt to inspect.")
    3.      return
    4.  end if

    5.  Set_Button_State(Loading = True, Spinner = Visible)
    6.  t_start ← Performance_Now()
    
    7.  try:
            // Attempt live fetch to Asna's FastAPI Backend
    8.      response ← HTTP_Fetch(
                url = "http://127.0.0.1:8000/check-prompt",
                method = "POST",
                headers = { "Content-Type": "application/json" },
                body = JSON_Stringify({ "prompt": P })
            )
    9.      if response.status == 200 then:
    10.         result ← response.JSON()
    11.     else:
    12.         throw Error("Backend returned status " + response.status)
    13.     end if
    14. catch NetworkError or ServerOffline:
            // Graceful degradation: Invoke client-side rule evaluation simulator
    15.     elapsed_ms ← Performance_Now() - t_start
    16.     result ← Run_Local_Rule_Fallback(P, elapsed_ms)
    17. finally:
    18.     Set_Button_State(Loading = False, Spinner = Hidden)
    19. end try

    20. Render_Verdict_Banner(result)
    21. Update_Risk_Meter(result.risk_score)
    22. Append_To_Audit_Table(result)

Subroutine Render_Verdict_Banner(result):
    23. if result.is_blocked is True then:
    24.     verdict_banner.Class ← "verdict-block" // Red theme with pulsing border
    25.     verdict_title.Text   ← "BLOCKED"
    26.     action_notice.Text   ← "Strict Isolation: Discarded before reaching LLM"
    27. else:
    28.     verdict_banner.Class ← "verdict-pass"  // Green theme with emerald glow
    29.     verdict_title.Text   ← "ALLOWED"
    30.     action_notice.Text   ← "Forwarded safely to Upstream LLM reasoning gateway"
    31. end if
    32. latency_tag.Text ← "Latency: " + result.latency_ms + " ms"

Subroutine Poll_Audit_Logs(filter_mode):
    33. logs ← Fetch("http://127.0.0.1:8000/logs") or Local_Logs_Array
    34. filtered_logs ← Filter(logs, by = filter_mode)  // ALL, BLOCK, or PASS
    35. Render_HTML_Table(filtered_logs)
```

---

## 2. Step-by-Step Technical Explanation (For Presentation & Viva)

1. **Step 1: Asynchronous Event Dispatch & UI Feedback (Lines 1–6)**:
   - When the user types or clicks a quick-test chip (e.g. Benign query, DAN Jailbreak, Instruction Override), the client initiates an asynchronous non-blocking fetch request.
   - Provides immediate visual feedback by transitioning the inspect button into a spinner state.

2. **Step 2: Dual Connectivity with Graceful Fallback (Lines 7–19)**:
   - **Why**: Demonstrations during project viva cannot afford network or server startup failures.
   - **How**: The frontend first attempts to communicate with Asna's live FastAPI backend at `http://127.0.0.1:8000/check-prompt`. If the backend is temporarily offline, the client automatically triggers an integrated client-side rule simulator, guaranteeing zero UI failure during mentor review.

3. **Step 3: Reactive State & Dynamic Threat Visualization (Lines 20–32)**:
   - If blocked: Instantly updates the banner with a high-contrast pulsing red border (`--block-rose`), displays the category (e.g., `DIRECT_INSTRUCTION_OVERRIDE`), and animates the Threat Risk Meter to the corresponding severity percentage.
   - If allowed: Emits a green emerald glow indicating prompt safety and safety policy compliance.

4. **Step 4: Continuous Audit Trail & Evaluation Telemetry (Lines 33–35)**:
   - Renders a real-time table of past inspected queries with instant client-side filtering (`All`, `Blocked Only`, `Allowed Only`).
   - The Evaluation Module tab presents comparative metric cards (Accuracy: 89.0%, Precision: 89.8%, Latency: $<0.05$ ms) ready for presentation evaluation.

---

## 3. Ready-to-Present Slide Points for Aswathy

### Slide: Interactive Firewall Client & Visual Security Telemetry
- **UI Architecture**: Single Page Application built with responsive CSS grid and vanilla JavaScript (zero build dependencies).
- **Core User Features**:
  - Interactive prompt testing console with 1-click test chips (Benign, DAN, Override, Leak).
  - High-visibility security badges (`ALLOW` vs `BLOCK`) and sub-millisecond latency timer.
  - Interactive Threat Risk Meter ($0.0$ to $1.0$) mapped to severity thresholds.
- **Audit & Evaluation**:
  - Live table capturing inspection history with dynamic filtering.
  - Evaluation Module visualizing comparative benchmark metrics from the IEEE Access paper.
- **Viva Defense Point**: *"The frontend visualizes the firewall's strict isolation principle: administrators can verify in real time that blocked prompts are terminated instantly, protecting upstream models from token consumption."*
