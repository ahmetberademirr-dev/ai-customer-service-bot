"""
Core response engine combining intent classification, SQL logging, and automated replies.
"""

from typing import Dict, Any
from .classifier import IntentClassifier
from .database import TicketDatabase


RESPONSE_TEMPLATES: Dict[str, str] = {
    "order_status": (
        "Thank you for reaching out! Please share your order number and we will "
        "immediately retrieve the latest tracking update for your shipment."
    ),
    "refund_request": (
        "We have received your refund inquiry. Eligible items can be returned within "
        "14 days of delivery. Please reply with your order ID to initiate the process."
    ),
    "billing_inquiry": (
        "Our billing automation has logged your request. A copy of your invoice and "
        "payment verification details will be sent to your registered email shortly."
    ),
    "technical_support": (
        "We are sorry you are experiencing technical difficulties. Could you please "
        "share your device type and a brief description of the error code?"
    ),
}


class CustomerServiceBot:
    """Automated customer support bot with intent routing and SQL telemetry."""

    def __init__(self, confidence_threshold: float = 0.45, db_path: str = "customer_service.db") -> None:
        self.classifier = IntentClassifier()
        self.classifier.train()
        self.db = TicketDatabase(db_path=db_path)
        self.confidence_threshold = confidence_threshold

    def handle_message(self, customer_id: str, message: str) -> Dict[str, Any]:
        intent, confidence = self.classifier.predict(message)
        escalated = confidence < self.confidence_threshold

        if escalated:
            reply = (
                "Thank you for contacting support. Your inquiry has been forwarded "
                "to a customer service specialist who will assist you shortly."
            )
        else:
            reply = RESPONSE_TEMPLATES.get(
                intent,
                "Thank you for your message. Our team will get back to you soon.",
            )

        ticket_id = self.db.log_ticket(
            customer_id=customer_id,
            message=message,
            predicted_intent=intent,
            confidence=confidence,
            escalated=escalated,
            response=reply,
        )

        return {
            "ticket_id": ticket_id,
            "intent": intent,
            "confidence": confidence,
            "escalated": escalated,
            "reply": reply,
        }

