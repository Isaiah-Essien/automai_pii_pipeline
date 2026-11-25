"""Load and group seven-field span JSONL used for NER and adjudication."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

from contextual_phi.constants import REDACT_ENTITY_TYPES, VALID_DECISIONS


@dataclass(frozen=True)
class SpanTrainingRow:
    """
    One JSONL line: a single annotated span inside a clinical sentence.

    All generators and shard scripts must keep offsets consistent with `span`.
    """

    sentence_id: int
    sentence: str
    span_start: int
    span_end: int
    span_text: str
    phi_type: str
    decision: str

    @classmethod
    def from_json_dict(cls, row: Dict[str, Any]) -> "SpanTrainingRow":
        """Parse a dict after json.loads; keys match the team schema."""
        return cls(
            sentence_id=int(row["sentence_id"]),
            sentence=row["sentence"],
            span_start=int(row["span_start"]),
            span_end=int(row["span_end"]),
            span_text=row["span"],
            phi_type=row["phi_type"],
            decision=row["decision"],
        )


@dataclass
class GroupedSentenceSpans:
    """Every span row that shares one sentence_id."""

    sentence_id: int
    sentence_text: str
    spans: List[Tuple[int, int, str, str]]  # start, end, phi_type, decision


class SpanJsonlReader:
    """
    Stream or materialize span JSONL with offset checks.

    Fails fast on bad offsets so we do not train on corrupted shards.
    """

    def __init__(self, jsonl_path: Path) -> None:
        self.jsonl_path = jsonl_path

    def iter_rows(self, max_rows: Optional[int] = None) -> Iterator[SpanTrainingRow]:
        """
        Yield validated rows in file order.

        Args:
            max_rows: Stop after this many lines (pilot runs on Colab).
        """
        seen = 0
        with self.jsonl_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                row = SpanTrainingRow.from_json_dict(json.loads(raw_line))
                self._assert_offsets_match(row)
                yield row
                seen += 1
                if max_rows is not None and seen >= max_rows:
                    break

    def load_all(self, max_rows: Optional[int] = None) -> List[SpanTrainingRow]:
        """Materialize rows into a list (use only on shards that fit in RAM)."""
        return list(self.iter_rows(max_rows=max_rows))

    @staticmethod
    def _assert_offsets_match(row: SpanTrainingRow) -> None:
        snippet = row.sentence[row.span_start : row.span_end]
        if snippet != row.span_text:
            raise ValueError(
                f"Offset mismatch for sentence_id={row.sentence_id}: "
                f"expected {row.span_text!r}, got {snippet!r}"
            )
        if row.decision not in VALID_DECISIONS:
            raise ValueError(f"Unknown decision {row.decision!r}")


class SentenceSpanGrouper:
    """Collapse span-level lines into one structure per sentence_id."""

    def group_by_sentence(
        self, rows: List[SpanTrainingRow]
    ) -> Dict[int, GroupedSentenceSpans]:
        """
        Group rows by sentence_id.

        Returns:
            Mapping sentence_id -> grouped spans with shared sentence text.
        """
        buckets: Dict[int, Dict[str, Any]] = defaultdict(
            lambda: {"text": None, "spans": []}
        )
        for row in rows:
            entry = buckets[row.sentence_id]
            entry["text"] = row.sentence
            entry["spans"].append(
                (row.span_start, row.span_end, row.phi_type, row.decision)
            )
        return {
            sid: GroupedSentenceSpans(
                sentence_id=sid,
                sentence_text=data["text"],
                spans=data["spans"],
            )
            for sid, data in buckets.items()
        }

    def redact_spans_for_ner(
        self, grouped: GroupedSentenceSpans
    ) -> List[Tuple[int, int, str]]:
        """
        Pick spans for Stage 1 BIO training.

        Only REDACT decisions on PHI types we care about in Phase 1.
        """
        result: List[Tuple[int, int, str]] = []
        for start, end, phi_type, decision in grouped.spans:
            if decision == "REDACT" and phi_type in REDACT_ENTITY_TYPES:
                result.append((start, end, phi_type))
        return result