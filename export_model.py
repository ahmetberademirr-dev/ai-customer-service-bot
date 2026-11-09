"""
Export the trained Python models and store rules for the browser demo.

    python export_model.py

Writes:
* docs/model.json  - vocabularies, IDF weights and logistic-regression weights,
                     so docs/bot.js can make exactly the same predictions.
* docs/data.json   - replies, demo orders, store rules and a sample of customer
                     messages for the dashboard simulation.
* tests/expected_predictions.json - Python's predictions, used by
                     tests/parity.mjs to prove the browser gives the same answers.

Python is the single source of truth: change data/ or src/, re-run this script.
"""

import csv
import json
import random
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

from src import bot as rules
from src.bot import CustomerServiceBot
from src.classifier import DATA_DIR, IntentClassifier, LanguageDetector, _TR_FOLD, load_examples

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
DEMO_ORDERS = ["100231", "100245", "100262", "100278", "100290", "100301"]


def rounded(values, digits: int = 6):
    return [float(f"{v:.{digits}g}") for v in values]


def export_vectorizer(vec: TfidfVectorizer) -> dict:
    vocab = sorted(vec.vocabulary_, key=vec.vocabulary_.get)
    return {
        "analyzer": vec.analyzer,
        "ngram_range": list(vec.ngram_range),
        "sublinear_tf": vec.sublinear_tf,
        "vocab": vocab,
        "idf": rounded(vec.idf_),
    }


def export_linear(model) -> dict:
    return {
        "classes": [str(c) for c in model.classes_],
        "coef": [rounded(row) for row in model.coef_],
        "intercept": rounded(model.intercept_),
    }


def main() -> None:
    train = load_examples()
    test = load_examples(DATA_DIR / "intents_test.csv")
    intent_model = IntentClassifier().train(train)
    language_model = LanguageDetector().train(train)

    features = dict(intent_model.pipeline.named_steps["features"].transformer_list)
    model = {
        "intent": {
            "vectorizers": [export_vectorizer(features["words"]), export_vectorizer(features["chars"])],
            **export_linear(intent_model.pipeline.named_steps["model"]),
        },
        "language": {
            "vectorizers": [export_vectorizer(language_model.pipeline.named_steps["chars"])],
            **export_linear(language_model.pipeline.named_steps["model"]),
        },
    }

    with open(DATA_DIR / "orders.csv", newline="", encoding="utf-8") as f:
        orders = []
        for r in csv.DictReader(f):
            orders.append({
                k: (int(v) if k.endswith(("_ago", "_days")) and v != "" else (v or None))
                for k, v in r.items()
            })

    # Dashboard simulation: the held-out test messages, with a demo order
    # number attached to order questions (fixed seed = same numbers every time).
    rng = random.Random(7)
    simulation = []
    for text, intent, lang in test:
        if intent in rules.ORDER_INTENTS and not rules.extract_order_id(text):
            text = f"{text} {rng.choice(DEMO_ORDERS)}"
        simulation.append({"text": text, "lang": lang})

    data = {
        "rules": {
            "threshold": CustomerServiceBot.__init__.__defaults__[1],
            "language_confidence": rules.LANGUAGE_CONFIDENCE,
            "max_message_length": rules.MAX_MESSAGE_LENGTH,
            "return_window_days": rules.RETURN_WINDOW_DAYS,
            "order_intents": sorted(rules.ORDER_INTENTS),
            "simple_intents": {k: list(v) for k, v in rules.SIMPLE_INTENTS.items()},
            "urgent_words": sorted(rules.URGENT_WORDS),
            "filler_words": sorted(rules.FILLER_WORDS),
            "tr_fold": {chr(k): chr(v) for k, v in _TR_FOLD.items()},
        },
        "replies": json.loads((DATA_DIR / "replies.json").read_text(encoding="utf-8")),
        "orders": orders,
        "simulation": simulation,
    }

    expected = []
    for text, _, _ in train + test:
        intent, conf = intent_model.predict(text)
        lang, lang_conf = language_model.predict(text)
        expected.append({"text": text, "intent": intent, "confidence": conf,
                         "language": lang, "language_confidence": lang_conf})

    DOCS.mkdir(exist_ok=True)
    compact = {"ensure_ascii": False, "separators": (",", ":")}
    (DOCS / "model.json").write_text(json.dumps(model, **compact), encoding="utf-8")
    (DOCS / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "tests" / "expected_predictions.json").write_text(
        json.dumps(expected, ensure_ascii=False, indent=1), encoding="utf-8")

    for name in ("model.json", "data.json"):
        print(f"docs/{name}: {(DOCS / name).stat().st_size / 1024:.0f} KB")
    print(f"tests/expected_predictions.json: {len(expected)} predictions")


if __name__ == "__main__":
    main()
