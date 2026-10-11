"""Corpus assembly: sentence ids, decision-mix control, sharding, writers.

The generator owns exactly one global sentence_id counter.  Ids are consecutive
from 1 with no gaps, and a sentence's lines are always written as a unit, so no
sentence_id can straddle two shards.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path

from .config import Config
from .diversity import DiversityTracker
from .lexicons import Lexicons, load_lexicons
from .metadata import NoteContext, make_note_context
from .schema import METADATA_FIELDS, NEGATIVE_FIELDS, REQUIRED_FIELDS, decision_for
from .spans import SpanBuilder, SpanError
from .frames import Slots, compose_frame, ensure_probed
from .templates import REGISTRY, Template, negative_sentence, templates_by_decision
from .variants import EMAIL_FAMILIES, PHONE_FAMILIES

SENTENCES_PER_NOTE = (1, 8)


@dataclass
class GenerationStats:
    lines: int = 0
    sentences: int = 0
    negatives: int = 0
    notes: int = 0
    decisions: dict[str, int] = field(default_factory=dict)
    phi_types: dict[str, int] = field(default_factory=dict)
    build_failures: int = 0


class ShardWriter:
    """Writes JSONL shards, rolling over only on sentence boundaries."""

    def __init__(self, out_dir: Path, prefix: str, shard_lines: int):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.prefix = prefix
        self.shard_lines = shard_lines
        self.shard_index = 0
        self.lines_in_shard = 0
        self.total_lines = 0
        self._fh = None
        self.paths: list[Path] = []
        self._open_next()

    def _open_next(self) -> None:
        if self._fh:
            self._fh.close()
        self.shard_index += 1
        path = self.out_dir / f"{self.prefix}-{self.shard_index:05d}.jsonl"
        self._fh = path.open("w", encoding="utf-8")
        self.paths.append(path)
        self.lines_in_shard = 0

    def write_group(self, records: list[dict]) -> None:
        """Write all lines for one sentence_id together.

        Rolling over before the group rather than mid-group is what keeps the
        'no sentence_id spans two shards' invariant true by construction.
        """
        if self.lines_in_shard and self.lines_in_shard + len(records) > self.shard_lines:
            self._open_next()
        for record in records:
            self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.lines_in_shard += len(records)
        self.total_lines += len(records)

    def close(self) -> None:
        if self._fh:
            self._fh.close()
            self._fh = None


class Generator:
    def __init__(self, config: Config, lexicons: Lexicons | None = None):
        self.config = config
        self.lex = lexicons or load_lexicons()
        self.rng = random.Random(config.seed)
        self.next_sentence_id = config.start_sentence_id
        # Group ids are counted separately in id_per_line mode so they never
        # consume a value from the per-line sequence.
        self.next_group_id = 1
        self.stats = GenerationStats()
        self.diversity = DiversityTracker(config.diversity)
        # Tell the tracker which surface forms are curated collisions, so the
        # lexical ceiling can exempt them rather than flagging them at scale.
        self.diversity.note_ambiguous_entries(
            [p.person_form for p in self.lex.person_disease]
            + [p.other_form for p in self.lex.person_disease]
            + [p.person_form for p in self.lex.person_drug]
            + [p.other_form for p in self.lex.person_drug]
            + [p.person_form for p in self.lex.person_place]
            + [p.other_form for p in self.lex.person_place]
            + [e for e, _ in self.lex.eponyms]
            + list(self.lex.role_ambiguous)
        )

    # ------------------------------------------------------- template choice

    def _wanted_decision(self) -> str:
        """Which side of the 55/45 line ratio currently needs feeding."""
        redact = self.stats.decisions.get("REDACT", 0)
        preserve = self.stats.decisions.get("PRESERVE", 0)
        total = redact + preserve
        target = self.config.decision_mix["REDACT"]
        if total == 0:
            return "REDACT"
        return "REDACT" if (redact / total) < target else "PRESERVE"

    def _pick_template(self) -> Template:
        """Choose a template, steering the running REDACT/PRESERVE line ratio.

        The 55/45 target is a ratio over *lines*, but a template emits a whole
        sentence's worth of lines at once, so we steer rather than dictate:
        whichever side is currently under its target gets the next draw.
        """
        redact = self.stats.decisions.get("REDACT", 0)
        preserve = self.stats.decisions.get("PRESERVE", 0)
        total = redact + preserve
        target = self.config.decision_mix["REDACT"]
        want_redact = True if total == 0 else (redact / total) < target
        pool = templates_by_decision("REDACT" if want_redact else "PRESERVE")
        if not pool:
            pool = REGISTRY
        # Weighted draw, damped by how heavily the template has already been used
        # so no single template can exceed its Section 15 share.
        weights = [
            t.weight * self.diversity.template_damping(t.name, self.stats.lines)
            for t in pool
        ]
        if sum(weights) <= 0:
            weights = [t.weight for t in pool]
        return self.rng.choices(pool, weights=weights, k=1)[0]

    def _variant_context(self) -> dict:
        """Pick surface-form families, favouring whichever is furthest behind.

        Section 15 requires each PHONE and EMAIL family to reach 15 percent of
        its type, which a uniform draw would satisfy only on average.
        """
        return {
            "phone_family": self.diversity.neediest_family("PHONE", PHONE_FAMILIES, self.rng),
            "email_family": self.diversity.neediest_family("EMAIL", EMAIL_FAMILIES, self.rng),
        }

    # ------------------------------------------------------------- assembly

    def build_sentence(self, note: NoteContext, sentence_index: int) -> list[dict] | None:
        """Build one sentence and return its JSONL records, or None on failure."""
        ensure_probed(self.lex, self.rng)
        want = self._wanted_decision()
        frame = compose_frame(self.rng, want)
        template_name = frame.name
        builder = SpanBuilder()
        ctx = self._variant_context()
        ctx["region"] = self.rng.choice(("ng", "ke", "rw", "gh", "tz"))
        slots = Slots(self.lex, self.rng, ctx)
        try:
            frame.render(builder, slots, self.rng)
            build = builder.finish()
        except SpanError:
            # A template that produced a structurally invalid sentence is a bug,
            # not data: count it and move on rather than emitting a bad line.
            self.stats.build_failures += 1
            return None

        if not build.spans:
            return None

        # In the schema's default layout one sentence_id covers the whole
        # sentence; in id_per_line mode each emitted line takes the next id and
        # the sentence's id is kept in group_id so the spans can still be grouped.
        # The two counters are separate: sharing one would let a group number
        # consume a line id and leave gaps in the line sequence.
        per_line = self.config.id_per_line
        if per_line:
            group_id = self.next_group_id
            self.next_group_id += 1
        else:
            group_id = self.next_sentence_id
            self.next_sentence_id += 1

        records = []
        for span in build.spans:
            decision = decision_for(span.phi_type)
            if per_line:
                line_id = self.next_sentence_id
                self.next_sentence_id += 1
            else:
                line_id = group_id
            record = {
                "sentence_id": line_id,
                "sentence": build.sentence,
                "span_start": span.span_start,
                "span_end": span.span_end,
                "span": span.span,
                "phi_type": span.phi_type,
                "decision": decision,
                "note_id": note.note_id,
                "patient_id": note.patient_id,
                "sentence_index": sentence_index,
                "source": note.source,
                # The prose is English by construction; `code_switched` is true
                # when the PHI inside it comes from another language, which is
                # how these notes are actually written.
                "language": note.language,
                "code_switched": slots.code_switched(),
                # Sorted so the value is stable for grouping and diffing.
                "phi_languages": sorted(slots.phi_languages),
                "ambiguity_type": span.ambiguity_type,
                "surface_form": span.surface_form,
            }
            if per_line:
                record["group_id"] = group_id
            records.append(record)
            self.stats.decisions[decision] = self.stats.decisions.get(decision, 0) + 1
            self.stats.phi_types[span.phi_type] = self.stats.phi_types.get(span.phi_type, 0) + 1
            self.diversity.record_line(
                template=template_name,
                phi_type=span.phi_type,
                span_text=span.span,
                surface_form=span.surface_form,
            )

        self.diversity.record_sentence(build.sentence)
        self.stats.lines += len(records)
        self.stats.sentences += 1
        return records

    def build_negative(self, note: NoteContext, sentence_index: int) -> dict:
        """Section 13.3: a no-span sentence, carrying only the six listed keys."""
        import unicodedata

        sentence_id = self.next_sentence_id
        self.next_sentence_id += 1
        self.stats.negatives += 1
        record = {
            "sentence_id": sentence_id,
            "sentence": unicodedata.normalize("NFC", negative_sentence(self.rng)),
            "note_id": note.note_id,
            "sentence_index": sentence_index,
            "source": note.source,
            "language": note.language,
        }
        if self.config.id_per_line:
            record["group_id"] = self.next_group_id
            self.next_group_id += 1
        return record

    # ----------------------------------------------------------------- drive

    def run(self, out_dir: Path | str | None = None) -> GenerationStats:
        out = Path(out_dir or self.config.out_dir)
        positives = ShardWriter(out, "part", self.config.shard_lines)
        negatives = ShardWriter(out, "negatives", self.config.shard_lines)

        try:
            while self.stats.lines < self.config.target_lines:
                note = make_note_context(
                    self.rng, self.config.language_mix, self.config.source
                )
                self.stats.notes += 1
                n_sentences = self.rng.randrange(*SENTENCES_PER_NOTE)
                for sentence_index in range(n_sentences):
                    if self.stats.lines >= self.config.target_lines:
                        break
                    if self.rng.random() < self.config.negatives_ratio:
                        negatives.write_group([self.build_negative(note, sentence_index)])
                        continue
                    records = self.build_sentence(note, sentence_index)
                    if records:
                        positives.write_group(records)
        finally:
            positives.close()
            negatives.close()

        self.stats_paths = {"positives": positives.paths, "negatives": negatives.paths}
        return self.stats


def generate(config: Config, out_dir: Path | str | None = None) -> Generator:
    gen = Generator(config)
    gen.run(out_dir)
    return gen
