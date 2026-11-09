"""
Scenario tests for the Python bot.

The conversations live in tests/scenarios.json so that the browser version
(docs/bot.js) is checked against exactly the same expectations
(see tests/parity.mjs).

Run with:  python -m unittest discover tests
"""

import json
import unittest
from pathlib import Path

from src.bot import CustomerServiceBot

SCENARIOS = json.loads((Path(__file__).parent / "scenarios.json").read_text(encoding="utf-8"))
BOT = None


def setUpModule():
    global BOT
    BOT = CustomerServiceBot(db_path=":memory:")


def check_turn(test: unittest.TestCase, result: dict, expect: dict) -> None:
    for field in ("intent", "outcome", "priority", "language"):
        if field in expect:
            test.assertEqual(result[field], expect[field], f"{field} for: {result['message'][:60]}")
    for text in expect.get("reply_contains", []):
        test.assertIn(text, result["reply"])
    if "message_length" in expect:
        test.assertEqual(len(result["message"]), expect["message_length"])


class TestScenarios(unittest.TestCase):
    def test_all_scenarios(self):
        for scenario in SCENARIOS:
            with self.subTest(scenario=scenario["name"]):
                BOT.reset()
                for turn in scenario["turns"]:
                    message = turn.get("say") or turn["say_repeat"][0] * turn["say_repeat"][1]
                    check_turn(self, BOT.handle_message("TEST", message, turn.get("default_lang")), turn["expect"])


class TestDatabase(unittest.TestCase):
    def setUp(self):
        BOT.reset()

    def test_cancel_updates_the_order_record(self):
        BOT.handle_message("A", "Siparişimi iptal etmek istiyorum 100245")
        self.assertEqual(BOT.db.get_order("100245")["status"], "cancelled")

    def test_summary_numbers(self):
        BOT.handle_message("A", "Hello")
        BOT.handle_message("A", "I was charged twice")
        metrics = BOT.db.get_summary_metrics()
        self.assertEqual(metrics["total_messages"], 2)
        self.assertEqual(metrics["handled_without_human"], 0.5)
        self.assertEqual(metrics["high_priority"], 1)


if __name__ == "__main__":
    unittest.main()
