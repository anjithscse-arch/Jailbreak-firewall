"""Test Suite for Anjith's Rule Engine.

Evaluates the 6 regex rule categories against base-paper dataset samples:
- `backend/data/jailbreaktracer_benchmark.csv` (1,000 samples from IEEE Access paper)
- `backend/data/prompts.csv` (650 multi-category curated prompt firewall samples)

Records:
- Total samples evaluated
- True Positives (Hits on actual attacks)
- False Positives (Rules incorrectly blocking benign prompts)
- True Negatives (Correctly passed benign prompts)
- False Negatives (Missed attacks that bypassed static regex)
- Breakdown of hits per rule category
"""

import os
import sys
import time
import pandas as pd
from rules import evaluate_rules

# Set UTF-8 encoding for Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')



def run_rule_evaluation(benchmark_csv_path: str, dataset_name: str):
    """Runs evaluation over a CSV benchmark file and logs detailed metrics."""
    if not os.path.exists(benchmark_csv_path):
        print(f"Error: Dataset not found at {benchmark_csv_path}")
        return None

    df = pd.read_csv(benchmark_csv_path)
    print("=" * 70)
    print(f"[*] EVALUATING RULE ENGINE ON: {dataset_name}")
    print(f"[-] Path: {benchmark_csv_path}")
    print(f"[-] Total Samples: {len(df)}")
    print("=" * 70)


    # Determine ground truth column
    # In benchmark.csv: 'label' == 'JAILBREAK' vs 'BENIGN'
    # In prompts.csv: 'is_attack' == 1 / True or 'label' != 'BENIGN'
    has_is_attack = 'is_attack' in df.columns
    has_label = 'label' in df.columns

    tp = 0  # Attack correctly blocked
    fp = 0  # Benign incorrectly blocked
    tn = 0  # Benign correctly allowed
    fn = 0  # Attack missed (allowed)

    category_hits = {
        "DIRECT_INSTRUCTION_OVERRIDE": 0,
        "DAN_PERSONA_JAILBREAK": 0,
        "SYSTEM_PROMPT_LEAK": 0,
        "ROLE_MANIPULATION": 0,
        "PHRASE_BYPASS_EVASION": 0,
        "TOOL_COMMAND_MANIPULATION": 0,
    }

    start_time = time.perf_counter()

    for idx, row in df.iterrows():
        # Get text
        text = str(row.get('text', row.get('prompt', '')))
        
        # Determine ground truth
        if has_is_attack:
            is_actual_attack = bool(row['is_attack'])
        elif has_label:
            is_actual_attack = str(row['label']).strip().upper() not in ('BENIGN', '0', 'SAFE')
        else:
            is_actual_attack = False

        res = evaluate_rules(text)
        is_blocked = res['is_blocked']

        if is_blocked:
            if res['primary_reason'] in category_hits:
                category_hits[res['primary_reason']] += 1

        if is_actual_attack and is_blocked:
            tp += 1
        elif not is_actual_attack and is_blocked:
            fp += 1
        elif not is_actual_attack and not is_blocked:
            tn += 1
        else:
            fn += 1

    total_time_ms = (time.perf_counter() - start_time) * 1000
    avg_latency_ms = total_time_ms / len(df)

    total_attacks = tp + fn
    total_benign = tn + fp
    total_samples = len(df)

    accuracy = ((tp + tn) / total_samples) * 100 if total_samples > 0 else 0
    precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
    recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    fpr = (fp / total_benign) * 100 if total_benign > 0 else 0

    print(f"\n[+] PERFORMANCE METRICS:")
    print(f"  • Total Evaluated:     {total_samples}")
    print(f"  • Ground Truth:        {total_attacks} Attacks | {total_benign} Benign")
    print(f"  • True Positives (TP): {tp} (Attacks intercepted)")
    print(f"  • True Negatives (TN): {tn} (Benign queries passed)")
    print(f"  • False Positives(FP): {fp} (Benign queries false-flagged)")
    print(f"  • False Negatives(FN): {fn} (Attacks missed)")
    print(f"  --------------------------------------------------")
    print(f"  • Accuracy:            {accuracy:.2f}%")
    print(f"  • Precision:           {precision:.2f}%")
    print(f"  • Recall (Hit Rate):   {recall:.2f}%")
    print(f"  • F1-Score:            {f1:.2f}%")
    print(f"  • False Positive Rate: {fpr:.2f}%")
    print(f"  • Average Latency:     {avg_latency_ms:.4f} ms / prompt")

    print(f"\n[*] HIT COUNTS BY RULE CATEGORY:")
    for cat, count in category_hits.items():
        print(f"  - {cat:30s}: {count:4d} hits")


    return {
        "dataset": dataset_name,
        "total": total_samples,
        "attacks": total_attacks,
        "benign": total_benign,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "avg_latency_ms": avg_latency_ms,
        "category_hits": category_hits,
    }


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_dir = os.path.abspath(os.path.join(base_dir, ".."))
    
    # 1. Base paper benchmark
    benchmark_path = os.path.join(workspace_dir, "backend", "data", "jailbreaktracer_benchmark.csv")
    res1 = run_rule_evaluation(benchmark_path, "JailbreakTracer IEEE Access Benchmark (1,000 samples)")

    # 2. Curated firewall dataset
    prompts_path = os.path.join(workspace_dir, "backend", "data", "prompts.csv")
    res2 = run_rule_evaluation(prompts_path, "Curated Firewall Prompts Dataset (650 samples)")
