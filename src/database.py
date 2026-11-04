"""
SQL database layer for logging customer support tickets and operational metrics.
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any


class TicketDatabase:
    """Manages SQLite storage for customer inquiries and resolution tracking."""

    def __init__(self, db_path: str = "customer_service.db") -> None:
        self.db_path = db_path
        self._init_schema()

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    predicted_intent TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    escalated INTEGER NOT NULL DEFAULT 0,
                    response TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def log_ticket(
        self,
        customer_id: str,
        message: str,
        predicted_intent: str,
        confidence: float,
        escalated: bool,
        response: str,
    ) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                INSERT INTO support_tickets (
                    customer_id, message, predicted_intent, confidence, escalated, response, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    customer_id,
                    message,
                    predicted_intent,
                    confidence,
                    int(escalated),
                    response,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def get_summary_metrics(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) AS total_tickets,
                    AVG(confidence) AS avg_confidence,
                    SUM(escalated) AS escalated_count
                FROM support_tickets
                """
            )
            row = cursor.fetchone()
            total = row[0] or 0
            avg_conf = round(row[1], 3) if row[1] is not None else 0.0
            escalated = row[2] or 0
            return {
                "total_tickets": total,
                "avg_confidence": avg_conf,
                "automation_rate": round(1 - (escalated / total), 3) if total > 0 else 0.0,
            }

