"""Paired masked reconstruction sweep over ratios, reverse steps and seeds."""

import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.diffusion.baselines import PositionFrequencyBaseline
from src.diffusion.generator import reconstruct_iterative
from src.diffusion.masking import mask_tokens
from src.evaluation.runner import train_default


def run() -> dict:
    model, train, test, _ = train_default()
    baseline = PositionFrequencyBaseline(train)
    rows = []
    for ratio in (0.15, 0.4, 0.75):
        for seed in (7, 17, 27):
            rng = random.Random(seed)
            examples = [(sequence, *mask_tokens(sequence, ratio, rng, ensure_one=True)) for sequence in test]
            baseline_correct = sum(baseline.reconstruct(masked)[position] == sequence[position]
                                   for sequence, masked, positions in examples for position in positions)
            total = sum(len(positions) for _, _, positions in examples)
            for steps in (1, 2, 4, 8):
                correct = sum(reconstruct_iterative(model, masked, steps=steps, seed=seed)["tokens"][position] == sequence[position]
                              for sequence, masked, positions in examples for position in positions)
                rows.append({"mask_ratio": ratio, "seed": seed, "reverse_steps": steps, "masked_tokens": total,
                             "denoiser_accuracy": correct / total, "position_baseline_accuracy": baseline_correct / total})
    return {"dataset": {"train": len(train), "held_out": len(test)}, "rows": rows,
            "note": "Paired masks and held-out sequences. The position-frequency baseline is trained only on the training split."}


if __name__ == "__main__":
    report = run()
    target = Path("reports/lecture_08_sweep.json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(target), "rows": len(report["rows"])}, indent=2))
