#!/usr/bin/env python3
"""CLI: EDA stats, bar charts, word cloud, and bigram list for one shard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import ensure_training_package_on_path

ensure_training_package_on_path()

from contextual_phi.project_settings import DeidProjectSettings  # noqa: E402
from contextual_phi.shard_eda import ShardExploratoryReport  # noqa: E402
from contextual_phi.span_io import SpanJsonlReader  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="PHI shard exploratory analysis")
    parser.add_argument("--profile", choices=["3M", "5M"], default="3M")
    parser.add_argument("--project-root", default=None)
    parser.add_argument("--shard", choices=["eval", "ner", "adj"], default="eval")
    parser.add_argument("--max-rows", type=int, default=100_000)
    args = parser.parse_args()

    if args.project_root:
        settings = DeidProjectSettings.for_local_workspace(Path(args.project_root), args.profile)
    else:
        settings = DeidProjectSettings.for_colab(profile=args.profile)

    shard_name = {
        "eval": settings.hyperparameters.evaluation_shard_filename,
        "ner": settings.hyperparameters.ner_shard_filename,
        "adj": settings.hyperparameters.adjudication_shard_filename,
    }[args.shard]

    rows = SpanJsonlReader(settings.paths.shard_file(shard_name)).load_all(max_rows=args.max_rows)
    report = ShardExploratoryReport(settings.paths.log_root / "eda")
    stats = report.summarize(rows)

    stats_path = report.output_directory / f"stats_{args.shard}.json"
    stats_path.write_text(
        json.dumps(
            {
                "line_count": stats.line_count,
                "decision_counts": stats.decision_counts,
                "phi_type_counts": stats.phi_type_counts,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    report.save_count_bar_chart(
        stats.decision_counts, "Decision counts", f"{args.shard}_decision.png"
    )
    report.save_count_bar_chart(
        stats.phi_type_counts, "PHI type counts", f"{args.shard}_phi_type.png"
    )
    report.save_word_cloud(rows, f"{args.shard}_wordcloud.png")

    bigrams = report.most_common_ngrams(rows, n=2, top_k=30)
    (report.output_directory / f"{args.shard}_bigrams.txt").write_text(
        "\n".join(f"{gram}\t{count}" for gram, count in bigrams),
        encoding="utf-8",
    )

    print(f"EDA artifacts: {report.output_directory}")
    print(json.dumps(stats.decision_counts, indent=2))


if __name__ == "__main__":
    main()