"""Runs tests/parity.mjs (browser bot vs Python bot) when Node.js is installed."""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

from src.bot import CustomerServiceBot
from src.classifier import DATA_DIR, IntentClassifier, load_examples

ROOT = Path(__file__).resolve().parent.parent


@unittest.skipUnless(shutil.which("node"), "Node.js not installed")
class TestBrowserParity(unittest.TestCase):
    def test_export_is_up_to_date(self):
        """docs/ must be re-exported after changing the training data."""
        expected = json.loads((ROOT / "tests" / "expected_predictions.json").read_text(encoding="utf-8"))
        examples = load_examples() + load_examples(DATA_DIR / "intents_test.csv")
        self.assertEqual([e["text"] for e in expected], [t for t, _, _ in examples],
                         "Run `python export_model.py` after editing data/.")
        model = IntentClassifier().train()
        for e in expected[:50]:
            self.assertEqual(model.predict(e["text"]), (e["intent"], e["confidence"]))

    def test_browser_bot_matches_python(self):
        result = subprocess.run(["node", "tests/parity.mjs"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
