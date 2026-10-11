"""Tests that each Section 14 check actually catches its failure mode."""

import json
from pathlib import Path

from phigen.validate import validate_build

BASE = {
    "sentence_id": 1,
    "sentence": "Patient Amara Bello was admitted.",
    "span_start": 8,
    "span_end": 19,
    "span": "Amara Bello",
    "phi_type": "PERSON",
    "decision": "REDACT",
    "note_id": "note_1",
    "patient_id": "pt_1",
    "sentence_index": 0,
    "source": "synthetic",
    "language": "en",
    "code_switched": False,
    "ambiguity_type": "none",
    "surface_form": "standard",
    "phi_languages": [],
}


def write_build(tmp_path: Path, records: list[dict], negatives: list[dict] | None = None) -> Path:
    out = tmp_path / "out"
    out.mkdir()
    with (out / "part-00001.jsonl").open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    with (out / "negatives-00001.jsonl").open("w", encoding="utf-8") as fh:
        for r in negatives or []:
            fh.write(json.dumps(r) + "\n")
    return out


def checks_failed(report) -> set[str]:
    return {f.check for f in report.failures}


def test_clean_build_passes(tmp_path):
    report = validate_build(write_build(tmp_path, [dict(BASE)]))
    assert report.passed, [f.reason for f in report.failures]


def test_offset_mismatch_is_caught_and_quarantined(tmp_path):
    bad = dict(BASE, span="Amara Bell")
    out = write_build(tmp_path, [bad])
    report = validate_build(out)
    assert "offset_consistency" in checks_failed(report)
    quarantine = out / "quarantine.jsonl"
    assert quarantine.exists()
    entry = json.loads(quarantine.read_text().splitlines()[0])
    assert entry["check"] == "offset_consistency"
    assert entry["record"]["span"] == "Amara Bell"


def test_bounds_violation_is_caught(tmp_path):
    report = validate_build(write_build(tmp_path, [dict(BASE, span_end=999)]))
    assert "bounds" in checks_failed(report)


def test_missing_required_key_is_caught(tmp_path):
    bad = dict(BASE)
    del bad["decision"]
    report = validate_build(write_build(tmp_path, [bad]))
    assert "parse" in checks_failed(report)


def test_unknown_phi_type_is_caught(tmp_path):
    report = validate_build(write_build(tmp_path, [dict(BASE, phi_type="MOOD")]))
    assert "type_membership" in checks_failed(report)


def test_age_redacted_is_caught(tmp_path):
    """AGE is a Section 5 type, so REDACT on it must fail decision consistency."""
    bad = dict(BASE, span_start=0, span_end=7, span="Patient", phi_type="AGE", decision="REDACT")
    report = validate_build(write_build(tmp_path, [bad]))
    assert "decision_consistency" in checks_failed(report)


def test_sentence_identity_across_group_is_caught(tmp_path):
    a = dict(BASE)
    b = dict(BASE, span_start=0, span_end=7, span="Patient", phi_type="DATE",
             sentence="Patient Amara Bello was admitted today.")
    report = validate_build(write_build(tmp_path, [a, b]))
    assert "sentence_identity" in checks_failed(report)


def test_ordering_violation_is_caught(tmp_path):
    first = dict(BASE)
    second = dict(BASE, span_start=0, span_end=7, span="Patient", phi_type="DATE")
    report = validate_build(write_build(tmp_path, [first, second]))  # descending
    assert "ordering" in checks_failed(report)


def test_same_type_overlap_is_caught(tmp_path):
    a = dict(BASE, span_start=0, span_end=13, span="Patient Amara")
    b = dict(BASE, span_start=8, span_end=19, span="Amara Bello")
    report = validate_build(write_build(tmp_path, [a, b]))
    assert "overlap_policy" in checks_failed(report)


def test_partial_cross_type_overlap_is_caught(tmp_path):
    a = dict(BASE, span_start=0, span_end=13, span="Patient Amara", phi_type="PERSON")
    b = dict(BASE, span_start=8, span_end=19, span="Amara Bello", phi_type="DRUG",
             decision="PRESERVE")
    report = validate_build(write_build(tmp_path, [a, b]))
    assert "overlap_policy" in checks_failed(report)


