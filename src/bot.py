"""
Conversation engine: understand the message, act on the order, reply, log.

Flow for every message:
1. Detect language (Turkish / English) and topic (intent) with confidence.
2. If the bot is not confident enough, ask the customer to rephrase.
   Two misunderstandings in a row go to a human instead of looping.
3. For order topics, find the order number (in this message or earlier in the
   conversation), look the order up and apply the store's rules
   (e.g. shipped orders can't be cancelled, returns are open for 14 days).
4. Set a priority (money problems, late orders and angry wording go first).
5. Log everything for the operations summary.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .classifier import IntentClassifier, LanguageDetector, normalize
from .database import TicketDatabase

REPLIES_FILE = Path(__file__).resolve().parent.parent / "data" / "replies.json"

ORDER_INTENTS = {"order_status", "cancel_order", "return_refund", "change_address"}
RETURN_WINDOW_DAYS = 14
MAX_MESSAGE_LENGTH = 500
LANGUAGE_CONFIDENCE = 0.75

# Topics the bot can close on its own, and ones that always go to a person.
SIMPLE_INTENTS = {
    "greeting": ("greeting", "answered"),
    "goodbye": ("goodbye", "answered"),
    "account_help": ("account_help", "answered"),
    "out_of_scope": ("out_of_scope", "answered"),
    "payment_issue": ("payment_issue", "escalated"),   # money is never automated
    "human_agent": ("human_agent", "escalated"),
}

URGENT_WORDS = {
    "acil", "rezalet", "berbat", "dolandir", "dolandirici", "sikayet", "avukat",
    "mahkeme", "hakem", "urgent", "asap", "terrible", "scam", "fraud", "lawyer",
    "unacceptable", "worst", "furious",
}

_ORDER_ID = re.compile(r"(?<!\d)(\d{6})(?!\d)")


def extract_order_id(message: str) -> Optional[str]:
    match = _ORDER_ID.search(message)
    return match.group(1) if match else None


# Words that can surround a bare order number without changing its meaning.
FILLER_WORDS = {
    "siparis", "siparisim", "siparisimin", "no", "numara", "numaram", "numarasi",
    "numarali", "order", "number", "nr", "id", "my", "is", "it", "s", "bu", "iste",
}


def is_mostly_order_number(message: str) -> bool:
    """True for messages like '100231', '#100231' or 'sipariş no 100231'."""
    words = [w for w in normalize(message).split() if w != "0"]
    return all(w in FILLER_WORDS for w in words)


class CustomerServiceBot:
    def __init__(self, db_path: str = "customer_service.db", confidence_threshold: float = 0.4) -> None:
        self.intents = IntentClassifier().train()
        self.language = LanguageDetector().train()
        self.db = TicketDatabase(db_path)
        self.confidence_threshold = confidence_threshold
        with open(REPLIES_FILE, encoding="utf-8") as f:
            self.replies: Dict[str, Dict[str, str]] = json.load(f)
        # Short-term memory per customer: language, the question we asked,
        # the last order number they mentioned, and misunderstandings in a row.
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def reset(self) -> None:
        """Fresh orders and no conversation memory (used by tests and demos)."""
        self.db = TicketDatabase(":memory:")
        self.sessions.clear()

    # ------------------------------------------------------------------
    def handle_message(self, customer_id: str, message: str, default_lang: Optional[str] = None) -> Dict[str, Any]:
        """default_lang: language to use when a first message is too short to tell (e.g. '#100231')."""
        message = message[:MAX_MESSAGE_LENGTH]
        session = self.sessions.setdefault(
            customer_id, {"lang": None, "pending": None, "last_order": None, "misses": 0}
        )

        order_id = extract_order_id(message)
        if order_id:
            session["last_order"] = order_id
        intent, confidence = self.intents.predict(message)

        # A bare order number is the answer to our previous question.
        if order_id and (is_mostly_order_number(message) or confidence < self.confidence_threshold):
            intent, confidence = session["pending"] or "order_status", 1.0

        # Short replies ("ok") and gibberish say nothing reliable about language:
        # keep the conversation's language, or the page's language for a first message.
        lang, lang_confidence = self.language.predict(message)
        unclear = lang_confidence < LANGUAGE_CONFIDENCE or confidence < self.confidence_threshold
        if unclear and (session["lang"] or default_lang):
            lang = session["lang"] or default_lang
        session["lang"] = lang

        if confidence < self.confidence_threshold:
            session["misses"] += 1
            if session["misses"] >= 2:
                session["misses"] = 0
                key, outcome, fields = "clarify_escalate", "escalated", {}
            else:
                key, outcome, fields = "clarify", "clarify", {}
        else:
            session["misses"] = 0
            key, outcome, fields = self._act(intent, session, lang)

        priority = self._priority(message, intent, key, outcome)
        reply = self.replies[key][lang].format(**fields)

        ticket_id = self.db.log_ticket(
            customer_id=customer_id, message=message, language=lang, intent=intent,
            confidence=confidence, outcome=outcome, priority=priority,
            order_id=fields.get("order_id"), response=reply,
        )
        return {
            "ticket_id": ticket_id, "message": message, "intent": intent, "confidence": confidence,
            "language": lang, "outcome": outcome, "priority": priority,
            "escalated": outcome == "escalated", "reply": reply,
        }

    # ------------------------------------------------------------------
    def _act(self, intent: str, session: Dict[str, Any], lang: str) -> Tuple[str, str, Dict[str, Any]]:
        if intent not in ORDER_INTENTS:
            session["pending"] = None
            key, outcome = SIMPLE_INTENTS[intent]
            return key, outcome, {}

        order_id = session["last_order"]
        if not order_id:
            session["pending"] = intent
            return "ask_order_id", "asked_info", {}

        order = self.db.get_order(order_id)
        if not order:
            session["pending"], session["last_order"] = intent, None
            return "order_not_found", "asked_info", {"order_id": order_id}

        session["pending"] = None
        fields = {
            "order_id": order_id,
            "item": order[f"item_{lang}"],
            "carrier": order["carrier"],
            "eta": max(order["eta_in_days"] or 1, 1),
            "days": order["delivered_days_ago"],
        }
        handler = getattr(self, f"_{intent}")
        key, outcome = handler(order, fields)
        return key, outcome, fields

    # Store rules for each order topic --------------------------------
    def _order_status(self, order: Dict[str, Any], fields: Dict[str, Any]) -> Tuple[str, str]:
        status = order["status"]
        if status == "preparing":
            return "status_preparing", "answered"
        if status == "shipped":
            if order["eta_in_days"] < 0:
                fields["days"] = -order["eta_in_days"]
                return "status_delayed", "escalated"
            return "status_shipped", "answered"
        if status == "delivered":
            return "status_delivered", "answered"
        return "status_cancelled", "answered"

    def _cancel_order(self, order: Dict[str, Any], fields: Dict[str, Any]) -> Tuple[str, str]:
        status = order["status"]
        if status == "preparing":
            self.db.set_order_status(order["order_id"], "cancelled")
            return "cancel_ok", "answered"
        if status == "shipped":
            return "cancel_shipped", "answered"
        if status == "delivered":
            return "cancel_delivered", "answered"
        return "cancel_already", "answered"

    def _return_refund(self, order: Dict[str, Any], fields: Dict[str, Any]) -> Tuple[str, str]:
        status = order["status"]
        if status == "delivered":
            if order["delivered_days_ago"] <= RETURN_WINDOW_DAYS:
                fields["code"] = f"RET-{order['order_id']}"
                return "return_ok", "answered"
            return "return_expired", "escalated"
        if status == "cancelled":
            return "status_cancelled", "answered"
        return "return_not_delivered", "answered"

    def _change_address(self, order: Dict[str, Any], fields: Dict[str, Any]) -> Tuple[str, str]:
        status = order["status"]
        if status == "preparing":
            return "address_ok", "answered"
        if status == "shipped":
            return "address_too_late", "escalated"
        if status == "delivered":
            return "status_delivered", "answered"
        return "address_cancelled", "answered"

    # ------------------------------------------------------------------
    @staticmethod
    def _priority(message: str, intent: str, key: str, outcome: str) -> str:
        words = set(normalize(message).split())
        if intent == "payment_issue" or key == "status_delayed" or words & URGENT_WORDS:
            return "high"
        if outcome == "escalated":
            return "medium"
        return "low"
