#!/usr/bin/env python3
"""CLI: Stage 1 NER fine-tune on ner_3M or ner_5M shards."""

from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import ensure_training_package_on_path

ensure_training_package_on_path()

from contextual_phi.ner_finetune import NerFineTuningJob  # noqa: E402
from contextual_phi.project_settings import DeidProjectSettings  # noqa: E402


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fine-tune PHI NER (not LM pretraining)")
    parser.add_argument("--profile", choices=["3M", "5M"], default="3M")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Shard/checkpoint root (Colab Drive path or local phi_project folder)",
    )
    parser.add_argument(
        "--pilot",
        action="store_true",
        help="Train on first 50k NER lines only",
    )
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()
    if args.project_root:
        settings = DeidProjectSettings.for_local_workspace(
            project_root=Path(args.project_root),
            profile=args.profile,
        )
    else:
        settings = DeidProjectSettings.for_colab(profile=args.profile)

    if args.pilot:
        settings.hyperparameters.row_limit = 50_000
        settings.run_name = f"ner_{args.profile}_pilot"

    NerFineTuningJob(settings).run()


if __name__ == "__main__":
    main()