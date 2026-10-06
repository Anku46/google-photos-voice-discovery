"""
eval/run_eval.py — Evaluation harness for Phase 3.6.

Scores the filter stage and gap classifier against the golden set (golden.jsonl).
Run this after every prompt or model change.

Usage:
    python eval/run_eval.py
"""

import json
import os
from pathlib import Path

GOLDEN_PATH = Path(__file__).parent / "golden.jsonl"


def load_golden() -> list[dict]:
    records = []
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate_filter(predictions: list[dict], golden: list[dict]) -> dict:
    """
    Score the filter stage against golden labels.

    predictions: list of {review_id, predicted_label} where label is 'relevant'|'irrelevant'
    golden:      loaded golden.jsonl records

    Returns precision, recall, f1.
    """
    gold_map = {r["review_id"]: r["label"] for r in golden}
    tp = fp = fn = tn = 0

    for pred in predictions:
        rid = pred["review_id"]
        predicted = pred["predicted_label"]
        actual = gold_map.get(rid)
        if actual is None:
            continue
        if predicted == "relevant" and actual == "relevant":
            tp += 1
        elif predicted == "relevant" and actual == "irrelevant":
            fp += 1
        elif predicted == "irrelevant" and actual == "relevant":
            fn += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "target_recall": 0.90,
        "recall_ok": recall >= 0.90,
    }


def evaluate_gap_classifier(predictions: list[dict], golden: list[dict]) -> dict:
    """
    Score the primary_gap classifier against golden labels.

    predictions: list of {review_id, predicted_primary_gap}
    Returns per-gap accuracy and a confusion dict.
    """
    gold_map = {r["review_id"]: r["primary_gap"] for r in golden if r["label"] == "relevant"}
    correct = 0
    total = 0
    confusion: dict[str, dict[str, int]] = {}

    for pred in predictions:
        rid = pred["review_id"]
        actual = gold_map.get(rid)
        if actual is None:
            continue
        predicted = pred.get("predicted_primary_gap")
        total += 1
        if predicted == actual:
            correct += 1
        confusion.setdefault(actual, {})
        confusion[actual][predicted or "None"] = confusion[actual].get(predicted or "None", 0) + 1

    accuracy = correct / total if total > 0 else 0.0
    return {
        "accuracy": round(accuracy, 3),
        "correct": correct,
        "total": total,
        "confusion_matrix": confusion,
    }


def print_filter_report(result: dict) -> None:
    print("\n=== Filter Stage Evaluation ===")
    print(f"  TP={result['tp']}  FP={result['fp']}  FN={result['fn']}  TN={result['tn']}")
    print(f"  Precision : {result['precision']}")
    print(f"  Recall    : {result['recall']}  (target >= {result['target_recall']})")
    print(f"  F1        : {result['f1']}")
    status = "✅ PASS" if result["recall_ok"] else "❌ FAIL — tune prompt or keyword list"
    print(f"  Status    : {status}")


def print_gap_report(result: dict) -> None:
    print("\n=== Gap Classifier Evaluation ===")
    print(f"  Accuracy : {result['accuracy']}  ({result['correct']}/{result['total']})")
    print("  Confusion matrix (actual → predicted):")
    for actual, preds in result["confusion_matrix"].items():
        for pred, count in preds.items():
            mark = "✅" if actual == pred else "❌"
            print(f"    {mark}  {actual!r:30s} → {pred!r} ({count})")


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    from src.pipeline.groq_client import get_groq_client
    from src.pipeline.filter import run_semantic_filter, LEXICAL_PATTERN
    from src.pipeline.extract import run_cognitive_extraction
    from src.pipeline.classify import run_journey_classification
    
    golden = load_golden()
    print(f"Loaded {len(golden)} golden records.")

    from collections import Counter
    labels = Counter(r["label"] for r in golden)
    gaps   = Counter(r["primary_gap"] for r in golden if r["label"] == "relevant")
    print(f"\nGolden label distribution: {dict(labels)}")
    print(f"Gap distribution (relevant only): {dict(gaps)}")
    print("\n--- Running Evaluation against Golden Set (this uses Groq API) ---")
    
    client = get_groq_client()
    
    filter_preds = []
    gap_preds = []
    
    for record in golden:
        rid = record["review_id"]
        text = record["review_text"]
        
        # 1. Filter Stage
        predicted_label = "irrelevant"
        if LEXICAL_PATTERN.search(text):
            try:
                res = run_semantic_filter(client, text)
                if res.classification.value == "RETRIEVAL_EXPERIENCE":
                    predicted_label = "relevant"
            except Exception as e:
                print(f"[{rid}] Filter error: {e}")
        
        filter_preds.append({
            "review_id": rid,
            "predicted_label": predicted_label
        })
        
        # 2. Gap Classification (only for ground-truth relevant items so we can measure accuracy)
        if record["label"] == "relevant":
            try:
                # We need to extract first to feed the classifier
                ext = run_cognitive_extraction(client, text)
                cls = run_journey_classification(client, ext.model_dump(), text)
                gap_preds.append({
                    "review_id": rid,
                    "predicted_primary_gap": cls.primary_gap.value
                })
            except Exception as e:
                print(f"[{rid}] Classify error: {e}")
                
    filter_report = evaluate_filter(filter_preds, golden)
    print_filter_report(filter_report)
    
    if gap_preds:
        gap_report = evaluate_gap_classifier(gap_preds, golden)
        print_gap_report(gap_report)
    else:
        print("\nNo gap predictions made.")
