import unittest

from src.evaluation.multimodal import evaluate_scenarios


class ScenarioTests(unittest.TestCase):
    def test_expected_outputs_and_grounding(self):
        summary = evaluate_scenarios()["summary"]
        self.assertEqual(summary["severity_accuracy"], 1.0)
        self.assertEqual(summary["extraction_accuracy"], 1.0)
        self.assertEqual(summary["evidence_grounding_rate"], 1.0)
        self.assertEqual(summary["unsupported_claim_count"], 0)
        self.assertEqual(summary["task_completion_rate"], 1.0)
        self.assertEqual(summary["expected_failure_rejection_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
