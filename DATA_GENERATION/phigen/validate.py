"""Every validation check in Section 14.

Validation is part of the build, not a manual review step.  A line that fails is
quarantined together with the reason it failed, never silently dropped, so a
systematic generator fault shows up as a growing quarantine file rather than as
a quietly smaller corpus.
"""

from __future__ import annotations

import json
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .schema import (
    ALL_TYPES,
    AMBIGUITY_TYPES,
    PHI_LANGUAGES,
    METADATA_FIELDS,
    NEGATIVE_FIELDS,
    PRESERVE_TYPES,
    REDACT_TYPES,
    REQUIRED_FIELDS,
    SURFACE_FORMS,
)


@dataclass
class Failure:
    scope: str  # "line", "group", or "corpus"
    check: str
    reason: str
    shard: str = ""
    line_number: int = 0
    payload: dict | None = None


@dataclass
class ValidationReport:
    lines_checked: int = 0
    groups_checked: int = 0
    negatives_checked: int = 0
    failures: list[Failure] = field(default_factory=list)
    checks_run: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures

    def add(self, failure: Failure) -> None:
        self.failures.append(failure)

    def summary(self) -> dict:
        by_check: dict[str, int] = defaultdict(int)
        for f in self.failures:
            by_check[f"{f.scope}:{f.check}"] += 1
        return {
            "lines_checked": self.lines_checked,
            "groups_checked": self.groups_checked,
            "negatives_checked": self.negatives_checked,
            "checks_run": self.checks_run,
            "failure_count": len(self.failures),
            "failures_by_check": dict(by_check),
            "passed": self.passed,
        }


LINE_CHECKS = (
    "parse",
    "offset_consistency",
    "bounds",
    "non_empty_span",
    "type_membership",
    "decision_consistency",
    "no_literal_newline",
)
GROUP_CHECKS = (
    "sentence_identity",
    "ordering",
    "overlap_policy",
    "duplicate_spans",
)
CORPUS_CHECKS = (
    "identifier_sequence",
    "shard_integrity",
    "split_integrity",
)


def _check_line(record: dict, shard: str, line_no: int, report: ValidationReport,
                id_per_line: bool = False) -> bool:
    """Section 14.1.  Returns True when the line is clean."""
    ok = True

    # Parse: the seven required keys plus the Section 12 metadata fields.
    missing = [k for k in REQUIRED_FIELDS + METADATA_FIELDS if k not in record]
    if missing:
        report.add(Failure("line", "parse", f"missing keys: {missing}", shard, line_no, record))
        return False
    allowed = set(REQUIRED_FIELDS) | set(METADATA_FIELDS)
    if id_per_line:
        allowed.add("group_id")
    extra = set(record) - allowed
    if extra:
        report.add(
            Failure("line", "parse", f"unexpected keys: {sorted(extra)}", shard, line_no, record)
        )
        ok = False

    sentence = record["sentence"]
    start, end, span = record["span_start"], record["span_end"], record["span"]

    if not isinstance(start, int) or not isinstance(end, int):
        report.add(Failure("line", "bounds", "offsets must be integers", shard, line_no, record))
        return False

    # Bounds: 0 <= span_start < span_end <= len(sentence).
    if not (0 <= start < end <= len(sentence)):
        report.add(
            Failure(
                "line",
                "bounds",
                f"0 <= {start} < {end} <= {len(sentence)} is false",
                shard,
                line_no,
                record,
            )
        )
        return False

    # Offset consistency, after NFC normalisation.
    nfc_sentence = unicodedata.normalize("NFC", sentence)
    if nfc_sentence != sentence:
        report.add(
            Failure("line", "offset_consistency", "sentence is not NFC", shard, line_no, record)
        )
        ok = False
    if sentence[start:end] != span:
        report.add(
            Failure(
                "line",
                "offset_consistency",
                f"sentence[{start}:{end}]={sentence[start:end]!r} != span={span!r}",
                shard,
                line_no,
                record,
            )
        )
        ok = False

    # Non-empty span.
    if not span.strip():
        report.add(
            Failure("line", "non_empty_span", "span is empty or whitespace", shard, line_no, record)
        )
        ok = False

    # Type membership.
    phi_type = record["phi_type"]
    if phi_type not in ALL_TYPES:
        report.add(
            Failure("line", "type_membership", f"unknown phi_type {phi_type!r}", shard, line_no, record)
        )
        ok = False

    # Decision consistency with the type's schema section.
    decision = record["decision"]
    if decision not in ("REDACT", "PRESERVE"):
        report.add(
            Failure("line", "decision_consistency", f"bad decision {decision!r}", shard, line_no, record)
        )
        ok = False
    elif phi_type in REDACT_TYPES and decision != "REDACT":
        report.add(
            Failure(
                "line",
                "decision_consistency",
                f"{phi_type} is a Section 4 type but decision is {decision}",
                shard,
                line_no,
                record,
            )
        )
        ok = False
    elif phi_type in PRESERVE_TYPES and decision != "PRESERVE":
        report.add(
            Failure(
                "line",
                "decision_consistency",
                f"{phi_type} is a Section 5 type but decision is {decision}",
                shard,
                line_no,
                record,
            )
        )
        ok = False

    # No literal newline.
    if "\n" in sentence or "\r" in sentence:
        report.add(
            Failure("line", "no_literal_newline", "sentence contains a newline", shard, line_no, record)
        )
        ok = False

    # Metadata sanity beyond the schema's explicit table.
    if record["ambiguity_type"] not in AMBIGUITY_TYPES:
        report.add(
            Failure("line", "parse", f"bad ambiguity_type {record['ambiguity_type']!r}", shard, line_no, record)
        )
        ok = False
    if record["surface_form"] not in SURFACE_FORMS:
        report.add(
            Failure("line", "parse", f"bad surface_form {record['surface_form']!r}", shard, line_no, record)
        )
        ok = False
    langs = record["phi_languages"]
    if not isinstance(langs, list) or any(l not in PHI_LANGUAGES for l in langs):
        report.add(
            Failure("line", "parse", f"bad phi_languages {langs!r}", shard, line_no, record)
        )
        ok = False
    elif langs != sorted(langs):
        report.add(
            Failure("line", "parse", "phi_languages is not sorted", shard, line_no, record)
        )
        ok = False
    # code_switched must agree with the languages actually present.
    expected_cs = any(l != "en" for l in langs) if isinstance(langs, list) else None
    if expected_cs is not None and record["code_switched"] != expected_cs:
        report.add(
            Failure(
                "line",
                "parse",
                f"code_switched={record['code_switched']} disagrees with phi_languages={langs}",
                shard,
                line_no,
                record,
            )
        )
        ok = False

    if record["source"] not in ("synthetic", "real"):
        report.add(
            Failure("line", "parse", f"bad source {record['source']!r}", shard, line_no, record)
        )
        ok = False

    return ok


