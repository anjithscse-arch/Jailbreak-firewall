# Anjith — Second Interim Presentation: Rule Engine Pseudocode & Technical Explanation

**Student Name**: Anjith  
**Module**: Layer 1 Deterministic Rule Engine & Text Normalization  
**Project Title**: AI Prompt Injection and Jailbreak Detection Firewall  
**Base Paper**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation* (IEEE Access, Vol. 13, 2025)  

---

## 1. Formal Pseudocode (Algorithm 1)

```text
Algorithm 1: Layer-1 Deterministic Threat Detection & Evasion Sanitization
Input  : Raw prompt string P submitted by client
Output : Tuple (Verdict in {BLOCK, PASS}, Reason, Severity, RiskScore)

Subroutine Normalize_And_Sanitize(text):
    1.  text_nfkc ← Unicode_NFKC_Normalize(text)
    2.  text_clean ← Strip_Zero_Width_And_Control_Chars(text_nfkc)
    3.  text_homo ← Replace_Homoglyphs_With_ASCII(text_clean)
        // Maps Cyrillic (а, е, о, р, с, у, х) and leetspeak (@, $, 0, 1, 3) to standard Latin
    4.  text_lower ← To_Lowercase(text_homo)
    5.  text_norm ← Collapse_Whitespace(text_lower)
    6.  return text_norm

Main Algorithm:
    7.  P_norm ← Normalize_And_Sanitize(P)
    8.  matched_rules ← empty list
    
    9.  For each rule_checker C in [
            Check_Direct_Instruction_Override,
            Check_DAN_Persona_Jailbreak,
            Check_System_Prompt_Leak,
            Check_Role_Authority_Manipulation,
            Check_Phrase_Bypass_Evasion,
            Check_Tool_Command_Manipulation
        ] do:
    10.     match ← C(P_norm)
    11.     if match is not NULL then:
    12.         matched_rules.Append(match)
    13.     end if
    14. end for

    15. if matched_rules is empty then:
    16.     return ("PASS", NULL, "NONE", 0.0)
    17. end if

    18. top_match ← Sort_By_Highest_Severity_Weight(matched_rules)[0]
    
    19. if top_match.Severity in {"CRITICAL", "HIGH"} or Length(matched_rules) >= 2 then:
    20.     return ("BLOCK", top_match.Category, top_match.Severity, top_match.Weight)
    21. else:
    22.     return ("PASS", top_match.Category, top_match.Severity, top_match.Weight)
    23. end if
```

---

## 2. Step-by-Step Technical Explanation (For Presentation & Viva)

1. **Step 1: Unicode NFKC Normalization (Lines 1–2)**:
   - **Why**: Attackers frequently use fullwidth unicode characters (e.g. `ｉｇｎｏｒｅ`) or zero-width non-printable characters (`\u200B`, `\uFEFF`) to disrupt regex token boundaries while remaining readable to LLMs.
   - **How**: NFKC decomposes compatibility characters into standard canonical equivalents, and invisible control codes are stripped out.

2. **Step 2: Homoglyph & Leetspeak Translation (Lines 3–5)**:
   - **Why**: Adversaries swap Latin characters with visually identical Cyrillic characters (e.g., Cyrillic small letter `а` [U+0430] instead of Latin `a` [U+0061]), which tricks naive regexes into missing the pattern.
   - **How**: A deterministic lookup dictionary maps all documented cross-alphabet homoglyphs back to ASCII Latin prior to regex evaluation.

3. **Step 3: Multi-Category Regular Expression Matching (Lines 7–14)**:
   - Evaluates the normalized prompt against compiled regular expressions across 6 distinct threat classes:
     - **Direct Instruction Override**: Catches commands demanding the model disregard safety rules.
     - **DAN & Persona Jailbreak**: Catches persona emulation (DAN mode, Developer mode, EvilBot).
     - **System Prompt Leak**: Catches directives seeking to extract developer system messages.
     - **Role Manipulation**: Catches unauthorized admin or root elevation claims.
     - **Phrase Bypass Evasion**: Catches hypothetical or fictional framing bypasses.
     - **Tool/Command Manipulation**: Catches shell injection (`rm -rf`) or database attacks (`DROP TABLE`).

4. **Step 4: Severity-Weighted Early Exit Arbiter (Lines 15–23)**:
   - Instead of binary pattern matching, each category carries an assigned severity (`CRITICAL`, `HIGH`, `MEDIUM`).
   - Any `CRITICAL` or `HIGH` match triggers an instant `BLOCK` in **$< 0.05$ ms**, terminating before calling heavier ML models or LLMs.

---

## 3. Ready-to-Present Slide Points for Anjith

### Slide: Layer 1 Rule Engine Architecture & Algorithm
- **Role in Two-Layer Defense**: Ultra-fast deterministic perimeter filter executing in $<0.05$ ms.
- **Novelty**: Includes pre-filtering homoglyph neutralization and invisible character stripping before regex evaluation.
- **6 Threat Taxonomies**: Direct Override, DAN Jailbreak, System Leak, Role Elevation, Phrase Bypass, Command Injection.
- **Empirical Validation**: Achieved **100% Precision** (zero false positives) on curated conversational queries and intercepted known attacks in sub-millisecond time.
- **Viva Defense Point**: *"Static rules cannot catch creative paraphrasing alone, which is why Layer 1 acts as a low-latency fast-exit filter that hands off ambiguous cases to Anusree's Layer 2 ML classifier."*
