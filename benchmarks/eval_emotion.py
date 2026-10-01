"""Scores multi_tool_agent.core_companion.analyze_emotion on labeled data.

Usage:
    python benchmarks/eval_emotion.py            # report
    python benchmarks/eval_emotion.py --gate     # exit 1 if crisis recall < 100%
    python benchmarks/eval_emotion.py --external # also score a dair-ai/emotion sample (needs `pip install datasets`)

Offline, free, deterministic. Writes benchmarks/results/emotion.json.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from multi_tool_agent import core_companion  # noqa: E402

DATA = Path(__file__).parent / "datasets"
RESULTS = Path(__file__).parent / "results"
LABELS = ["calm", "stressed", "anxious", "happy", "sad", "angry", "neutral"]


def load(name: str) -> list[dict]:
    with open(DATA / name, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def predict(text: str) -> dict:
    return core_companion.analyze_emotion(text)


def prf(gold: list[str], pred: list[str]) -> dict:
    """Per-class precision/recall/F1 plus accuracy and macro-F1."""
    per_class = {}
    for label in LABELS:
        tp = sum(1 for g, p in zip(gold, pred) if g == label and p == label)
        fp = sum(1 for g, p in zip(gold, pred) if g != label and p == label)
        fn = sum(1 for g, p in zip(gold, pred) if g == label and p != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "precision": round(precision, 3), "recall": round(recall, 3),
            "f1": round(f1, 3), "support": tp + fn,
        }
    present = [c for c in LABELS if per_class[c]["support"] > 0]
    macro_f1 = sum(per_class[c]["f1"] for c in present) / len(present)
    accuracy = sum(g == p for g, p in zip(gold, pred)) / len(gold)
    return {
        "n": len(gold), "accuracy": round(accuracy, 3),
        "macro_f1": round(macro_f1, 3), "per_class": per_class,
    }


def confusion(gold: list[str], pred: list[str]) -> dict:
    matrix: dict[str, Counter] = defaultdict(Counter)
    for g, p in zip(gold, pred):
        matrix[g][p] += 1
    return {g: dict(c) for g, c in matrix.items()}


def evaluate() -> dict:
    labeled = load("emotion_labeled.jsonl")
    crisis = load("crisis.jsonl")
    benign = load("benign.jsonl")

    preds = [predict(r["text"]) for r in labeled]
    gold = [r["emotion"] for r in labeled]
    pred = [p["emotion"] for p in preds]

    by_tag = {}
    for tag in sorted({r["tag"] for r in labeled}):
        idx = [i for i, r in enumerate(labeled) if r["tag"] == tag]
        by_tag[tag] = round(sum(gold[i] == pred[i] for i in idx) / len(idx), 3)

    mixed_idx = [i for i, r in enumerate(labeled) if r["tag"] == "mixed"]
    mixed_primary = sum(gold[i] == pred[i] for i in mixed_idx) / len(mixed_idx)
    mixed_secondary = sum(
        labeled[i]["secondary"] == preds[i].get("secondary_emotion") for i in mixed_idx
    ) / len(mixed_idx)

    crisis_preds = [predict(r["text"]) for r in crisis]
    missed = [r["text"] for r, p in zip(crisis, crisis_preds) if not p.get("crisis")]
    recall = 1 - len(missed) / len(crisis)

    benign_preds = [predict(r["text"]) for r in benign]
    benign_fp = [r["text"] for r, p in zip(benign, benign_preds) if p.get("crisis")]
    non_crisis_texts = labeled + benign
    non_crisis_fp = sum(1 for p in preds if p.get("crisis")) + len(benign_fp)

    benign_gold = [r["emotion"] for r in benign]
    benign_pred = [p["emotion"] for p in benign_preds]

    return {
        "emotion": prf(gold, pred),
        "by_tag_accuracy": by_tag,
        "mixed": {
            "n": len(mixed_idx),
            "primary_accuracy": round(mixed_primary, 3),
            "secondary_accuracy": round(mixed_secondary, 3),
        },
        "confusion": confusion(gold, pred),
        "crisis": {
            "n": len(crisis), "recall": round(recall, 3), "missed": missed,
        },
        "crisis_false_positives": {
            "n_non_crisis": len(non_crisis_texts),
            "false_positive_rate": round(non_crisis_fp / len(non_crisis_texts), 3),
            "hard_negative_n": len(benign),
            "hard_negative_fp": len(benign_fp),
            "hard_negative_fp_texts": benign_fp,
        },
        "hard_negative_emotion_accuracy": round(
            sum(g == p for g, p in zip(benign_gold, benign_pred)) / len(benign), 3
        ),
    }


def evaluate_external(sample: int = 500) -> dict:
    """Scores on dair-ai/emotion (test split), keeping labels we also have."""
    from datasets import load_dataset  # type: ignore

    ds = load_dataset("dair-ai/emotion", split="test")
    names = ds.features["label"].names
    mapping = {"joy": "happy", "sadness": "sad", "anger": "angry", "fear": "anxious"}
    gold, pred = [], []
    for row in ds:
        label = mapping.get(names[row["label"]])
        if label is None:
            continue
        gold.append(label)
        pred.append(predict(row["text"])["emotion"])
        if len(gold) >= sample:
            break
    stats = prf(gold, pred)
    # No-signal predictions (neutral) count as misses; report how often that is.
    stats["predicted_neutral_rate"] = round(sum(p == "neutral" for p in pred) / len(pred), 3)
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true", help="exit 1 if crisis recall < 100%%")
    parser.add_argument("--external", action="store_true")
    args = parser.parse_args()

    result = {"with_negation": evaluate()}

    # Ablation: disable negation handling and re-score.
    original = core_companion._is_negated
    core_companion._is_negated = lambda text, kw: False  # type: ignore[assignment]
    try:
        ablated = evaluate()
    finally:
        core_companion._is_negated = original
    result["without_negation"] = {
        "emotion_accuracy": ablated["emotion"]["accuracy"],
        "macro_f1": ablated["emotion"]["macro_f1"],
        "negation_subset_accuracy": ablated["by_tag_accuracy"].get("negation"),
    }

    if args.external:
        try:
            result["external_dair_ai_emotion"] = evaluate_external()
        except ImportError:
            print("skip --external: pip install datasets", file=sys.stderr)

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "emotion.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    e = result["with_negation"]
    print(f"emotion  n={e['emotion']['n']}  accuracy={e['emotion']['accuracy']:.1%}  macro-F1={e['emotion']['macro_f1']:.3f}")
    print(f"by tag   {e['by_tag_accuracy']}")
    print(f"mixed    primary={e['mixed']['primary_accuracy']:.0%}  secondary={e['mixed']['secondary_accuracy']:.0%}  (n={e['mixed']['n']})")
    print(f"negation ablation: accuracy {result['without_negation']['emotion_accuracy']:.1%} without handling "
          f"(negation subset {result['without_negation']['negation_subset_accuracy']:.0%} vs {e['by_tag_accuracy'].get('negation', 0):.0%} with)")
    print(f"crisis   recall={e['crisis']['recall']:.1%} (n={e['crisis']['n']})  missed={e['crisis']['missed']}")
    fp = e["crisis_false_positives"]
    print(f"crisis   false-positive rate={fp['false_positive_rate']:.1%} over {fp['n_non_crisis']} non-crisis; "
          f"hard negatives {fp['hard_negative_fp']}/{fp['hard_negative_n']}: {fp['hard_negative_fp_texts']}")
    if "external_dair_ai_emotion" in result:
        x = result["external_dair_ai_emotion"]
        print(f"external n={x['n']} accuracy={x['accuracy']:.1%} macro-F1={x['macro_f1']:.3f} neutral-rate={x['predicted_neutral_rate']:.0%}")

    if args.gate and e["crisis"]["recall"] < 1.0:
        print("GATE FAILED: crisis recall below 100%", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