def _check_group(sentence_id: int, records: list[dict], report: ValidationReport) -> None:
    """Section 14.2 checks that apply within one sentence_id."""
    # Sentence identity: byte-identical text on every line of the group.
    texts = {r["sentence"] for r in records}
    if len(texts) > 1:
        report.add(
            Failure("group", "sentence_identity", f"{len(texts)} distinct sentence texts", payload={"sentence_id": sentence_id})
        )

    # Ordering: ascending span_start, shorter span first on a tie.
    keys = [(r["span_start"], r["span_end"]) for r in records]
    if keys != sorted(keys):
        report.add(
            Failure("group", "ordering", f"spans out of order: {keys}", payload={"sentence_id": sentence_id})
        )

    # Duplicate spans.
    if len(set(keys)) != len(keys):
        report.add(
            Failure("group", "duplicate_spans", f"repeated offsets in {keys}", payload={"sentence_id": sentence_id})
        )

    # Overlap policy: no same-type overlap; cross-type only under containment.
    for i, a in enumerate(records):
        for b in records[i + 1 :]:
            a_s, a_e = a["span_start"], a["span_end"]
            b_s, b_e = b["span_start"], b["span_end"]
            if not (a_s < b_e and b_s < a_e):
                continue
            if a["phi_type"] == b["phi_type"]:
                report.add(
                    Failure(
                        "group",
                        "overlap_policy",
                        f"same-type overlap for {a['phi_type']}: ({a_s},{a_e}) and ({b_s},{b_e})",
                        payload={"sentence_id": sentence_id},
                    )
                )
                continue
            contained = (a_s <= b_s and b_e <= a_e) or (b_s <= a_s and a_e <= b_e)
            if not contained:
                report.add(
                    Failure(
                        "group",
                        "overlap_policy",
                        f"partial overlap: ({a_s},{a_e}) and ({b_s},{b_e})",
                        payload={"sentence_id": sentence_id},
                    )
                )


def _check_negative(record: dict, shard: str, line_no: int, report: ValidationReport,
                    id_per_line: bool = False) -> bool:
    """Section 13.3: negatives carry exactly the six listed keys."""
    keys = set(record)
    expected = set(NEGATIVE_FIELDS) | ({"group_id"} if id_per_line else set())
    if keys != expected:
        report.add(
            Failure(
                "line",
                "parse",
                f"negative line keys {sorted(keys)} != {sorted(expected)}",
                shard,
                line_no,
                record,
            )
        )
        return False
    if "\n" in record["sentence"] or "\r" in record["sentence"]:
        report.add(Failure("line", "no_literal_newline", "negative sentence has a newline", shard, line_no, record))
        return False
    if unicodedata.normalize("NFC", record["sentence"]) != record["sentence"]:
        report.add(Failure("line", "offset_consistency", "negative sentence is not NFC", shard, line_no, record))
        return False
    return True


