"""Iterative confidence-based unmasking and an autoregressive bigram baseline."""

from __future__ import annotations

from collections import Counter, defaultdict
import random

from .denoiser import TinyDenoiser
from .masking import MASK
from .scheduler import positions_this_step


def generate(model: TinyDenoiser, *, length: int, steps: int = 4, prefix: list[str] | None = None, seed: int = 0) -> dict:
    if length < 1 or steps < 1:
        raise ValueError("length and steps must be positive")
    prefix = list(prefix or [])
    if len(prefix) > length or any(token not in model.vocabulary for token in prefix):
        raise ValueError("prefix is too long or contains an unknown token")
    tokens = prefix + [MASK] * (length - len(prefix))
    trace = [list(tokens)]
    rng = random.Random(seed)
    for step in range(steps):
        masked_positions = [i for i, token in enumerate(tokens) if token == MASK]
        if not masked_positions:
            break
        candidates = []
        for position in masked_positions:
            probabilities = model.probabilities(tokens, position)
            # Random tie breaking makes equal-score locations reproducible by seed.
            sampled = rng.choices(list(probabilities), weights=list(probabilities.values()))[0]
            candidates.append((probabilities[sampled], rng.random(), position, sampled))
        count = positions_this_step(len(masked_positions), steps - step)
        for _, _, position, token in sorted(candidates, reverse=True)[:count]:
            tokens[position] = token
        trace.append(list(tokens))
    return {"tokens": tokens, "text": " ".join(tokens), "steps_used": len(trace) - 1, "trace": trace}


class BigramBaseline:
    def __init__(self, sequences: list[list[str]]):
        self.vocabulary = sorted({token for sequence in sequences for token in sequence})
        if not self.vocabulary:
            raise ValueError("at least one nonempty sequence is required")
        self.counts: dict[str, Counter[str]] = defaultdict(Counter)
        for sequence in sequences:
            previous = "<START>"
            for token in sequence:
                self.counts[previous][token] += 1
                previous = token

    def probabilities(self, previous: str) -> dict[str, float]:
        counts = self.counts[previous]
        total = sum(counts.values()) + len(self.vocabulary)
        return {token: (counts[token] + 1) / total for token in self.vocabulary}

    def generate(self, length: int, *, prefix: list[str] | None = None, seed: int = 0) -> dict:
        if length < 1:
            raise ValueError("length must be positive")
        tokens = list(prefix or [])
        if len(tokens) > length or any(token not in self.vocabulary for token in tokens):
            raise ValueError("invalid prefix")
        rng = random.Random(seed)
        while len(tokens) < length:
            probabilities = self.probabilities(tokens[-1] if tokens else "<START>")
            tokens.append(rng.choices(list(probabilities), weights=list(probabilities.values()))[0])
        return {"tokens": tokens, "text": " ".join(tokens), "steps_used": len(tokens) - len(prefix or [])}
