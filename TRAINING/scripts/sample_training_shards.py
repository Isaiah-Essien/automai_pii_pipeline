#!/usr/bin/env python3
"""CLI: reservoir-sample eval / NER / adj shards from part-*.jsonl (run locally on HDD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_training_package_on_path

ensure_training_package_on_path()

from contextual_phi.shard_sampler import ShardSamplingTargets, TrainingShardSampler  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Sample Colab-sized training shards")
    parser.add_argument("--source", type=str, required=True, help="Directory with part-*.jsonl")
    parser.add_argument("--output", type=str, required=True, help="Output directory for shards")
    parser.add_argument("--ner-size", type=int, default=3_000_000)
    parser.add_argument("--adj-size", type=int, default=400_000)
    parser.add_argument("--eval-size", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    targets = ShardSamplingTargets(
        evaluation_lines=args.eval_size,
        ner_lines=args.ner_size,
        adjudication_lines=args.adj_size,
        random_seed=args.seed,
    )
    sampler = TrainingShardSampler(targets)
    manifest = sampler.write_shard_bundle(
        source_directory=Path(args.source),
        output_directory=Path(args.output),
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()