def validate_build(
    out_dir: Path | str,
    quarantine_path: Path | str | None = None,
    start_sentence_id: int = 1,
    id_per_line: bool = False,
) -> ValidationReport:
    """Validate every shard of a build, quarantining any failing line.

    `start_sentence_id` is the first id this build was expected to emit.  A
    corpus produced in several passes continues the sequence rather than
    restarting, so checking against 1 would report every id in the earlier
    passes as a gap.

    `id_per_line` says the build gave every line its own id and moved the
    sentence's id to `group_id`.  The group checks then key on `group_id`,
    since a sentence_id no longer identifies a sentence.
    """
    out = Path(out_dir)
    report = ValidationReport()
    report.checks_run = list(LINE_CHECKS + GROUP_CHECKS + CORPUS_CHECKS)
    quarantine = Path(quarantine_path or out / "quarantine.jsonl")
    quarantined: list[tuple[dict, Failure]] = []

    positive_shards = sorted(out.glob("part-*.jsonl"))
    negative_shards = sorted(out.glob("negatives-*.jsonl"))

    groups: dict[int, list[dict]] = defaultdict(list)
    shard_of_sentence: dict[int, set[str]] = defaultdict(set)
    note_ids: dict[str, set[int]] = defaultdict(set)
    all_ids: set[int] = set()

    # ---- line level -------------------------------------------------------
    for shard in positive_shards:
        for line_no, raw in enumerate(shard.open(encoding="utf-8"), start=1):
            raw = raw.rstrip("\n")
            if not raw:
                continue
            report.lines_checked += 1
            before = len(report.failures)
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                failure = Failure("line", "parse", f"invalid JSON: {exc}", shard.name, line_no)
                report.add(failure)
                quarantined.append(({"raw": raw}, failure))
                continue
            clean = _check_line(record, shard.name, line_no, report, id_per_line)
            if not clean:
                quarantined.append((record, report.failures[before]))
                continue
            # The sequence and shard checks follow sentence_id; grouping
            # follows group_id when ids are per line, since a sentence_id then
            # identifies a single line rather than a sentence.
            sid = record["sentence_id"]
            group_key = record["group_id"] if id_per_line else sid
            groups[group_key].append(record)
            shard_of_sentence[group_key].add(shard.name)
            all_ids.add(sid)
            note_ids[record["note_id"]].add(sid)

    for shard in negative_shards:
        for line_no, raw in enumerate(shard.open(encoding="utf-8"), start=1):
            raw = raw.rstrip("\n")
            if not raw:
                continue
            report.negatives_checked += 1
            before = len(report.failures)
            try:
                record = json.loads(raw)
            except json.JSONDecodeError as exc:
                failure = Failure("line", "parse", f"invalid JSON: {exc}", shard.name, line_no)
                report.add(failure)
                quarantined.append(({"raw": raw}, failure))
                continue
            if not _check_negative(record, shard.name, line_no, report, id_per_line):
                quarantined.append((record, report.failures[before]))
                continue
            all_ids.add(record["sentence_id"])

    # ---- group level ------------------------------------------------------
    for sentence_id, records in groups.items():
        report.groups_checked += 1
        _check_group(sentence_id, records, report)

    # ---- corpus level -----------------------------------------------------
    # Identifier sequence: consecutive from the build's starting id, no duplicates.
    if all_ids:
        low = min(all_ids)
        if low != start_sentence_id:
            report.add(
                Failure(
                    "corpus",
                    "identifier_sequence",
                    f"lowest sentence_id is {low}, expected {start_sentence_id}",
                )
            )
        expected = set(range(start_sentence_id, max(all_ids) + 1))
        missing = expected - all_ids
        if missing:
            sample = sorted(missing)[:10]
            report.add(
                Failure(
                    "corpus",
                    "identifier_sequence",
                    f"{len(missing)} sentence_id gaps, e.g. {sample}",
                )
            )

    # Shard integrity: no sentence_id spans two shards.
    for sentence_id, shards in shard_of_sentence.items():
        if len(shards) > 1:
            report.add(
                Failure(
                    "corpus",
                    "shard_integrity",
                    f"sentence_id {sentence_id} appears in {sorted(shards)}",
                )
            )

    # Split integrity: no note_id or patient_id in more than one split.  Splits
    # are assigned at training time (Section 1), so at build time we assert the
    # grouping key is intact -- every sentence of a note shares one patient_id.
    patient_of_note: dict[str, set[str]] = defaultdict(set)
    for records in groups.values():
        for record in records:
            patient_of_note[record["note_id"]].add(record["patient_id"])
    for note_id, patients in patient_of_note.items():
        if len(patients) > 1:
            report.add(
                Failure(
                    "corpus",
                    "split_integrity",
                    f"note_id {note_id} maps to {len(patients)} patient_ids, "
                    "so a grouped split cannot keep it whole",
                )
            )

    # ---- quarantine -------------------------------------------------------
    if quarantined:
        with quarantine.open("w", encoding="utf-8") as fh:
            for record, failure in quarantined:
                fh.write(
                    json.dumps(
                        {
                            "reason": failure.reason,
                            "check": failure.check,
                            "shard": failure.shard,
                            "line_number": failure.line_number,
                            "record": record,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

    return report
