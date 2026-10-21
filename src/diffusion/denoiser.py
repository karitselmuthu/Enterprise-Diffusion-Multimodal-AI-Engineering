"""Tiny trainable log-linear masked-token denoiser.

This intentionally uses only the Python standard library. It is a teaching
model, not a transformer or a state-of-the-art language model.
"""

from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path
import random

from .masking import MASK, mask_tokens


class TinyDenoiser:
    def __init__(self, vocabulary: list[str], weights: dict[str, dict[str, float]] | None = None):
        self.vocabulary = sorted(set(vocabulary) - {MASK})
        if not self.vocabulary:
            raise ValueError("vocabulary must contain at least one token")
        self.weights = {token: dict((weights or {}).get(token, {})) for token in self.vocabulary}

    @classmethod
    def from_sequences(cls, sequences: list[list[str]]) -> "TinyDenoiser":
        return cls(sorted({token for sequence in sequences for token in sequence}))

    @staticmethod
    def features(tokens: list[str], position: int) -> dict[str, float]:
        if tokens[position] != MASK:
            raise ValueError("the predicted position must be masked")
        features = {"bias": 1.0, f"position:{position}": 1.0, f"length:{len(tokens)}": 1.0}
        for i in range(position - 1, -1, -1):
            if tokens[i] != MASK:
                features[f"left:{tokens[i]}"] = 1.0
                break
        for i in range(position + 1, len(tokens)):
            if tokens[i] != MASK:
                features[f"right:{tokens[i]}"] = 1.0
                break
        visible = [token for token in tokens if token != MASK]
        if visible:
            counts = Counter(visible)
            for token, count in counts.items():
                features[f"bag:{token}"] = count / len(visible)
        return features

    def probabilities(self, tokens: list[str], position: int) -> dict[str, float]:
        features = self.features(tokens, position)
        scores = {token: sum(self.weights[token].get(feature, 0.0) * value for feature, value in features.items()) for token in self.vocabulary}
        maximum = max(scores.values())
        exponentials = {token: math.exp(score - maximum) for token, score in scores.items()}
        normalizer = sum(exponentials.values())
        return {token: value / normalizer for token, value in exponentials.items()}

    def train(self, sequences: list[list[str]], *, epochs: int = 20, learning_rate: float = 0.25, seed: int = 0) -> list[float]:
        if epochs < 1 or learning_rate <= 0:
            raise ValueError("epochs and learning_rate must be positive")
        rng = random.Random(seed)
        losses = []
        for _ in range(epochs):
            order = list(sequences)
            rng.shuffle(order)
            loss, examples = 0.0, 0
            for sequence in order:
                if not sequence or any(token not in self.weights for token in sequence):
                    raise ValueError("training sequence is empty or contains out-of-vocabulary tokens")
                masked, positions = mask_tokens(sequence, rng.uniform(0.15, 0.75), rng, ensure_one=True)
                for position in positions:
                    probabilities = self.probabilities(masked, position)
                    target = sequence[position]
                    loss -= math.log(max(probabilities[target], 1e-12))
                    examples += 1
                    features = self.features(masked, position)
                    for token in self.vocabulary:
                        gradient = (1.0 if token == target else 0.0) - probabilities[token]
                        for feature, value in features.items():
                            self.weights[token][feature] = self.weights[token].get(feature, 0.0) + learning_rate * gradient * value
            losses.append(loss / examples if examples else 0.0)
        return losses

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"vocabulary": self.vocabulary, "weights": self.weights}, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "TinyDenoiser":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data["vocabulary"], data["weights"])
