"""Exploratory plots and counts on eval / NER / adj shards before GPU training."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from contextual_phi.span_io import SpanTrainingRow


@dataclass
class ShardSummaryStatistics:
    """Aggregates we print and stash as JSON next to plots."""

    line_count: int
    decision_counts: Dict[str, int]
    phi_type_counts: Dict[str, int]
    span_length_histogram: Dict[str, int]
    sentence_length_buckets: Dict[str, int]


class ShardExploratoryReport:
    """
    Compute shard statistics and optional matplotlib / wordcloud artifacts.

    Designed to run on eval_100k from a CPU machine before we burn Colab GPU hours.
    """

    def __init__(self, output_directory: Path) -> None:
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def summarize(self, rows: List[SpanTrainingRow]) -> ShardSummaryStatistics:
        """Single pass over rows for counts and coarse length buckets."""
        decisions: Counter = Counter()
        phi_types: Counter = Counter()
        span_lengths: Counter = Counter()
        sentence_buckets: Counter = Counter()
        sentence_text_by_id: Dict[int, str] = {}

        for row in rows:
            decisions[row.decision] += 1
            phi_types[row.phi_type] += 1
            span_lengths[len(row.span_text)] += 1
            sentence_text_by_id[row.sentence_id] = row.sentence

        for text in sentence_text_by_id.values():
            if len(text) < 80:
                bucket = "short"
            elif len(text) < 160:
                bucket = "medium"
            else:
                bucket = "long"
            sentence_buckets[bucket] += 1

        return ShardSummaryStatistics(
            line_count=len(rows),
            decision_counts=dict(decisions),
            phi_type_counts=dict(phi_types),
            span_length_histogram=dict(span_lengths),
            sentence_length_buckets=dict(sentence_buckets),
        )

    def tokenize_for_ngrams(self, text: str) -> List[str]:
        """Simple alphanumeric tokenizer for bigram frequency lists."""
        return re.findall(r"[A-Za-z0-9]+", text.lower())

    def most_common_ngrams(
        self,
        rows: List[SpanTrainingRow],
        n: int = 2,
        top_k: int = 40,
    ) -> List[Tuple[str, int]]:
        """
        Count n-gram frequencies across sentence text (not just span text).

        Args:
            n: 1=unigram, 2=bigram, etc.
            top_k: How many top entries to return.
        """
        counts: Counter = Counter()
        for row in rows:
            tokens = self.tokenize_for_ngrams(row.sentence)
            for index in range(len(tokens) - n + 1):
                gram = " ".join(tokens[index : index + n])
                counts[gram] += 1
        return counts.most_common(top_k)

    def save_word_cloud(
        self,
        rows: List[SpanTrainingRow],
        filename: str = "wordcloud.png",
    ) -> Optional[Path]:
        """Plot a word cloud of sentence text (skipped if optional deps missing)."""
        try:
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
        except ImportError:
            return None

        corpus = " ".join(row.sentence for row in rows[:50_000])
        cloud = WordCloud(width=1200, height=600, background_color="white").generate(corpus)
        output_path = self.output_directory / filename
        plt.figure(figsize=(12, 6))
        plt.imshow(cloud, interpolation="bilinear")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path

    def save_count_bar_chart(
        self,
        counts: Dict[str, int],
        chart_title: str,
        filename: str,
    ) -> Optional[Path]:
        """Save a simple bar chart when matplotlib is installed."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            return None

        labels = list(counts.keys())
        values = [counts[key] for key in labels]
        output_path = self.output_directory / filename
        plt.figure(figsize=(10, 5))
        plt.bar(labels, values)
        plt.title(chart_title)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path