# Anusree — Machine Learning Baseline Classifier Report

**Developer / Researcher**: Anusree  
**Module**: Layer 2 Machine Learning Threat Classifier  
**Project**: AI Prompt Injection and Jailbreak Detection Firewall  
**Base Paper**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation* (IEEE Access, Vol. 13, 2025)  
**Date**: September 18, 2026  

---

## 1. Dataset Inspection & Verification

We loaded and inspected the base-paper IEEE Access benchmark corpus (`backend/data/jailbreaktracer_benchmark.csv`):

- **Total Sample Count**: 1,000 samples
- **Columns**: `text`, `prompt`, `label`, `source`
- **Class Balance Analysis**:
  * **Benign Prompts (`label == BENIGN`)**: 500 samples (50.0%)
  * **Jailbreak / Attack Prompts (`label == JAILBREAK`)**: 500 samples (50.0%)
- **Validation Outcome**: Verified that the dataset is perfectly balanced ($50:50$ binary split) without class skew, eliminating the need for synthetic oversampling (SMOTE) at this baseline stage.

---

## 2. Experimental Setup: Train/Test Split & Feature Extraction

- **Train/Test Split**:
  * **Strategy**: Stratified random split (preserving exact 50:50 class proportions in both subsets)
  * **Training Split (80%)**: 800 samples (400 Benign, 400 Jailbreak)
  * **Held-out Test Split (20%)**: 200 samples (100 Benign, 100 Jailbreak)
  * **Random State**: Seed 42 for complete reproducibility

- **Feature Pipeline (TF-IDF Vectorization)**:
  * **N-gram Range**: $(1, 2)$ — Unigrams and Bigrams
  * **Vocabulary Size**: 10,000 max features
  * **Sublinear Term Frequency Scaling**: Enabled (`sublinear_tf=True`) to dampen the effect of highly frequent tokens
  * **Normalization**: Unicode accent stripping, lowercase normalization

- **Classification Algorithm**:
  * **Model**: Calibrated Multiclass Logistic Regression (`solver='liblinear'`, `class_weight='balanced'`, $C=1.0$)
  * **Rationale**: Serves as a mathematically sound, interpretable, and ultra-fast baseline before evaluating heavier deep transformer architectures.

---

## 3. Empirical Training & Test Results

The baseline training pass executed in **0.362 seconds** on CPU. Held-out test evaluation yielded the following metrics:

| Evaluation Metric | Baseline Score (TF-IDF + Logistic Regression) |
| :--- | :---: |
| **Accuracy** | **89.00%** |
| **Precision** | **89.80%** |
| **Recall (Detection Rate)** | **88.00%** |
| **F1-Score** | **88.89%** |
| **Average Inference Latency** | **0.476 ms / sample** |
| **Model Size on Disk** | **~245 KB** (`baseline_classifier.joblib`) |

### Confusion Matrix on 200 Held-Out Samples:
```
                       Predicted BENIGN (0)   Predicted ATTACK (1)
  Actual BENIGN (100):         90 (TN)                10 (FP)
  Actual ATTACK (100):         12 (FN)                88 (TP)
```

### Key Analytical Observations:
1. **High Baseline Precision (89.8%)**: Only 10 benign prompts out of 100 were falsely flagged, demonstrating good discriminatory power even without deep contextual embeddings.
2. **Strong Recall (88.0%)**: Successfully detected 88 out of 100 adversarial jailbreak prompts that bypassed keyword and static pattern checks.
3. **Sub-millisecond Latency**: Inference executes in **0.476 ms**, which is $1000\times$ faster than calling an LLM-as-a-judge API (typically 2,000–5,000 ms).

---

## 4. Phase Conclusion & Future Roadmap

> **Status Milestone**:  
> **"Baseline established, transformer upgrade planned next phase"**

### Next Steps Planned:
1. **Transformer Fine-Tuning**: Fine-tune domain-specialized encoders (such as `roberta-base` or `deberta-v3-small`) to advance from $89\%$ accuracy toward the base paper's benchmark of **$97.25\%$** (JailBreakRoBERTa).
2. **LIME Integration**: Couple the classifier output with `LimeTextExplainer` to produce token-level attribution explanations for flagged queries.
3. **Hybrid Ensemble**: Feed prediction probabilities ($P_{\text{ml}}$) into the Decision Arbiter alongside Anjith's Rule Engine scores.
