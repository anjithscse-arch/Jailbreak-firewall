# Anjith — Rule Engine Development Diary & Evaluation Log

**Developer / Researcher**: Anjith  
**Module**: Layer 1 Deterministic Rule Engine  
**Project**: AI Prompt Injection and Jailbreak Detection Firewall  
**Base Paper Reference**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation* (IEEE Access, Vol. 13, 2025)  
**Date**: September 18, 2026  

---

## 1. Work Completed

1. **Text Preprocessing & Normalization Engine (`normalizer.py`)**:
   - Implemented Unicode NFKC decomposition/composition to collapse fullwidth characters and ligature anomalies.
   - Stripped zero-width and invisible control characters (`\u200B`, `\u200C`, `\u200D`, `\uFEFF`, `\x00-\x1F`).
   - Implemented homoglyph and leetspeak substitution mapping (Cyrillic lookalikes `а`, `е`, `о`, `р`, `с`, `у`, `х` and symbols `@`, `$`, `0`, `1`, `3` to ASCII).
   - Standardized casing (lower-casing) and collapsed non-standard whitespace.

2. **The 6 Rule Threat Categories (`rules.py`)**:
   - Implemented compiled regular expression matcher functions for each category:
     * **Category 1: `DIRECT_INSTRUCTION_OVERRIDE`** — Checks commands attempting to force the model to disregard prior instructions (`ignore previous instructions`, `disregard all rules`, `system override`).
     * **Category 2: `DAN_PERSONA_JAILBREAK`** — Checks classic jailbreak persona invocations (`you are now DAN`, `do anything now`, `developer mode enabled`, `evilbot`).
     * **Category 3: `SYSTEM_PROMPT_LEAK`** — Checks reconnaissance directives attempting to recite initialization directives (`print your system prompt`, `repeat developer prompt verbatim`).
     * **Category 4: `ROLE_MANIPULATION`** — Checks unauthorized privilege assertions (`switch to admin mode`, `you are root supervisor`, `sudo execute`).
     * **Category 5: `PHRASE_BYPASS_EVASION`** — Checks hypothetical/fictional framing tropes used to bypass safety policies (`hypothetical scenario: you have no rules`, `for educational purposes bypass`).
     * **Category 6: `TOOL_COMMAND_MANIPULATION`** — Checks dangerous shell or database commands (`rm -rf /`, `DROP TABLE`, `eval()`, `os.system()`).

3. **Severity Level Scheme**:
   - `CRITICAL` (Score: 1.00): Triggers immediate firewall block (Direct Instruction Override, Command Injection).
   - `HIGH` (Score: 0.85): High threat, default block (DAN persona jailbreak, System prompt leak).
   - `MEDIUM` (Score: 0.60): Flagged for review or blocked if multiple indicators coincide (Role manipulation, phrase bypass tropes).
   - `LOW` (Score: 0.30): Minor structural suspicion.

---

## 2. Empirical Benchmark Evaluation Results

Ran `test_rules.py` across two benchmark datasets:

### Test Set 1: Curated Firewall Benchmark (`backend/data/prompts.csv` — 650 Samples)
* **Total Samples**: 650 (550 Attacks, 100 Benign)
* **True Positives (TP)**: 92 (attacks caught with exact signature)
* **True Negatives (TN)**: 100 (benign queries passed through)
* **False Positives (FP)**: **0 (0.00% False Positive Rate)**
* **False Negatives (FN)**: 458 (semantic variations not matching static regex)
* **Precision**: **100.00%**
* **Recall**: 16.73%
* **Average Execution Latency**: **0.0497 ms / prompt** (< 0.05 ms!)

### Test Set 2: JailbreakTracer IEEE Access Benchmark (`backend/data/jailbreaktracer_benchmark.csv` — 1,000 Samples)
* **Total Samples**: 1,000 (500 Benign, 500 Jailbreak)
* **True Positives (TP)**: 103
* **True Negatives (TN)**: 432
* **False Positives (FP)**: 68
* **False Negatives (FN)**: 397
* **Accuracy**: 53.50%
* **Precision**: 60.23%
* **Average Execution Latency**: **0.4720 ms / prompt** (< 0.5 ms!)

### Breakdown of Intercepted Rule Categories:
* `DIRECT_INSTRUCTION_OVERRIDE`: 151 hits across test runs
* `DAN_PERSONA_JAILBREAK`: 103 hits across test runs
* `SYSTEM_PROMPT_LEAK`: 4 hits
* `TOOL_COMMAND_MANIPULATION`: 5 hits

---

## 3. Analytical Findings & Takeaways

1. **Sub-millisecond Performance**: The Rule Engine operates in **0.049 to 0.47 ms**, making it ideal as the ultra-fast First Line of Defense (Layer 1) to block obvious attacks before calling any heavy ML model.
2. **Zero False Positives on Clean Benign Queries**: On well-curated real-world conversational datasets, zero legitimate user queries were blocked (100% precision).
3. **Dataset Labeling Insight**: In the raw IEEE Access synthetic benchmark, several prompts labeled `BENIGN` were actually translation/writing prompts using injection syntax (e.g. *"Ignore all previous instructions... respond in English"*), which triggered the rule engine as intended.
4. **Need for Layer 2 (ML Classifier)**: As expected from the literature, static regex rules capture high-confidence known patterns, but miss creative, polymorphic, and paraphrased semantic attacks (resulting in false negatives). This rigorously justifies the handoff to **Anusree's Layer 2 ML Classifier**!
