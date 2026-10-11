"""End-to-end: generate a small corpus and assert it validates cleanly."""

import json

from phigen.config import Config, DiversityConfig
from phigen.generate import Generator
from phigen.schema import METADATA_FIELDS, NEGATIVE_FIELDS, REQUIRED_FIELDS, decision_for
from phigen.validate import validate_build


def small_config(**overrides) -> Config:
    base = dict(target_lines=400, seed=99, shard_lines=120, out_dir="out")
    base.update(overrides)
    return Config(**base)


def test_small_build_validates_clean(tmp_path):
    gen = Generator(small_config())
    stats = gen.run(tmp_path)
    report = validate_build(tmp_path)
    assert stats.lines >= 400
    assert report.passed, [f.reason for f in report.failures[:5]]
    assert stats.build_failures == 0


def test_every_line_has_exactly_the_required_and_metadata_fields(tmp_path):
    Generator(small_config()).run(tmp_path)
    expected = set(REQUIRED_FIELDS) | set(METADATA_FIELDS)
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            assert set(json.loads(line)) == expected


def test_offsets_hold_on_every_generated_line(tmp_path):
    Generator(small_config()).run(tmp_path)
    checked = 0
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            r = json.loads(line)
            assert r["sentence"][r["span_start"] : r["span_end"]] == r["span"]
            checked += 1
    assert checked > 0


def test_decision_always_follows_phi_type(tmp_path):
    Generator(small_config()).run(tmp_path)
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            r = json.loads(line)
            assert r["decision"] == decision_for(r["phi_type"])


def test_age_is_never_redacted(tmp_path):
    Generator(small_config(target_lines=2000)).run(tmp_path)
    seen_age = False
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            r = json.loads(line)
            if r["phi_type"] == "AGE":
                seen_age = True
                assert r["decision"] == "PRESERVE"
    assert seen_age, "no AGE spans generated, so the guarantee is untested"


