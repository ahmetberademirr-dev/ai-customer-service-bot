"""
Intent and language classification.

Two small scikit-learn models are trained on data/intents_train.csv:

* IntentClassifier: which of the 10 topics a message is about.
  Word n-grams catch phrases ("cancel my order"), character n-grams catch
  Turkish suffixes and typos ("siparisim", "siparişimi", "sipariş").
* LanguageDetector: Turkish or English, so the bot answers in the
  customer's language.
"""

import csv
import re
import warnings
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TRAIN_FILE = DATA_DIR / "intents_train.csv"

# Customers often type Turkish without Turkish characters ("siparisim nerde").
# Folding both spellings to the same form lets one example cover both.
_TR_FOLD = str.maketrans("çğıöşüâîûÇĞİIÖŞÜÂÎÛ", "cgiosuaiucgiiosuaiu")


def normalize(text: str) -> str:
    """Lowercase, fold Turkish characters, replace numbers, drop punctuation."""
    text = text.translate(_TR_FOLD).lower()
    text = re.sub(r"[0-9]+", " 0 ", text)
    text = re.sub(r"[^a-z0 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _fit(pipeline: Pipeline, texts: List[str], labels: List[str]) -> None:
    # numpy 2 with Apple's Accelerate library prints spurious "overflow in matmul"
    # warnings during training; the fitted model is unaffected.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning, module="sklearn")
        pipeline.fit(texts, labels)


def load_examples(path: Path = TRAIN_FILE) -> List[Tuple[str, str, str]]:
    """Return (text, intent, lang) rows from a CSV file."""
    with open(path, newline="", encoding="utf-8") as f:
        return [(row["text"], row["intent"], row["lang"]) for row in csv.DictReader(f)]


class IntentClassifier:
    """TF-IDF (words + characters) followed by logistic regression."""

    def __init__(self, c: float = 10.0) -> None:
        features = FeatureUnion([
            ("words", TfidfVectorizer(
                preprocessor=normalize, analyzer="word",
                token_pattern=r"[a-z0]+", ngram_range=(1, 2), sublinear_tf=True,
            )),
            ("chars", TfidfVectorizer(
                preprocessor=normalize, analyzer="char_wb",
                ngram_range=(2, 5), sublinear_tf=True,
            )),
        ])
        self.pipeline = Pipeline([
            ("features", features),
            ("model", LogisticRegression(C=c, max_iter=5000)),
        ])
        self._is_trained = False

    def train(self, examples: List[Tuple[str, str, str]] = None) -> "IntentClassifier":
        examples = examples if examples is not None else load_examples()
        _fit(self.pipeline, [e[0] for e in examples], [e[1] for e in examples])
        self._is_trained = True
        return self

    def predict(self, message: str) -> Tuple[str, float]:
        """Return (intent, confidence between 0 and 1)."""
        if not self._is_trained:
            self.train()
        probabilities = self.pipeline.predict_proba([message])[0]
        best = int(probabilities.argmax())
        return str(self.pipeline.classes_[best]), round(float(probabilities[best]), 3)

    @property
    def intents(self) -> List[str]:
        return [str(c) for c in self.pipeline.classes_]


class LanguageDetector:
    """Turkish vs English, trained on the same examples."""

    def __init__(self) -> None:
        self.pipeline = Pipeline([
            ("chars", TfidfVectorizer(lowercase=True, analyzer="char_wb", ngram_range=(1, 3))),
            ("model", LogisticRegression(C=10.0, max_iter=5000)),
        ])
        self._is_trained = False

    def train(self, examples: List[Tuple[str, str, str]] = None) -> "LanguageDetector":
        examples = examples if examples is not None else load_examples()
        _fit(self.pipeline, [e[0] for e in examples], [e[2] for e in examples])
        self._is_trained = True
        return self

    def predict(self, message: str) -> Tuple[str, float]:
        if not self._is_trained:
            self.train()
        probabilities = self.pipeline.predict_proba([message])[0]
        best = int(probabilities.argmax())
        return str(self.pipeline.classes_[best]), round(float(probabilities[best]), 3)
