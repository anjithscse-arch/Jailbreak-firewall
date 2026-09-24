"""Baseline Machine Learning Classifier for Layer 2 Firewall Defense.

Developer / Researcher: Anusree
Module: Layer 2 ML Classifier
Base Paper: JailbreakTracer (IEEE Access 2025)

Workflow:
1. Load and inspect the base-paper dataset (sample count, class balance).
2. Stratified train/test split (80% train, 20% test).
3. Baseline Model: TF-IDF n-gram vectorization + Calibrated Logistic Regression.
4. Run training pass and evaluate on held-out test split.
5. Record Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
6. Export serialized model pipeline for live firewall inference.
"""

import os
import sys
import time
import joblib
import pandas as pd
import numpy as np

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def load_and_inspect_dataset(data_path: str):
    """Loads dataset and verifies sample count and class balance."""
    print("=" * 70)
    print("[*] STEP 1: DATASET INSPECTION & CLASS BALANCE VERIFICATION")
    print("=" * 70)
    print(f"[-] Loading dataset from: {data_path}")
    
    df = pd.read_csv(data_path)
    print(f"[-] Total Sample Count: {len(df):,}")
    print(f"[-] Dataset Columns:    {list(df.columns)}")

    # Standardize labels into binary 0 (Benign) and 1 (Jailbreak / Attack)
    if 'label' in df.columns and 'BENIGN' in df['label'].values:
        df['binary_label'] = df['label'].apply(lambda x: 0 if str(x).strip().upper() == 'BENIGN' else 1)
        raw_dist = df['label'].value_counts()
    elif 'is_attack' in df.columns:
        df['binary_label'] = df['is_attack'].astype(int)
        raw_dist = df['category'].value_counts() if 'category' in df.columns else df['binary_label'].value_counts()
    else:
        raise ValueError("Could not find suitable label column in dataset")

    text_col = 'text' if 'text' in df.columns else 'prompt'
    df['clean_text'] = df[text_col].fillna('').astype(str)

    benign_count = (df['binary_label'] == 0).sum()
    attack_count = (df['binary_label'] == 1).sum()
    total = len(df)

    print("\n[-] Class Distribution:")
    print(f"  • Benign (Class 0):   {benign_count:5d} ({benign_count/total*100:5.1f}%)")
    print(f"  • Attack/JB (Class 1): {attack_count:5d} ({attack_count/total*100:5.1f}%)")
    
    if abs(benign_count - attack_count) < 50:
        print("[+] Class Balance Status: WELL BALANCED (~50:50 distribution confirmed)")
    else:
        print("[-] Class Balance Status: Imbalanced / Asymmetric distribution")

    return df


def train_and_evaluate_baseline(df: pd.DataFrame, model_output_path: str):
    """Performs train/test split, fits TF-IDF + Logistic Regression, and logs metrics."""
    print("\n" + "=" * 70)
    print("[*] STEP 2: TRAIN / TEST SPLIT (80% Train, 20% Held-out Test)")
    print("=" * 70)

    X = df['clean_text'].values
    y = df['binary_label'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print(f"[-] Training Samples:   {len(X_train):,}")
    print(f"[-] Testing Samples:    {len(X_test):,}")

    print("\n" + "=" * 70)
    print("[*] STEP 3: BASELINE MODEL PIPELINE SETUP")
    print("=" * 70)
    print("[-] Feature Extractor: TF-IDF Vectorizer (ngram_range=(1, 2), max_features=10,000, sublinear_tf=True)")
    print("[-] Classifier:        Logistic Regression (C=1.0, solver='liblinear', class_weight='balanced')")

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=10000,
            sublinear_tf=True,
            strip_accents='unicode',
            lowercase=True
        )),
        ('clf', LogisticRegression(
            C=1.0,
            solver='liblinear',
            class_weight='balanced',
            random_state=42
        ))
    ])

    print("\n" + "=" * 70)
    print("[*] STEP 4: TRAINING BASELINE MODEL")
    print("=" * 70)
    t0 = time.perf_counter()
    pipeline.fit(X_train, y_train)
    train_duration = time.perf_counter() - t0
    print(f"[+] Model training completed successfully in {train_duration:.3f} seconds!")

    print("\n" + "=" * 70)
    print("[*] STEP 5: EVALUATION ON HELD-OUT TEST SPLIT")
    print("=" * 70)
    t0 = time.perf_counter()
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    inference_duration_ms = (time.perf_counter() - t0) * 1000
    avg_per_sample_ms = inference_duration_ms / len(X_test)

    acc = accuracy_score(y_test, y_pred) * 100
    prec = precision_score(y_test, y_pred) * 100
    rec = recall_score(y_test, y_pred) * 100
    f1 = f1_score(y_test, y_pred) * 100
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n[+] PERFORMANCE SUMMARY:")
    print(f"  • Accuracy:           {acc:6.2f}%")
    print(f"  • Precision:          {prec:6.2f}%")
    print(f"  • Recall:             {rec:6.2f}%")
    print(f"  • F1-Score:           {f1:6.2f}%")
    print(f"  • Avg Inference Time: {avg_per_sample_ms:.4f} ms / sample")

    print("\n[+] CONFUSION MATRIX:")
    print(f"               Predicted Benign (0)   Predicted Attack (1)")
    print(f"  Actual Benign:       {cm[0, 0]:5d} (TN)              {cm[0, 1]:5d} (FP)")
    print(f"  Actual Attack:       {cm[1, 0]:5d} (FN)              {cm[1, 1]:5d} (TP)")

    print("\n[+] DETAILED CLASSIFICATION REPORT:")
    print(classification_report(y_test, y_pred, target_names=['BENIGN', 'ATTACK/JAILBREAK']))

    # Save model artifact
    joblib.dump(pipeline, model_output_path)
    print(f"[+] Serialized model saved to: {model_output_path}")

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "confusion_matrix": cm.tolist(),
        "train_time_sec": train_duration,
        "latency_ms": avg_per_sample_ms
    }


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(base_dir, ".."))
    
    # 1. Inspect and train on the IEEE Access JailbreakTracer benchmark dataset
    benchmark_file = os.path.join(workspace_dir, "backend", "data", "jailbreaktracer_benchmark.csv")
    model_save_path = os.path.join(base_dir, "baseline_classifier.joblib")

    df_benchmark = load_and_inspect_dataset(benchmark_file)
    metrics = train_and_evaluate_baseline(df_benchmark, model_save_path)
