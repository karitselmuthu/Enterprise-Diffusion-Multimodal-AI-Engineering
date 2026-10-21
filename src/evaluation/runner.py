"""Deterministic Lecture 8 benchmark with held-out synthetic combinations."""

from __future__ import annotations

import random

from src.diffusion.denoiser import TinyDenoiser
from src.diffusion.generator import BigramBaseline, generate
from src.diffusion.masking import mask_tokens
from .metrics import accuracy, cross_entropy, profile


def synthetic_incidents() -> list[list[str]]:
    devices = ["pump", "valve", "sensor", "motor"]
    locations = ["north", "south", "east", "west"]
    conditions = ["pressure", "temperature", "vibration", "flow"]
    levels = ["high", "low"]
    return [f"the {device} in {location} reports {level} {condition}".split()
            for device in devices for location in locations
            for condition in conditions for level in levels]


def split_incidents(seed: int = 7) -> tuple[list[list[str]], list[list[str]]]:
    sequences = synthetic_incidents()
    random.Random(seed).shuffle(sequences)
    return sequences[:96], sequences[96:]


def train_default(*, epochs: int = 20, seed: int = 7) -> tuple[TinyDenoiser, list[list[str]], list[list[str]], list[float]]:
    train, test = split_incidents(seed)
    model = TinyDenoiser.from_sequences(train)
    losses = model.train(train, epochs=epochs, seed=seed)
    return model, train, test, losses


def benchmark(*, epochs: int = 20, steps: int = 4, seed: int = 7) -> dict:
    model, train, test, losses = train_default(epochs=epochs, seed=seed)
    baseline = BigramBaseline(train)
    rng = random.Random(seed)
    correct, total, probabilities = 0, 0, []
    for sequence in test:
        masked, positions = mask_tokens(sequence, 0.4, rng, ensure_one=True)
        for position in positions:
            scores = model.probabilities(masked, position)
            prediction = max(scores, key=scores.get)
            correct += prediction == sequence[position]
            total += 1
            probabilities.append(scores[sequence[position]])
    diffusion = profile(lambda: generate(model, length=8, steps=steps, seed=seed))
    autoregressive = profile(lambda: baseline.generate(8, seed=seed))
    return {
        "dataset": {"train": len(train), "held_out": len(test), "seed": seed},
        "masked_reconstruction_accuracy": correct / total,
        "token_error_rate": (total - correct) / total,
        "masked_cross_entropy_nats": cross_entropy(probabilities),
        "training_loss_first_last": [losses[0], losses[-1]],
        "diffusion": diffusion,
        "autoregressive": autoregressive,
        "comparison_note": "Reconstruction accuracy applies only to the masked model. Generated text is illustrative; no claim of semantic quality equivalence is made. Python traced memory excludes native allocations.",
    }
