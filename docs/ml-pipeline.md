# Machine Learning Pipeline & Explainability

Layer 2 of the firewall utilizes a supervised multiclass text classification pipeline optimized for high-throughput CPU inference without requiring a dedicated GPU.

---

## 1. Feature Engineering Architecture

The ML pipeline employs a **FeatureUnion** combining word-level semantic n-grams and character-level boundary n-grams:

```
[Raw Preprocessed Prompt]
            │
            ├─────────────────────────────────────────────┐
            ▼                                             ▼
[Word TfidfVectorizer]                       [Char TfidfVectorizer]
  - analyzer="word"                            - analyzer="char_wb"
  - ngram_range=(1, 2)                         - ngram_range=(3, 5)
  - sublinear_tf=True                          - sublinear_tf=True
  - max_features=12,000                        - max_features=15,000
            │                                             │
            └──────────────────────┬──────────────────────┘
                                   ▼
                       [Concatenated Feature Vector]
                       (~27,000 sparse dimensions)
                                   │
                                   ▼
                [Calibrated Multiclass Logistic Regression]
                       (class_weight="balanced")
                                   │
                                   ▼
                    [Probability Distribution over 10 Classes]
```

### Why Character-Level N-Grams?
Adversaries frequently alter prompts through spacing (`i g n o r e`), leetspeak (`1gn0r3`), or minor character swaps. The `char_wb` analyzer extracts n-grams within word boundaries, capturing structural substrings even when tokens are obfuscated.

---

## 2. Model Training & Validation Split

- **Dataset Size**: 650 curated synthetic prompts.
- **Threat Categories**: 10 balanced classes (Benign + 9 Attack Vectors).
- **Split Strategy**: Stratified 70% Training, 15% Validation, 15% Test.
- **No Data Leakage**: Word and character feature vocabularies are fitted strictly on training observations and evaluated on unseen test data.

---

## 3. Explainability Mathematics

Explainability is calculated via **Feature Attribution Alignment**:

For an incoming prompt transformed into sparse representation $X$ with non-zero feature indices $j \in \mathcal{J}$, and predicted class index $k$:

$$
\text{Contribution}(j) = X_j \cdot W_{k, j}
$$

Where:
- $X_j$: Normalized TF-IDF term frequency value for feature $j$.
- $W_{k, j}$: Learned regression coefficient weight for class $k$ on feature $j$.

Top positive features indicate terms pushing the prompt toward the threat classification, while negative features indicate stabilizing benign context.

---

## 5. Academic Research Dataset Integration: JailbreakTracer (IEEE Access 2025)

The firewall incorporates the complete corpus from the research paper:
> **Title**: *JailbreakTracer: Explainable Detection of Jailbreaking Prompts in LLMs Using Synthetic Data Generation*  
> **Authors**: Md. Faiyaz Abdullah Sayeedi, Maaz Bin Hossain, Md. Kamrul Hassan, et al.  
> **Venue**: IEEE Access (Vol. 13, 2025)  
> **DOI**: 10.1109/ACCESS.2025.3579996  
> **Repository**: [https://github.com/faiyazabdullah/JailbreakTracer](https://github.com/faiyazabdullah/JailbreakTracer)  
> **Kaggle**: [https://www.kaggle.com/datasets/faiyazabdullah/jailbreaktracer-corpus](https://www.kaggle.com/datasets/faiyazabdullah/jailbreaktracer-corpus)

### Corpus Files Downloaded (`backend/data/jailbreaktracer/`):
1. **Forbidden Question Reasoning Dataset**: `forbidden_questions/formatted_dataset.csv` (323.2 MB, **107,250 samples** uniformly distributed across 13 forbidden scenarios: Illegal Activity, Hate Speech, Malware, Physical Harm, Economic Harm, Fraud, Pornography, Political Lobbying, Privacy, Legal, Financial, Health, Government).
2. **Balanced Toxic Prompt Classification Dataset**: `merged_dataset/Final Dataset/merged(in).csv` (28.8 MB, **32,058 samples**: 16,029 benign + 16,029 jailbreaks).
3. **In-the-Wild Attack Prompts**: `jailbreak_prompts_2023_05_07.csv` (1.32 MB) & `jailbreak_prompts_2023_12_25.csv` (3.60 MB).
4. **Regular Benign Prompts**: `regular_prompts_2023_05_07.csv` (6.21 MB) & `regular_prompts_2023_12_25.csv` (23.18 MB).
5. **Synthetic Adversarial Prompts**: `synthetic_data/synthetic data/augmented_dataset.csv` (31.3 MB) & `synthetic_prompts.txt` (2.4 MB).
6. **Firewall Catalog Benchmark**: `backend/data/jailbreaktracer_benchmark.csv` (**1,000 samples**, 500 in-the-wild jailbreaks + 500 benign, registered in SQLite database catalog `DatasetRecord` ID=2).

### Augmented Model Performance (`tfidf-logreg-v2.jailbreaktracer`):
- **Test Accuracy**: **87.6%**
- **Macro Precision**: **88.8%**
- **Macro Recall**: **82.2%**
- **Macro F1-Score**: **0.843**
- **Inference Latency**: **< 15 ms** on standard CPU.
