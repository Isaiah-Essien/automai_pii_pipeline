"""Tests for composed-frame grammar and per-sentence coherence.

These lock in defects that were found by reading generated output: a clause
following an opening that left no subject, a doubled terminator, two different
ages in one sentence.  Each is cheap to reintroduce while editing parts, so each
gets a test rather than a comment.
"""

import json
import random
import re

import pytest

from phigen.config import Config
from phigen.frames import (
    AMBIGUITY_CLAUSES,
    CLAUSES,
    OPENINGS,
    SINGLETON_TYPES,
    Slots,
    compose_frame,
    count_possible_frames,
    ensure_probed,
)
from phigen.generate import Generator
from phigen.lexicons import load_lexicons
from phigen.spans import SpanBuilder


@pytest.fixture(scope="module")
def lex():
    return load_lexicons()


@pytest.fixture(scope="module")
def corpus(tmp_path_factory):
    """One shared build, read back as sentence groups."""
    out = tmp_path_factory.mktemp("frames")
    Generator(Config(target_lines=6000, seed=17, out_dir=str(out))).run(out)
    groups: dict[int, list[dict]] = {}
    for shard in sorted(out.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            r = json.loads(line)
            groups.setdefault(r["sentence_id"], []).append(r)
    assert groups
    return groups


def sentences(corpus):
    return [g[0]["sentence"] for g in corpus.values()]


def test_frame_space_is_large_enough_for_the_ceiling(lex):
    """Section 15 needs ~200 frames per phi_type; we should far exceed that."""
    assert count_possible_frames()["total_frames"] > 100_000


def test_every_type_has_several_clauses():
    """A type with one clause makes every frame using it dominate that type."""
    counts: dict[str, int] = {}
    for c in CLAUSES:
        for t in c.phi_types:
            counts[t] = counts.get(t, 0) + 1
    thin = {t: n for t, n in counts.items() if n < 4}
    assert not thin, f"types with too few clauses: {thin}"


def test_no_doubled_terminator(corpus):
    for s in sentences(corpus):
        assert ",." not in s and ",;" not in s and ".." not in s, s
        assert ";." not in s and " ." not in s, s


def test_no_missing_separator_between_clauses(corpus):
    """A lowercase word must never butt directly against a capitalised one."""
    for s in sentences(corpus):
        assert not re.search(r"[a-z][A-Z]", s), s


def test_sentence_ends_with_terminator(corpus):
    for s in sentences(corpus):
        assert s.rstrip()[-1] in ".!?", s


def test_no_verb_clause_after_predicate_opening(corpus):
    """"I am referring X to your unit and was treated" is the failure mode."""
    for s in sentences(corpus):
        for stem in ("to your unit", "Thank you for reviewing", "Kindly attend to"):
            idx = s.find(stem)
            if idx >= 0:
                rest = s[idx + len(stem) :]
                assert not rest.startswith(" and was"), s


def test_no_two_ages_in_one_sentence(corpus):
    """A sentence stating two different ages is incoherent."""
    for records in corpus.values():
        ages = [r["span"] for r in records if r["phi_type"] == "AGE"]
        assert len(ages) <= 1, ages


def test_singleton_types_appear_at_most_once(corpus):
    for records in corpus.values():
        for t in SINGLETON_TYPES:
            spans = [r for r in records if r["phi_type"] == t]
            assert len(spans) <= 1, (t, [r["span"] for r in spans])


def test_no_copula_age_mismatch(corpus):
    """"the stated age is aged 56" -- the clause already supplies the verb."""
    for s in sentences(corpus):
        assert "age is aged" not in s, s
        assert "records aged" not in s, s
        assert "Age: aged" not in s, s


def test_person_place_collision_is_not_a_bare_repeat(corpus):
    """The shared token should recur, but not as the identical whole span."""
    for records in corpus.values():
        people = {r["span"] for r in records if r["phi_type"] == "PERSON"}
        places = {r["span"] for r in records if r["phi_type"] == "LOCATION"}
        assert not (people & places), people & places


def test_offsets_hold_across_composed_frames(corpus):
    for records in corpus.values():
        for r in records:
            assert r["sentence"][r["span_start"] : r["span_end"]] == r["span"]


def test_every_register_is_reachable():
    rng = random.Random(0)
    seen = {compose_frame(rng).register for _ in range(2000)}
    from phigen.frames import REGISTERS

    assert seen == set(REGISTERS)


def test_every_part_renders_without_error(lex):
    """Each opening and clause must build cleanly in isolation."""
    rng = random.Random(1)
    ensure_probed(lex, rng)
    for part in OPENINGS + CLAUSES + AMBIGUITY_CLAUSES:
        b = SpanBuilder()
        slots = Slots(lex, rng, {"region": "ng"})
        part.fn(b, slots, rng)
        b.literal(".")
        build = b.finish()
        for sp in build.spans:
            assert build.sentence[sp.span_start : sp.span_end] == sp.span


def test_no_space_before_punctuation(corpus):
    """A clause seam must not leave " ;" or " ," behind."""
    for s in sentences(corpus):
        for bad in (" ;", " ,", " .", " :"):
            assert bad not in s, (bad, s)


def test_drop_last_char_refuses_to_touch_a_span():
    """Deleting inside a recorded span would silently break its offsets."""
    from phigen.spans import SpanBuilder, SpanError

    b = SpanBuilder()
    b.literal("Patient ")
    b.span("Amara Bello", "PERSON")
    with pytest.raises(SpanError, match="refusing to delete"):
        b.drop_last_char()


def test_drop_last_char_removes_literal_punctuation():
    from phigen.spans import SpanBuilder

    b = SpanBuilder()
    b.literal("Patient ")
    b.span("Amara Bello", "PERSON")
    b.literal(",")
    b.drop_last_char()
    b.literal("; reviewed.")
    build = b.finish()
    assert build.sentence == "Patient Amara Bello; reviewed."
    assert build.sentence[build.spans[0].span_start : build.spans[0].span_end] == "Amara Bello"
