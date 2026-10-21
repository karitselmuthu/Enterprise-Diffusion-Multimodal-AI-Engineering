import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.review.store import ReviewStore


class ReviewStoreTests(unittest.TestCase):
    def test_persistent_decision_and_evidence_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "reviews.sqlite3"
            first = ReviewStore(path)
            record = first.create({"severity": "high", "evidence": [{"source": "report_text", "content": "Smoke"}]})
            self.assertEqual(record["status"], "pending")
            with self.assertRaises(ValueError):
                first.decide(record["id"], status="approved", reviewer="analyst-1", summary="Smoke reported",
                             recommendation="Inspect", cited_sources=["missing_source"])
            decision = first.decide(record["id"], status="approved", reviewer="analyst-1", summary="Smoke reported",
                                    recommendation="Inspect the area", cited_sources=["report_text"])
            self.assertEqual(decision["status"], "approved")
            self.assertEqual(ReviewStore(path).get(record["id"])["decision"]["reviewer"], "analyst-1")
            with self.assertRaises(RuntimeError):
                first.decide(record["id"], status="rejected", reviewer="analyst-2", summary="No evidence",
                             recommendation="", cited_sources=[])

    def test_simultaneous_decisions_allow_one_winner(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ReviewStore(Path(folder) / "reviews.sqlite3")
            record = store.create({"evidence": [{"source": "report_text", "content": "Alarm"}]})
            def decide(index):
                try:
                    store.decide(record["id"], status="approved", reviewer=f"analyst-{index}",
                                 summary="Alarm reported", recommendation="Inspect", cited_sources=["report_text"])
                    return "approved"
                except RuntimeError:
                    return "conflict"
            with ThreadPoolExecutor(max_workers=2) as executor:
                outcomes = list(executor.map(decide, range(2)))
            self.assertCountEqual(outcomes, ["approved", "conflict"])
            self.assertEqual(store.get(record["id"])["status"], "approved")


if __name__ == "__main__":
    unittest.main()
