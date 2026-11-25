#!/usr/bin/env python3
"""CLI: Stage 2 REDACT vs PRESERVE fine-tune on adj_400k."""

from __future__ import annotations

import argparse
from pathlib import Path

from _bootstrap import ensure_training_package_on_path

ensure_training_package_on_path()

from contextual_phi.adjudication_finetune import AdjudicationFineTuningJob  # noqa: E402
from contextual_phi.project_settings import DeidProjectSettings  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune span adjudicator")
    parser.add_argument("--profile", choices=["3M", "5M"], default="3M")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--full", action="store_true", help="Use all rows in adj_400k.jsonl")
    args = parser.parse_args()

    if args.project_root:
        settings = DeidProjectSettings.for_local_workspace(Path(args.project_root), args.profile)
    else:
        settings = DeidProjectSettings.for_colab(profile=args.profile)

    row_cap = None if args.full else 50_000
    AdjudicationFineTuningJob(settings).run(max_rows=row_cap)


if __name__ == "__main__":
    main()