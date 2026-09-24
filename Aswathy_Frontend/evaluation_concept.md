# Aswathy — Evaluation Module Visualization Concept & Specification

**Author**: Aswathy  
**Role**: Frontend UI/UX & Data Visualization  
**Project**: AI Prompt Injection and Jailbreak Detection Firewall  
**Date**: September 18, 2026  

---

## 1. Objective & Purpose

The **Evaluation Module** is designed to provide security administrators, academic evaluators, and system auditors with clear, empirical visibility into firewall performance. It translates raw benchmark test numbers from **Anjith's Rule Engine** and **Anusree's ML Classifier** into real-time interactive charts, latency distributions, and comparative matrices.

---

## 2. Core Dashboard Metrics & KPI Cards

The top row presents high-level summary cards updating dynamically as benchmarks run:

```
+-------------------+  +-------------------+  +-------------------+  +-------------------+
|  System Accuracy  |  | Detection Rate    |  | False Positive    |  | Processing Latency|
|      89.00%       |  |      88.00%       |  |       0.00%       |  |     0.048 ms      |
|  (ML Baseline)    |  | (Recall on Attacks)| | (Curated Benign)  |  | (Layer 1 Fast-Path|
+-------------------+  +-------------------+  +-------------------+  +-------------------+
```

---

## 3. Detailed Visualization Components

### 3.1 Component A: Multi-Layer Performance Radar / Bar Chart
- **Purpose**: Compare detection effectiveness across Layer 1 (Rules), Layer 2 (ML Baseline), and the Hybrid Two-Layer Firewall.
- **Chart Type**: Grouped Bar Chart (Metrics: Accuracy, Precision, Recall, F1-Score).
- **Benchmark Data**:
  * **Layer 1 (Rule-Only)**: Precision $100\%$, Recall $16.7\%$, Latency $<0.05$ ms.
  * **Layer 2 (ML Baseline)**: Precision $89.8\%$, Recall $88.0\%$, Latency $0.48$ ms.
  * **Hybrid Combined Firewall (Projected)**: Precision $94.2\%$, Recall $91.5\%$, Latency $12.4$ ms.

```mermaid
gantt
    title Latency Comparison (Logarithmic Scale ms)
    dateFormat X
    axisFormat %s
    section Layer 1 Rule Engine : 0, 1
    section Layer 2 ML Classifier : 0, 5
    section Two-Layer Hybrid : 0, 12
    section Cloud LLM-as-a-Judge : 0, 2500
```

---

### 3.2 Component B: Interactive Confusion Matrix Heatmap
- **Purpose**: Allow reviewers to inspect True Positives, False Positives, True Negatives, and False Negatives visually.
- **Color Scale**: Green (correct classifications) to Deep Red (critical false negatives).
- **Interactive Behavior**: Clicking on the **False Negative (FN)** cell filters the audit table below to show the exact prompts that bypassed detection, facilitating error analysis.

| Actual \ Predicted | Predicted Benign (0) | Predicted Attack (1) |
| :--- | :---: | :---: |
| **Actual Benign (100)** | `90 (TN)` <br> *(Safe passed)* | `10 (FP)` <br> *(False alarm)* |
| **Actual Attack (100)** | `12 (FN)` <br> *(Missed)* | `88 (TP)` <br> *(Blocked)* |

---

### 3.3 Component C: Threat Category Breakdown Chart
- **Purpose**: Horizontal percentage stacked bars illustrating which threat vectors are most frequently blocked by rules vs. ML.
- **Categories Covered**:
  1. `DIRECT_INSTRUCTION_OVERRIDE` (85% caught via Layer 1)
  2. `DAN_PERSONA_JAILBREAK` (88% caught via Layer 1 & 2)
  3. `SYSTEM_PROMPT_LEAK` (72% caught)
  4. `ROLE_MANIPULATION` (65% caught)
  5. `PHRASE_BYPASS_EVASION` (78% caught via Layer 2 ML)
  6. `TOOL_COMMAND_MANIPULATION` (90% caught via Layer 1)

---

### 3.4 Component D: Explainable AI (LIME) Feature Attribution Visualizer (Phase 2 Preview)
- **Concept**: For any prompt blocked by Layer 2, display token importance bars directly beneath the prompt words:
  * Tokens highlighted in **Red** indicate positive attack contributions (e.g. `DAN` $+0.38$, `ignore` $+0.34$, `bypass` $+0.21$).
  * Tokens highlighted in **Green** indicate benign context weights.
- **UI Element**: Inline pill badges hovering over each token displaying the exact local linear regression coefficient.

---

## 4. Frontend Technology Stack & Implementation Strategy

- **Core Library**: Vanilla HTML5, CSS3 Grid/Flexbox, and JavaScript (zero build step needed for immediate browser execution).
- **Visualization Engine (Future Phase)**: `Chart.js` (lightweight 60KB canvas library) or `ApexCharts` for smooth dark-mode animations.
- **State Management**: Reactive fetch polling every 5 seconds against Asna's `/logs` endpoint to update metrics live without requiring page reloads.

---

## 5. Summary of Presentation Deliverables

1. **Working Dashboard (`index.html`)**: Features live prompt inspection, allow/block badges, audit table, and evaluation cards.
2. **Slide Visuals Deck (`demo_slides/slides.html`)**: 3 high-resolution presentation-ready slide cards for project viva / presentation screenshots.
3. **Evaluation Concept Spec (`evaluation_concept.md`)**: Complete architectural design and metrics specification.
