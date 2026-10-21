import math
import random
import unittest

from src.diffusion.denoiser import TinyDenoiser
from src.diffusion.generator import generate
from src.diffusion.masking import MASK, mask_tokens, reconstruct
from src.diffusion.noise import alpha_bars, linear_beta_schedule, sample_xt
from src.evaluation.runner import split_incidents


class DiffusionTests(unittest.TestCase):
    def test_gaussian_marginal_endpoints(self):
        self.assertEqual(sample_xt([2.0], 1.0, random.Random(1)), [2.0])
        bars = alpha_bars(linear_beta_schedule(10))
        self.assertTrue(all(left > right for left, right in zip(bars, bars[1:])))

    def test_mask_and_reconstruct(self):
        original = ["a", "b", "c"]
        masked, positions = mask_tokens(original, 1.0, random.Random(1))
        self.assertEqual(masked, [MASK] * 3)
        self.assertEqual(reconstruct(masked, {i: original[i] for i in positions}), original)

    def test_training_and_generation(self):
        train, _ = split_incidents()
        model = TinyDenoiser.from_sequences(train)
        losses = model.train(train, epochs=8, seed=7)
        self.assertLess(losses[-1], losses[0])
        output = generate(model, length=8, steps=3, prefix=["the"], seed=7)
        self.assertEqual(len(output["tokens"]), 8)
        self.assertNotIn(MASK, output["tokens"])
        self.assertEqual(output["steps_used"], 3)
        self.assertEqual(output["tokens"][0], "the")

    def test_probabilities_normalize(self):
        model = TinyDenoiser(["a", "b"])
        scores = model.probabilities([MASK], 0)
        self.assertTrue(math.isclose(sum(scores.values()), 1.0))


if __name__ == "__main__":
    unittest.main()
