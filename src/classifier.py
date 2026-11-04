"""
Intent classification module using Scikit-Learn.
Classifies incoming customer inquiries into predefined support categories.
"""

from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


TRAINING_DATA: List[Tuple[str, str]] = [
    ("Where is my order? It has been two weeks.", "order_status"),
    ("Can I track my package delivery?", "order_status"),
    ("When will my shipment arrive?", "order_status"),
    ("I want to request a refund for my last purchase.", "refund_request"),
    ("How do I return a damaged item and get my money back?", "refund_request"),
    ("Cancel my order and issue a full refund please.", "refund_request"),
    ("I was charged twice on my credit card invoice.", "billing_inquiry"),
    ("Can you send me the invoice for last month's subscription?", "billing_inquiry"),
    ("My payment failed but the amount was deducted.", "billing_inquiry"),
    ("The application crashes whenever I try to log in.", "technical_support"),
    ("I cannot reset my account password.", "technical_support"),
    ("Integration webhook is returning a 500 error.", "technical_support"),
]


class IntentClassifier:
    """Scikit-Learn pipeline for customer query intent detection."""

    def __init__(self) -> None:
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), stop_words="english")),
            ("clf", LogisticRegression(random_state=42)),
        ])
        self._is_trained = False

    def train(self, samples: List[Tuple[str, str]] = TRAINING_DATA) -> None:
        texts = [item[0] for item in samples]
        labels = [item[1] for item in samples]
        self.pipeline.fit(texts, labels)
        self._is_trained = True

    def predict(self, message: str) -> Tuple[str, float]:
        if not self._is_trained:
            self.train()
        probabilities = self.pipeline.predict_proba([message])[0]
        best_idx = probabilities.argmax()
        intent = self.pipeline.classes_[best_idx]
        confidence = float(probabilities[best_idx])
        return intent, round(confidence, 3)

