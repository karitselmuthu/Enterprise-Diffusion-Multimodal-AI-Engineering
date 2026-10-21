import unittest

from src.diffusion.baselines import PositionFrequencyBaseline
from src.diffusion.denoiser import TinyDenoiser
from src.diffusion.generator import reconstruct_iterative
from src.diffusion.masking import MASK
from src.multimodal.temporal import active_terms


class TemporalAndBaselineTests(unittest.TestCase):
    def test_temporal_order_and_recurrence(self):
        self.assertEqual(active_terms("Was critical yesterday but is resolved now."), (set(), "resolved"))
        self.assertEqual(active_terms("At 11:00 fire was resolved. At 09:00 fire was active."), (set(), "resolved"))
        self.assertEqual(active_terms("Alarm cleared yesterday. Alarm active again today."), ({"alarm"}, "active"))

    def test_paired_mask_baseline_preserves_visible_tokens(self):
        sequences = [["pump", "high"], ["valve", "low"], ["pump", "high"]]
        baseline = PositionFrequencyBaseline(sequences)
        self.assertEqual(baseline.reconstruct([MASK, "low"]), ["pump", "low"])
        model = TinyDenoiser.from_sequences(sequences)
        model.train(sequences, epochs=2)
        reconstructed = reconstruct_iterative(model, ["pump", MASK], steps=2)
        self.assertEqual(reconstructed["tokens"][0], "pump")
        self.assertNotIn(MASK, reconstructed["tokens"])


if __name__ == "__main__":
    unittest.main()