def test_negatives_carry_only_the_six_permitted_keys(tmp_path):
    Generator(small_config()).run(tmp_path)
    count = 0
    for shard in sorted(tmp_path.glob("negatives-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            assert set(json.loads(line)) == set(NEGATIVE_FIELDS)
            count += 1
    assert count > 0


def test_sentence_id_never_spans_two_shards(tmp_path):
    Generator(small_config(shard_lines=50)).run(tmp_path)
    shards = sorted(tmp_path.glob("part-*.jsonl"))
    assert len(shards) > 1, "test needs multiple shards to be meaningful"
    seen: dict[int, str] = {}
    for shard in shards:
        for line in shard.open(encoding="utf-8"):
            sid = json.loads(line)["sentence_id"]
            assert seen.setdefault(sid, shard.name) == shard.name


def test_sentence_ids_are_consecutive_from_one_across_both_files(tmp_path):
    Generator(small_config()).run(tmp_path)
    ids = set()
    for pattern in ("part-*.jsonl", "negatives-*.jsonl"):
        for shard in sorted(tmp_path.glob(pattern)):
            for line in shard.open(encoding="utf-8"):
                sid = json.loads(line)["sentence_id"]
                ids.add(sid)
    assert sorted(ids) == list(range(1, max(ids) + 1))


def test_group_lines_share_identical_sentence_text(tmp_path):
    Generator(small_config()).run(tmp_path)
    by_id: dict[int, set[str]] = {}
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            r = json.loads(line)
            by_id.setdefault(r["sentence_id"], set()).add(r["sentence"])
    assert all(len(v) == 1 for v in by_id.values())


def test_patient_id_is_not_derived_from_anything(tmp_path):
    """Distinct notes must not collide, and ids must not be enumerable."""
    Generator(small_config()).run(tmp_path)
    ids = set()
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            pid = json.loads(line)["patient_id"]
            assert pid.startswith("pt_") and len(pid) == 35
            ids.add(pid)
    assert len(ids) > 1


def test_generation_is_deterministic_for_a_fixed_seed(tmp_path):
    """Sentence content is reproducible; only the pseudonymous ids differ."""
    a, b = tmp_path / "a", tmp_path / "b"
    Generator(small_config(seed=4242)).run(a)
    Generator(small_config(seed=4242)).run(b)

    def sentences(root):
        out = []
        for shard in sorted(root.glob("part-*.jsonl")):
            for line in shard.open(encoding="utf-8"):
                r = json.loads(line)
                out.append((r["sentence_id"], r["span_start"], r["span_end"], r["phi_type"]))
        return out

    assert sentences(a) == sentences(b)


def test_prose_language_is_always_english(tmp_path):
    """The corpus is English prose; only the PHI inside it varies by language."""
    Generator(small_config()).run(tmp_path)
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            assert json.loads(line)["language"] == "en"


def test_code_switched_reflects_actual_phi_languages(tmp_path):
    Generator(small_config(target_lines=2000)).run(tmp_path)
    seen_switched = False
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            r = json.loads(line)
            expected = any(l != "en" for l in r["phi_languages"])
            assert r["code_switched"] == expected
            seen_switched |= expected
    assert seen_switched, "no code-switched sentence was generated"


def test_african_language_phi_is_present(tmp_path):
    """PHI should draw on several African languages, not just English names."""
    Generator(small_config(target_lines=3000)).run(tmp_path)
    langs: set[str] = set()
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            langs.update(json.loads(line)["phi_languages"])
    assert len(langs - {"en"}) >= 6, langs


def test_nested_containment_appears_in_a_real_build(tmp_path):
    """The Section 13.2 canonical case must actually occur in output."""
    Generator(small_config(target_lines=3000)).run(tmp_path)
    by_id: dict[int, list[dict]] = {}
    for shard in sorted(tmp_path.glob("part-*.jsonl")):
        for line in shard.open(encoding="utf-8"):
            r = json.loads(line)
            by_id.setdefault(r["sentence_id"], []).append(r)
    def contains(outer, inner):
        return outer["span_start"] <= inner["span_start"] and inner["span_end"] <= outer["span_end"]

    found = False
    for records in by_id.values():
        for i, a in enumerate(records):
            for b in records[i + 1 :]:
                # Ordering writes the shorter span first, so the container may be
                # either side of the pair.
                if a["phi_type"] != b["phi_type"] and (contains(a, b) or contains(b, a)):
                    found = True
    assert found, "no nested containment case was generated"


def test_build_can_continue_an_existing_corpus(tmp_path):
    """A second pass starts at the given id instead of restarting at 1.

    Extending a corpus in several passes must keep sentence_id globally
    consecutive with no duplicates (§14.2), so the later pass begins one past
    the highest id the earlier pass reached.
    """
    start = 11_177_505
    Generator(small_config(start_sentence_id=start)).run(tmp_path)
    ids = set()
    for pattern in ("part-*.jsonl", "negatives-*.jsonl"):
        for shard in sorted(tmp_path.glob(pattern)):
            for line in shard.open(encoding="utf-8"):
                ids.add(json.loads(line)["sentence_id"])
    assert min(ids) == start
    assert sorted(ids) == list(range(start, max(ids) + 1))


def test_continuation_build_validates_against_its_own_start(tmp_path):
    """Validation must not report the earlier passes' ids as gaps."""
    start = 500_001
    Generator(small_config(start_sentence_id=start)).run(tmp_path)

    good = validate_build(tmp_path, start_sentence_id=start)
    assert good.passed, [f.reason for f in good.failures[:5]]

    # Checking the same build against 1 should flag the sequence.
    bad = validate_build(tmp_path, start_sentence_id=1)
    assert any(f.check == "identifier_sequence" for f in bad.failures)


def test_different_seeds_produce_different_sentences(tmp_path):
    """A new pass needs a new seed; the id offset alone does not diversify."""
    a, b = tmp_path / "a", tmp_path / "b"
    Generator(small_config(seed=1111, start_sentence_id=1)).run(a)
    Generator(small_config(seed=2222, start_sentence_id=1)).run(b)

    def sentences(root):
        out = set()
        for shard in sorted(root.glob("part-*.jsonl")):
            for line in shard.open(encoding="utf-8"):
                out.add(json.loads(line)["sentence"])
        return out

    sa, sb = sentences(a), sentences(b)
    overlap = len(sa & sb) / len(sa)
    assert overlap < 0.10, f"seeds produced {overlap:.0%} identical sentences"
