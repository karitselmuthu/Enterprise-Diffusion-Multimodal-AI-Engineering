import tempfile
import unittest
from pathlib import Path

from scripts.human_ground_truth import export, score


class HumanGroundTruthTests(unittest.TestCase):
    def test_blank_sheets_are_not_scored(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            export(target)
            self.assertTrue((target / "source_packets.jsonl").exists())
            with self.assertRaises(ValueError):
                score(target / "reviewer_a.csv", target / "reviewer_b.csv")


if __name__ == "__main__":
    unittest.main()
