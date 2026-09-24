# Anusree — Second Interim Presentation: ML Classifier Pseudocode & Technical Explanation

**Student Name**: Anusree  
**Module**: Layer 2 Machine Learning Threat Classifier  
**Project Title**: AI Prompt Injection and Jailbreak Detection Firewall  
**Base Paper**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation* (IEEE Access, Vol. 13, 2025)  

---

## 1. Formal Pseudocode (Algorithm 2)

```text
Algorithm 2: Baseline Supervised ML Threat Classification Pipeline
Input  : Benchmark dataset D = {(x_i, y_i)}_{i=1}^N, Unseen prompt P_test, Threshold θ = 0.50
Output : Model Pipeline M, Predicted Class y_hat, Attack Probability P_attack, Verdict

Phase A: Model Training & Evaluation
    1.  Confirm Dataset Class Balance:
            N_benign ← Count(y == 0), N_attack ← Count(y == 1)
            Assert(|N_benign - N_attack| / N < 0.05)  // Validates 50:50 balance
    2.  (D_train, D_test) ← Stratified_Train_Test_Split(D, test_ratio = 0.20, random_state = 42)
    3.  Configure TF-IDF Vectorizer:
            V ← TfidfVectorizer(
                    ngram_range = (1, 2),        // Word unigrams and bigrams
                    max_features = 10000,
                    sublinear_tf = True,         // 1 + log(tf) scaling
                    strip_accents = 'unicode'
                )
    4.  Configure Classifier:
            C ← LogisticRegression(
                    C = 1.0, 
                    solver = 'liblinear', 
                    class_weight = 'balanced'
                )
    5.  Pipeline M ← Sequential_Pipeline(V, C)
    6.  Fit Model: M.Train(D_train.X, D_train.y)
    7.  Evaluate on Held-Out Split D_test:
            y_pred ← M.Predict(D_test.X)
            Accuracy, Precision, Recall, F1 ← Compute_Metrics(D_test.y, y_pred)
    8.  Serialize Model Artifact: Save_Joblib(M, "baseline_classifier.joblib")

Phase B: Real-Time Inference on Prompt P_test
    9.  Features x_vec ← V.Transform([P_test])
    10. P_probs ← C.Predict_Probability(x_vec)
    11. P_attack ← P_probs[Class = 1]   // Adversarial attack probability
    12. if P_attack >= θ then:
    13.     return ("BLOCK", y_hat = 1, P_attack, "ML_PROMPT_INJECTION_DETECTED")
    14. else:
    15.     return ("PASS",  y_hat = 0, P_attack, "BENIGN")
    16. end if
```

---

## 2. Step-by-Step Technical Explanation (For Presentation & Viva)

1. **Step 1: Dataset Verification & Stratification (Lines 1–2)**:
   - **Why**: Model evaluation is only trustworthy if data leakage is prevented and class balance is validated.
   - **How**: Used the IEEE Access *JailbreakTracer* corpus (1,000 samples). Confirmed exactly 500 Benign (50%) and 500 Jailbreak (50%) prompts. Applied stratified splitting ($800$ training, $200$ held-out test).

2. **Step 2: Dual N-Gram Feature Extraction via TF-IDF (Line 3)**:
   - **Why**: Adversarial prompts rely heavily on specific phrase combinations (e.g. `ignore previous`, `developer mode`, `without guidelines`) rather than isolated words.
   - **How**: Extracts word unigrams and bigrams ($1, 2$) capped at 10,000 most informative features with sublinear term-frequency dampening ($1 + \log(\text{tf})$).

3. **Step 3: Calibrated Logistic Regression Classifier (Lines 4–6)**:
   - **Why**: Before applying deep transformer networks (e.g. RoBERTa), an academic capstone requires establishing a rigorous statistical baseline. Logistic Regression provides well-calibrated posterior probabilities $P(y=1|x) \in [0, 1]$ with sub-millisecond execution time.
   - **How**: Uses liblinear optimization with L2 regularization and balanced class weighting.

4. **Step 4: Empirical Benchmark Results (Lines 7–8)**:
   - Achieved **89.00% Accuracy**, **89.80% Precision**, **88.00% Recall**, and **88.89% F1-Score** on the held-out test split in **0.476 ms** inference time.

5. **Step 5: Transition to Next Phase (Phase 2 Roadmap)**:
   - The baseline is established. The next development iteration integrates **JailBreakRoBERTa** (base paper target: 97.25% accuracy) and **LIME XAI** (`LimeTextExplainer`) for token-level visual feature attribution.

---

## 3. Ready-to-Present Slide Points for Anusree

### Slide: Layer 2 ML Threat Classifier & Empirical Baseline
- **Dataset**: IEEE Access *JailbreakTracer* Benchmark (1,000 balanced samples: 50% Benign, 50% Jailbreak).
- **Experimental Methodology**: Stratified 80/20 train/test split (800 train / 200 test), random seed 42.
- **Baseline Pipeline**: TF-IDF (Unigram + Bigram feature extraction, 10k vocabulary) + Calibrated Logistic Regression.
- **Key Metrics Achieved**:
  - **Accuracy**: **89.00%**
  - **Precision**: **89.80%** (Low false-positive rate)
  - **Recall**: **88.00%** (Broad adversarial coverage)
  - **Latency**: **0.476 ms** per sample.
- **Roadmap Note**: *"Baseline established; fine-tuned transformer (RoBERTa) and LIME token interpretability planned for the next project phase."*