def test_containment_cross_type_is_allowed(tmp_path):
    sentence = "Nurse Amoxicillin Adeyemi documented the dose."
    outer = dict(BASE, sentence=sentence, span_start=6, span_end=25,
                 span="Amoxicillin Adeyemi", phi_type="PERSON", decision="REDACT")
    inner = dict(BASE, sentence=sentence, span_start=6, span_end=17,
                 span="Amoxicillin", phi_type="DRUG", decision="PRESERVE")
    report = validate_build(write_build(tmp_path, [inner, outer]))
    assert report.passed, [f.reason for f in report.failures]


def test_duplicate_span_offsets_are_caught(tmp_path):
    a = dict(BASE)
    b = dict(BASE, phi_type="DRUG", decision="PRESERVE")
    report = validate_build(write_build(tmp_path, [a, b]))
    assert "duplicate_spans" in checks_failed(report)


def test_identifier_gap_is_caught(tmp_path):
    a = dict(BASE, sentence_id=1)
    b = dict(BASE, sentence_id=5)
    report = validate_build(write_build(tmp_path, [a, b]))
    assert "identifier_sequence" in checks_failed(report)


def test_shard_integrity_is_caught(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "part-00001.jsonl").write_text(json.dumps(BASE) + "\n")
    other = dict(BASE, span_start=0, span_end=7, span="Patient", phi_type="DATE")
    (out / "part-00002.jsonl").write_text(json.dumps(other) + "\n")
    (out / "negatives-00001.jsonl").write_text("")
    report = validate_build(out)
    assert "shard_integrity" in checks_failed(report)


def test_split_integrity_is_caught(tmp_path):
    a = dict(BASE, sentence_id=1, note_id="note_1", patient_id="pt_1")
    b = dict(BASE, sentence_id=2, note_id="note_1", patient_id="pt_2")
    report = validate_build(write_build(tmp_path, [a, b]))
    assert "split_integrity" in checks_failed(report)


def test_newline_in_sentence_is_caught(tmp_path):
    bad = dict(BASE, sentence="Patient Amara Bello was\nadmitted.")
    report = validate_build(write_build(tmp_path, [bad]))
    assert "no_literal_newline" in checks_failed(report)


def test_code_switched_must_agree_with_phi_languages(tmp_path):
    """A sentence with non-English PHI must report code_switched."""
    bad = dict(BASE, phi_languages=["ig", "yo"], code_switched=False)
    report = validate_build(write_build(tmp_path, [bad]))
    assert "parse" in checks_failed(report)


def test_unsorted_phi_languages_is_caught(tmp_path):
    bad = dict(BASE, phi_languages=["yo", "ig"], code_switched=True)
    report = validate_build(write_build(tmp_path, [bad]))
    assert "parse" in checks_failed(report)


def test_unknown_phi_language_is_caught(tmp_path):
    bad = dict(BASE, phi_languages=["xx"], code_switched=True)
    report = validate_build(write_build(tmp_path, [bad]))
    assert "parse" in checks_failed(report)


def test_valid_code_switched_line_passes(tmp_path):
    good = dict(BASE, phi_languages=["ig", "yo"], code_switched=True)
    report = validate_build(write_build(tmp_path, [good]))
    assert report.passed, [f.reason for f in report.failures]


def test_negative_with_extra_field_is_caught(tmp_path):
    """Section 13.3 fixes the negative record to exactly six keys."""
    negative = {
        "sentence_id": 2,
        "sentence": "The ward round was completed.",
        "note_id": "note_1",
        "sentence_index": 1,
        "source": "synthetic",
        "language": "en",
        "phi_type": "NONE",  # not permitted
    }
    report = validate_build(write_build(tmp_path, [dict(BASE)], [negative]))
    assert "parse" in checks_failed(report)


def test_valid_negative_passes(tmp_path):
    negative = {
        "sentence_id": 2,
        "sentence": "The ward round was completed.",
        "note_id": "note_1",
        "sentence_index": 1,
        "source": "synthetic",
        "language": "en",
    }
    report = validate_build(write_build(tmp_path, [dict(BASE)], [negative]))
    assert report.passed, [f.reason for f in report.failures]


def test_malformed_json_is_quarantined(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "part-00001.jsonl").write_text(json.dumps(BASE) + "\n{not json\n")
    (out / "negatives-00001.jsonl").write_text("")
    report = validate_build(out)
    assert "parse" in checks_failed(report)
    assert (out / "quarantine.jsonl").exists()
