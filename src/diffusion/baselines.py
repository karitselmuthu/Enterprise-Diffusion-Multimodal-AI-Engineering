"""Simple position-frequency masked-token baseline."""

from collections import Counter, defaultdict

from .masking import MASK


class PositionFrequencyBaseline:
    def __init__(self, sequences: list[list[str]]):
        self.by_position: dict[int, Counter[str]] = defaultdict(Counter)
        self.global_counts: Counter[str] = Counter()
        for sequence in sequences:
            for position, token in enumerate(sequence):
                self.by_position[position][token] += 1
                self.global_counts[token] += 1
        if not self.global_counts:
            raise ValueError("training sequences must contain tokens")

    def reconstruct(self, masked: list[str]) -> list[str]:
        return [token if token != MASK else (self.by_position[position] or self.global_counts).most_common(1)[0][0]
                for position, token in enumerate(masked)]
