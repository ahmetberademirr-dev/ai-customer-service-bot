"""
SQLite storage: the demo store's orders and a log of every customer message.

The ticket log is what turns the bot into an operations tool: every message is
stored with its topic, the bot's confidence, what the bot did (answered, asked
for info, asked to rephrase, handed to a human) and a priority.
"""

import csv
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ORDERS_FILE = Path(__file__).resolve().parent.parent / "data" / "orders.csv"

SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    item_tr TEXT NOT NULL,
    item_en TEXT NOT NULL,
    status TEXT NOT NULL,              -- preparing | shipped | delivered | cancelled
    carrier TEXT,
    ordered_days_ago INTEGER NOT NULL,
    eta_in_days INTEGER,               -- negative = late
    delivered_days_ago INTEGER
);

CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id TEXT NOT NULL,
    message TEXT NOT NULL,
    language TEXT NOT NULL,
    intent TEXT NOT NULL,
    confidence REAL NOT NULL,
    outcome TEXT NOT NULL,             -- answered | asked_info | clarify | escalated
    priority TEXT NOT NULL,            -- low | medium | high
    order_id TEXT,
    response TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _int_or_none(value: str) -> Optional[int]:
    return int(value) if value not in (None, "") else None


class TicketDatabase:
    """Orders + ticket log. Pass ":memory:" for a throwaway database."""

    def __init__(self, db_path: str = "customer_service.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self._seed_orders()

    def _seed_orders(self) -> None:
        if self.conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]:
            return
        with open(ORDERS_FILE, newline="", encoding="utf-8") as f:
            rows = [
                (
                    r["order_id"], r["item_tr"], r["item_en"], r["status"], r["carrier"] or None,
                    int(r["ordered_days_ago"]), _int_or_none(r["eta_in_days"]),
                    _int_or_none(r["delivered_days_ago"]),
                )
                for r in csv.DictReader(f)
            ]
        self.conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
        self.conn.commit()

    # ---- orders -----------------------------------------------------------
    def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
        return dict(row) if row else None

    def set_order_status(self, order_id: str, status: str) -> None:
        self.conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
        self.conn.commit()

    # ---- tickets ----------------------------------------------------------
    def log_ticket(self, **ticket: Any) -> int:
        ticket["created_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        columns = ", ".join(ticket)
        placeholders = ", ".join("?" for _ in ticket)
        cursor = self.conn.execute(
            f"INSERT INTO support_tickets ({columns}) VALUES ({placeholders})",
            tuple(ticket.values()),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def get_summary_metrics(self, min_confidence: float = 0.4) -> Dict[str, Any]:
        """Operational numbers a support team lead would look at."""
        total = self.conn.execute("SELECT COUNT(*) FROM support_tickets").fetchone()[0]
        outcomes = dict(self.conn.execute(
            "SELECT outcome, COUNT(*) FROM support_tickets GROUP BY outcome"
        ).fetchall())
        top_intents = dict(self.conn.execute(
            """
            SELECT intent, COUNT(*) AS n FROM support_tickets
            WHERE confidence >= ?
            GROUP BY intent ORDER BY n DESC LIMIT 5
            """, (min_confidence,)
        ).fetchall())
        high_priority = self.conn.execute(
            "SELECT COUNT(*) FROM support_tickets WHERE priority = 'high'"
        ).fetchone()[0]
        escalated = outcomes.get("escalated", 0)
        return {
            "total_messages": total,
            "outcomes": outcomes,
            "handled_without_human": round(1 - escalated / total, 3) if total else 0.0,
            "high_priority": high_priority,
            "top_intents": top_intents,
        }
