import unittest

from src.evaluation.multimodal import evaluate_scenarios, scenarios


class ScenarioTests(unittest.TestCase):
    def test_expected_outputs_and_grounding(self):
        report = evaluate_scenarios()
        summary = report["summary"]
        self.assertGreaterEqual(len(scenarios()), 25)
        self.assertGreaterEqual(summary["severity_accuracy"], 0.9)
        self.assertEqual(summary["extraction_accuracy"], 1.0)
        self.assertEqual(summary["evidence_grounding_rate"], 1.0)
        self.assertEqual(summary["unsupported_claim_count"], 0)
        self.assertEqual(summary["task_completion_rate"], 1.0)
        self.assertEqual(summary["expected_failure_rejection_rate"], 1.0)
        historical = next(row for row in report["scenarios"] if row["scenario"] == "historical_fire")
        self.assertFalse(historical["severity_correct"])


if __name__ == "__main__":
    unittest.main()
