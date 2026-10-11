"""Tests for offset-by-construction assembly and the overlap policy."""

import unicodedata

import pytest

from phigen.spans import (
    Span,
    SpanBuilder,
    SpanError,
    check_overlap_policy,
    order_spans,
    verify_spans,
)


def test_offsets_match_by_construction():
    b = SpanBuilder()
    b.literal("Patient ")
    b.span("Chioma Nwankwo", "PERSON")
    b.literal(" was admitted on ")
    b.span("14/03/2019", "DATE")
    b.literal(".")
    build = b.finish()

    assert build.sentence == "Patient Chioma Nwankwo was admitted on 14/03/2019."
    for s in build.spans:
        assert build.sentence[s.span_start : s.span_end] == s.span


def test_offsets_survive_diacritics_under_nfc():
    # "Adeyemi" with a combining acute on the e, supplied in decomposed form.
    decomposed = "Ade" + "́" + "yemi"
    b = SpanBuilder()
    b.literal("Nurse ")
    b.span(decomposed, "PERSON")
    b.literal(" signed off.")
    build = b.finish()

    assert build.sentence == unicodedata.normalize("NFC", build.sentence)
    s = build.spans[0]
    # NFC composed the e+acute into one code point, so the recorded end reflects
    # the composed length rather than the decomposed one.
    assert len(s.span) == len("Adeyemi")
    assert build.sentence[s.span_start : s.span_end] == s.span


def test_multi_span_sentence_is_ordered_ascending():
    b = SpanBuilder()
    b.literal("Patient ")
    b.span("Amara Bello", "PERSON")
    b.literal(", NIN ")
    b.span("28473910265", "NATIONAL_ID")
    b.literal(", called ")
    b.span("+234 803 221 4490", "PHONE")
    b.literal(".")
    build = b.finish()

    starts = [s.span_start for s in build.spans]
    assert starts == sorted(starts)


def test_nested_containment_emits_both_spans():
    b = SpanBuilder()
    b.literal("Staff nurse ")
    outer, inner = b.nested("Amoxicillin Adeyemi", "PERSON", "Amoxicillin", "DRUG")
    b.literal(" documented the dose.")
    build = b.finish()

    assert outer.contains(inner)
    assert build.sentence[inner.span_start : inner.span_end] == "Amoxicillin"
    assert build.sentence[outer.span_start : outer.span_end] == "Amoxicillin Adeyemi"
    # Ordering puts the shorter span first when starts tie.
    assert [s.phi_type for s in build.spans] == ["DRUG", "PERSON"]


def test_tie_on_start_orders_shorter_span_first():
    spans = [
        Span(0, 19, "Amoxicillin Adeyemi", "PERSON"),
        Span(0, 11, "Amoxicillin", "DRUG"),
    ]
    assert [s.phi_type for s in order_spans(spans)] == ["DRUG", "PERSON"]


def test_same_type_overlap_is_rejected():
    spans = order_spans(
        [Span(0, 10, "aaaaaaaaaa", "PERSON"), Span(5, 15, "bbbbbbbbbb", "PERSON")]
    )
    with pytest.raises(SpanError, match="same-type overlap"):
        check_overlap_policy(spans)


def test_partial_cross_type_overlap_is_rejected():
    spans = order_spans(
        [Span(0, 10, "aaaaaaaaaa", "PERSON"), Span(5, 15, "bbbbbbbbbb", "DRUG")]
    )
    with pytest.raises(SpanError, match="partial overlap"):
        check_overlap_policy(spans)


def test_cross_type_containment_is_allowed():
    spans = order_spans(
        [Span(0, 19, "x" * 19, "PERSON"), Span(0, 11, "x" * 11, "DRUG")]
    )
    check_overlap_policy(spans)  # must not raise


def test_adjacent_spans_do_not_count_as_overlap():
    spans = order_spans([Span(0, 5, "aaaaa", "PERSON"), Span(5, 10, "bbbbb", "PERSON")])
    check_overlap_policy(spans)  # touching endpoints are disjoint


def test_whitespace_only_span_is_rejected():
    b = SpanBuilder()
    b.literal("x")
    with pytest.raises(SpanError, match="non-whitespace"):
        b.span("   ", "PERSON")


def test_out_of_bounds_span_is_rejected():
    with pytest.raises(SpanError, match="bounds violated"):
        verify_spans("short", [Span(0, 99, "short", "PERSON")])


def test_offset_mismatch_is_rejected():
    with pytest.raises(SpanError, match="offset mismatch"):
        verify_spans("Patient Amara", [Span(0, 7, "Amara", "PERSON")])


def test_duplicate_offsets_are_rejected():
    spans = [Span(0, 5, "Amara", "PERSON"), Span(0, 5, "Amara", "DRUG")]
    with pytest.raises(SpanError, match="duplicate span offsets"):
        verify_spans("Amara went home", spans)


def test_newline_in_sentence_is_rejected():
    b = SpanBuilder()
    b.literal("line one\nline two")
    with pytest.raises(SpanError, match="newline"):
        b.finish()


def test_nested_requires_inner_inside_outer():
    b = SpanBuilder()
    with pytest.raises(SpanError, match="does not occur"):
        b.nested("Amara Bello", "PERSON", "Chioma", "DRUG")


def test_inner_span_not_at_outer_start():
    b = SpanBuilder()
    b.literal("Dr ")
    outer, inner = b.nested("Grace Malaria", "PERSON", "Malaria", "DISEASE")
    build = b.finish()
    assert build.sentence[inner.span_start : inner.span_end] == "Malaria"
    assert outer.contains(inner)
    # Distinct starts, so ordering is by start: outer first here.
    assert [s.phi_type for s in build.spans] == ["PERSON", "DISEASE"]
