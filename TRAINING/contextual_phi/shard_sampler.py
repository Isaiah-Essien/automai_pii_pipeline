"""Reservoir-sample eval / NER / adj shards from part-*.jsonl on an external drive."""

from __future__ import annotations

import json
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set


@dataclass
class ShardSamplingTargets:
    """How many lines we want in each downstream shard file."""

    evaluation_lines: int = 100_000
    ner_lines: int = 3_000_000
    adjudication_lines: int = 400_000
    random_seed: int = 42


class TrainingShardSampler:
    """
    Build eval_100k, ner_*M, and adj_400k without loading the full corpus into RAM.

    Algorithms:
      - Evaluation: reservoir sample over the full stream; double weight for PRESERVE rows.
      - NER: second pass, reservoir sample, skip sentence_ids held out for eval.
      - Adjudication: collect ambiguous / PRESERVE-rich rows up to a cap, then subsample.
    """

    PRESERVE_HINT_TYPES = {"DISEASE", "DRUG", "AGE", "NON_PHI"}

    def __init__(self, targets: ShardSamplingTargets) -> None:
        self.targets = targets

    @staticmethod
    def parse_jsonl_line(raw_line: str) -> Optional[Dict[str, Any]]:
        """Validate one line against the seven-field span schema."""
        try:
            row = json.loads(raw_line)
        except json.JSONDecodeError:
            return None
        required = {
            "sentence_id",
            "sentence",
            "span_start",
            "span_end",
            "span",
            "phi_type",
            "decision",
        }
        if not required.issubset(row.keys()):
            return None
        start, end = int(row["span_start"]), int(row["span_end"])
        if row["sentence"][start:end] != row["span"]:
            return None
        if row["decision"] not in {"REDACT", "PRESERVE"}:
            return None
        return row

    @staticmethod
    def list_part_files(source_directory: Path) -> List[Path]:
        return sorted(source_directory.glob("part-*.jsonl"))

    def iter_valid_rows(self, source_directory: Path) -> Iterator[Dict[str, Any]]:
        """Stream all valid rows from part-*.jsonl files."""
        for part_path in self.list_part_files(source_directory):
            with part_path.open("r", encoding="utf-8") as handle:
                for raw_line in handle:
                    raw_line = raw_line.strip()
                    if not raw_line:
                        continue
                    row = self.parse_jsonl_line(raw_line)
                    if row:
                        yield row

    @staticmethod
    def reservoir_update(
        reservoir: List[Dict[str, Any]],
        row: Dict[str, Any],
        capacity: int,
        items_seen: int,
        rng: random.Random,
    ) -> None:
        """
        Classic reservoir sampling step.

        After items_seen rows, each new row replaces a uniform random slot with
        probability capacity / items_seen.
        """
        if len(reservoir) < capacity:
            reservoir.append(row)
            return
        pick = rng.randint(0, items_seen - 1)
        if pick < capacity:
            reservoir[pick] = row

    def sample_evaluation_holdout(
        self, source_directory: Path
    ) -> List[Dict[str, Any]]:
        """Reservoir sample eval lines; overweight PRESERVE so eval is not all REDACT."""
        rng = random.Random(self.targets.random_seed)
        reservoir: List[Dict[str, Any]] = []
        seen = 0
        for row in self.iter_valid_rows(source_directory):
            seen += 1
            draws = 2 if row["decision"] == "PRESERVE" else 1
            for _ in range(draws):
                self.reservoir_update(
                    reservoir,
                    row,
                    self.targets.evaluation_lines,
                    seen,
                    rng,
                )
        return reservoir[: self.targets.evaluation_lines]

    def sample_ner_shard(
        self,
        source_directory: Path,
        held_out_sentence_ids: Set[Any],
    ) -> List[Dict[str, Any]]:
        """Reservoir sample NER shard, excluding eval sentence_ids."""
        rng = random.Random(self.targets.random_seed + 1)
        reservoir: List[Dict[str, Any]] = []
        seen = 0
        for row in self.iter_valid_rows(source_directory):
            if row["sentence_id"] in held_out_sentence_ids:
                continue
            seen += 1
            self.reservoir_update(
                reservoir,
                row,
                self.targets.ner_lines,
                seen,
                rng,
            )
        return reservoir

    def sample_adjudication_shard(
        self,
        source_directory: Path,
        held_out_sentence_ids: Set[Any],
    ) -> List[Dict[str, Any]]:
        """
        Prefer PRESERVE and clinically ambiguous types for Stage 2.

        We scan until we have enough candidates, shuffle, then cut to adj size.
        """
        candidates: List[Dict[str, Any]] = []
        scan_limit = self.targets.adjudication_lines * 4
        for row in self.iter_valid_rows(source_directory):
            if row["sentence_id"] in held_out_sentence_ids:
                continue
            if row["decision"] == "PRESERVE" or row["phi_type"] in self.PRESERVE_HINT_TYPES:
                candidates.append(row)
            if len(candidates) >= scan_limit:
                break
        random.Random(self.targets.random_seed + 2).shuffle(candidates)
        return candidates[: self.targets.adjudication_lines]

    def write_shard_bundle(self, source_directory: Path, output_directory: Path) -> Dict[str, Any]:
        """
        Run the full sampling pipeline and write JSONL plus manifest.json.

        Returns:
            Manifest dict with line counts for logging.
        """
        if not self.list_part_files(source_directory):
            raise FileNotFoundError(f"No part-*.jsonl under {source_directory}")

        eval_rows = self.sample_evaluation_holdout(source_directory)
        eval_ids = {row["sentence_id"] for row in eval_rows}
        ner_rows = self.sample_ner_shard(source_directory, eval_ids)
        adj_rows = self.sample_adjudication_shard(source_directory, eval_ids)

        output_directory.mkdir(parents=True, exist_ok=True)
        self._write_jsonl(output_directory / "eval_100k.jsonl", eval_rows)
        ner_millions = self.targets.ner_lines // 1_000_000
        self._write_jsonl(output_directory / f"ner_{ner_millions}M.jsonl", ner_rows)
        self._write_jsonl(output_directory / "adj_400k.jsonl", adj_rows)

        manifest = {
            "source": str(source_directory),
            "eval": len(eval_rows),
            "ner": len(ner_rows),
            "adj": len(adj_rows),
            "seed": self.targets.random_seed,
            "decision_mix_eval": dict(Counter(r["decision"] for r in eval_rows)),
        }
        (output_directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        return manifest

    @staticmethod
    def _write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")