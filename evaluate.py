"""
Measure how well the bot understands customers and write reports/evaluation.md.

Two measurements:
1. Held-out test set (data/intents_test.csv): 120 questions the model never
   sees during training, written with typos, missing Turkish characters and
   short phrasing.
2. 5-fold cross-validation on the training set: a second, stricter check,
   because one hand-written test set can be easier than real traffic.

For a support team the important split is not only "accuracy" but:
* answered   - the bot was confident enough to act,
* wrong      - the bot acted but on the wrong topic (the costly mistake),
* rephrase   - the bot asked the customer to rephrase (cheap mistake).
"""

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

from sklearn.model_selection import StratifiedKFold

from src.bot import CustomerServiceBot
from src.classifier import DATA_DIR, IntentClassifier, LanguageDetector, load_examples

THRESHOLD = CustomerServiceBot.__init__.__defaults__[1]
REPORT = Path(__file__).resolve().parent / "reports" / "evaluation.md"
METRICS = Path(__file__).resolve().parent / "docs" / "metrics.json"


def score(predictions: List[Tuple[str, float]], gold: List[str]) -> Dict[str, float]:
    n = len(gold)
    answered = [(p, g) for (p, c), g in zip(predictions, gold) if c >= THRESHOLD]
    correct_answered = sum(p == g for p, g in answered)
    return {
        "n": n,
        "accuracy": sum(p == g for (p, _), g in zip(predictions, gold)) / n,
        "answered": len(answered) / n,
        "correct_when_answered": correct_answered / len(answered) if answered else 0.0,
        "wrong": (len(answered) - correct_answered) / n,
        "rephrase": 1 - len(answered) / n,
    }


def main() -> None:
    train = load_examples()
    test = load_examples(DATA_DIR / "intents_test.csv")

    model = IntentClassifier().train(train)
    test_pred = [model.predict(t) for t, _, _ in test]
    test_gold = [g for _, g, _ in test]
    test_score = score(test_pred, test_gold)

    cv_pred, cv_gold = [], []
    labels = [e[1] for e in train]
    for train_idx, val_idx in StratifiedKFold(5, shuffle=True, random_state=0).split(train, labels):
        fold = IntentClassifier().train([train[i] for i in train_idx])
        for i in val_idx:
            cv_pred.append(fold.predict(train[i][0]))
            cv_gold.append(train[i][1])
    cv_score = score(cv_pred, cv_gold)

    lang = LanguageDetector().train(train)
    lang_acc = sum(lang.predict(t)[0] == l for t, _, l in test) / len(test)

    per_intent = defaultdict(lambda: [0, 0])
    for (p, _), g in zip(test_pred, test_gold):
        per_intent[g][0] += p == g
        per_intent[g][1] += 1
    mistakes = [(t, g, p, c) for (t, g, _), (p, c) in zip(test, test_pred) if p != g]

    pct = lambda x: f"{x * 100:.1f}%"
    lines = [
        "# Evaluation report",
        "",
        f"Training examples: {len(train)} ({dict(Counter(e[2] for e in train))}) · "
        f"Topics: {len(set(labels))} · Confidence threshold: {THRESHOLD}",
        "",
        "| | Held-out test set | Cross-validation |",
        "|---|---|---|",
        f"| Questions | {test_score['n']} | {cv_score['n']} |",
        f"| Topic accuracy | {pct(test_score['accuracy'])} | {pct(cv_score['accuracy'])} |",
        f"| Bot answers on its own | {pct(test_score['answered'])} | {pct(cv_score['answered'])} |",
        f"| Correct when it answers | {pct(test_score['correct_when_answered'])} | {pct(cv_score['correct_when_answered'])} |",
        f"| Answers on the wrong topic | {pct(test_score['wrong'])} | {pct(cv_score['wrong'])} |",
        f"| Asks the customer to rephrase | {pct(test_score['rephrase'])} | {pct(cv_score['rephrase'])} |",
        "",
        f"Language detection accuracy (test set): {pct(lang_acc)}",
        "",
        "The cross-validation column is the more conservative estimate.",
        "",
        "## Accuracy by topic (test set)",
        "",
        "| Topic | Correct |",
        "|---|---|",
        *[f"| {k} | {c}/{n} |" for k, (c, n) in sorted(per_intent.items())],
        "",
        "## Mistakes on the test set",
        "",
        "| Message | Expected | Predicted | Confidence | What the customer sees |",
        "|---|---|---|---|---|",
        *[
            f"| {t} | {g} | {p} | {c:.2f} | "
            f"{'asked to rephrase' if c < THRESHOLD else 'wrong answer'} |"
            for t, g, p, c in mistakes
        ],
        "",
        "Regenerate with `python evaluate.py`.",
        "",
    ]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    # Same numbers for the demo page, so the website never shows hand-typed figures.
    METRICS.parent.mkdir(exist_ok=True)
    METRICS.write_text(json.dumps({
        "train_examples": len(train),
        "topics": len(set(labels)),
        "threshold": THRESHOLD,
        "test": {k: round(v, 4) for k, v in test_score.items()},
        "cross_validation": {k: round(v, 4) for k, v in cv_score.items()},
        "language_accuracy": round(lang_acc, 4),
    }, indent=1), encoding="utf-8")
    print("\n".join(lines[:15]))
    print(f"\nFull report: {REPORT}")


if __name__ == "__main__":
    main()
