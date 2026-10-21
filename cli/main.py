"""Run the experiments without starting the API."""

import argparse
import json
from pathlib import Path
import random

from src.diffusion.generator import generate
from src.diffusion.noise import alpha_bars, linear_beta_schedule, sample_xt
from src.evaluation.reports import write_report
from src.evaluation.runner import benchmark, train_default


def main() -> None:
    parser = argparse.ArgumentParser(prog="enterprise-ai")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("noise")
    training = commands.add_parser("train")
    training.add_argument("--epochs", type=int, default=20)
    training.add_argument("--output", type=Path, default=Path("reports/tiny_denoiser.json"))
    generation = commands.add_parser("generate")
    generation.add_argument("--steps", type=int, default=4)
    generation.add_argument("--length", type=int, default=8)
    generation.add_argument("--prefix", nargs="*", default=[])
    measurement = commands.add_parser("benchmark")
    measurement.add_argument("--steps", type=int, default=4)
    measurement.add_argument("--output", type=Path, default=Path("reports/lecture_08.json"))
    args = parser.parse_args()
    if args.command == "noise":
        bars = alpha_bars(linear_beta_schedule(10))
        result = {"alpha_bars": bars, "sample": sample_xt([1.0, -1.0], bars[-1], random.Random(7))}
    elif args.command == "train":
        model, train, test, losses = train_default(epochs=args.epochs)
        model.save(args.output)
        result = {"model": str(args.output), "train": len(train), "held_out": len(test), "losses": losses}
    elif args.command == "generate":
        model, _, _, _ = train_default()
        result = generate(model, length=args.length, steps=args.steps, prefix=args.prefix, seed=7)
    else:
        result = benchmark(steps=args.steps)
        write_report(result, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
