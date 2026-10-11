# phigen — synthetic PHI-detection corpus generator

Config-driven Python pipeline that emits JSONL conforming to
`AutomAI-RL-Schema.pdf`. No LLM is involved: sentences are assembled from typed
frame parts and lexicons, and every offset is computed by construction.

The corpus is **English clinical prose carrying African-language PHI** — which is
how notes are actually written across the region. Names and places are drawn from
Igbo, Yoruba, Hausa, Swahili, Kinyarwanda, Kikuyu, Zulu, Chichewa, Akan, Fula,
Luganda, Acholi and Dagbani lexicons, and `code_switched` is computed from the
languages a sentence's spans actually use rather than sampled from a rate.

## Quick start

```bash
python3 scripts_build_lexicons.py                              # build data/lexicons/* (once)
python3 -m phigen build --config config/default.json --out out # 1,000-line smoke build
python3 -m pytest tests/ -q                                    # 88 tests
```

Scale up with `--target-lines`:

```bash
python3 -m phigen build --config config/full.json --target-lines 20000000 --out out
```

## Output

| File | Contents |
| --- | --- |
| `out/part-NNNNN.jsonl` | span lines: 7 required fields + 9 metadata fields |
| `out/negatives-NNNNN.jsonl` | no-span sentences, exactly the 6 keys of §13.3 |
| `out/quarantine.jsonl` | failed lines with their reason (absent when clean) |
| `out/reports/*.json` | validation, diversity, and generation reports |

One line per **span**, not per sentence (§7). A sentence with four spans produces
four lines sharing one `sentence_id` and identical sentence text.

### Negative sentences

`negatives-*.jsonl` holds sentences containing no PHI at all. They exist so
Stage 1 sees realistic quantities of clean text and does not over-predict
candidates: a model trained only on sentences that contain PHI never learns that
"nothing here" is a valid answer. They share the same `sentence_id` sequence, so
ids interleave between the two files and are gapless across their union.

`negatives_ratio` defaults to 0.30. Real notes are considerably more than 30%
PHI-free, so raise this first if Stage 1 over-predicts in evaluation.

## Modules

- `spans.py` — `SpanBuilder`: offsets recorded as fragments are placed, NFC at
  write time, §13.1 ordering, §13.2 overlap policy. The highest-risk logic; all
  of it is unit-tested including the rejection paths.
- `schema.py` — §4/§5 type lists; `decision_for()` derives the decision from the
  type, so a template cannot emit AGE as REDACT.
- `lexicons.py` — loaders plus a least-recently-used sampler that damps lexical
  concentration; language-tagged name and place pools.
- `variants.py` — PHONE (standard/local/spoken/mixed) and EMAIL
  (standard/spoken/mixed/local) surface forms, plus DATE, NIN, MRN, ADDRESS, AGE.
- `frames.py` — 275 composable parts (83 openings, 132 clauses, 18 ambiguity
  clauses, 28 connectives, 14 tails) across five registers, composing into
  ~17.7M distinct frames. Parts carry a grammatical `continuation` tag so a
  verb-initial clause never follows an opening that has no dangling subject.
- `templates.py` — the original 23 whole-sentence templates, kept for reference
  and for the negative-sentence frames.
- `generate.py` — sentence_id counter, decision-mix steering, shard writers that
  roll over only on sentence boundaries.
- `validate.py` — every §14 check; failures are quarantined with a reason.
- `diversity.py` — §15 floors, enforced during generation and reported after.
- `load_turso.py` — resumable bulk loader for libsql/Turso (see below).
- `renumber.py` — rewrites a built corpus so every line carries its own
  consecutive id, moving the sentence's id to `group_id`. Streams shard by
  shard, so memory stays flat regardless of corpus size.

### Registers

Real clinical text is not uniform prose, and a model trained on one shape fails
on the others. Frames compose across five:

| Register | Example shape |
| --- | --- |
| `narrative` | `Patient X presented at the outpatient department…` |
| `telegraphic` | `Pt X; R/O malaria, contact 0803…` |
| `structured` | `Name: X \| Age: 47 \| MRN: KNH-2024-88341` |
| `handover` | `Bed 13: X; awaiting review…` |
| `letter` | `I am referring X to your unit…` |

## Design notes

**Offsets are never searched for.** A frame part places literal text and spans
through the builder; the builder returns the offsets. Nothing regex-matches the
finished sentence. `sentence[span_start:span_end] == span` is asserted at build
time, again in validation, and again in the tests.

**NFC before offsets.** Each fragment is normalised as it is appended and the
join is asserted NFC-stable. A name like `Lérato` occupies 6 code points, not 7,
and every downstream offset reflects that.

**`ambiguity_type` never drives generation.** It labels a frame that was already
chosen for other reasons. It is reporting metadata only, and §12.1 requires it be
withheld from both models.

**`patient_id` has nothing to invert.** It is drawn from the OS CSPRNG with no
input, so it is not a hash of a hospital identifier and is not enumerable.

**`code_switched` is derived, not sampled.** Each span records the language of
the lexicon it came from in `phi_languages`; a sentence is code-switched exactly
when one of those is not `en`. Validation rejects any line whose `code_switched`
disagrees with its `phi_languages`, so the flag cannot drift from the content.

**Section 15 floors and scale.** A share-based ceiling is only satisfiable above
a certain volume: an entry appearing once is `1/N` of its type, so the 0.1%
lexical ceiling needs ≥1,000 lines per type, and the 0.5% template ceiling needs
both ≥200 distinct templates and ≥200 lines of that type. Below those thresholds
the report lists the floor under `not_yet_applicable` rather than as a violation,
so a genuine concentration fault at scale is not buried under arithmetic that was
never satisfiable.

**Closed vocabularies are exempt from the lexical ceiling, deliberately.** There
are ~95 human ages, ~78 body parts, and a few hundred real person/disease name
collisions worldwide. No sampler can push a single entry of such a type below
0.1%, and padding these lists with invented entries would teach the model a false
distribution — the hard cases *should* recur, since recurrence is what makes them
learnable. `lexical_ceiling_exempt_types` names the exempt types and the report
records the count and rationale under `exempt_from_lexical_ceiling`.

## Loading into Turso / libsql

```bash
export TURSO_AUTH_TOKEN='...'          # never hardcode; the loader reads the env
export TURSO_DATABASE_URL='libsql://<db>.turso.io'
python3 -m phigen.load_turso --out out --pattern 'part-*.jsonl' --workers 8
python3 -m phigen.load_turso --indexes-only --create-indexes    # after the load
```

The loader is **resumable**: progress is recorded per shard in a `_load_state`
table inside the target database, and inserts are `INSERT OR IGNORE` against a
`(sentence_id, span_start, span_end)` primary key. An interrupted transfer
continues from the last committed shard without duplicating rows. Failed batches
retry with exponential backoff.

Indexes are created only with `--create-indexes`, after the bulk load —
maintaining them during a 20M-row insert costs more than building them once.

Measured throughput against `aws-ap-northeast-1`: 235 rows/s single-connection,
~1,400 rows/s at 8 workers, slower at 16 (the server is the bottleneck). Budget
roughly 4 hours for 20M rows, and check your storage plan first — 20M rows of
this corpus is ~12 GB.

## Building a corpus in several passes

A corpus can be extended without restarting the id sequence. `start_sentence_id`
sets the first id a pass emits, so a later pass continues from one past the
highest id the previous pass reached and the union stays consecutive with no
duplicates (§14.2). Validation takes the same value, otherwise it reports every
id in the earlier passes as a gap.

**Each pass needs a new `seed`.** Reusing a seed reproduces that pass's sentences
even when the ids differ — measured at 7% identical sentences with the same seed
versus 0% with a fresh one.

```bash
python3 -m phigen build --config config/full3.json \
    --start-sentence-id 46707708 --id-per-line --out /path/to/out3
```

### One id per line

`--id-per-line` (or `"id_per_line": true`) gives every emitted line its own
consecutive `sentence_id` and moves the sentence's id to `group_id`. The default
layout is the schema's (§7): one `sentence_id` shared across a sentence's spans.

Grouping has to survive the change. Stage 1 NER trains on a sentence and all its
spans as a single example, and four of the §14.2 checks — sentence identity,
ordering, overlap policy, duplicate spans — are defined over the lines sharing a
sentence. In per-line mode those checks key on `group_id` instead, and the
id-sequence and shard checks continue to follow `sentence_id`.

`renumber.py` applies the same transformation to a corpus that was already built
in the default layout.

## Verified results

**500,000-line build**: 77,036 distinct frames, zero validation failures, zero
diversity violations, mix exactly 55.00/45.00 REDACT/PRESERVE, ~14,500 lines/s.

**Three-pass corpus**, one continuous id sequence 1…235,992,587:

| Pass | Config | Sentences | Lines |
| --- | --- | ---: | ---: |
| 1 | `full.json` | 11,177,504 | 23,353,273 |
| 2 | `full2.json` | 11,178,486 | 23,354,434 |
| 3 | `full3.json` | 90,217,119 | 189,284,880 |
| **Total** | | **112,573,109** | **235,992,587** |

125 GB across 811 positive and 137 negative shards. Passes 1 and 2 were built in
the default layout and renumbered afterwards; pass 3 used `--id-per-line`
directly. Pass 3 also used the expanded 275-part frame library, so its structural
diversity is higher than the first two passes.

Ids and offsets are verified across passes 1 and 2 — zero out-of-sequence ids and
zero offset mismatches over all 46.7M lines.

Round-trip integrity after loading into Turso, checked in SQL against the stored
rows — `substr(sentence, span_start+1, span_end-span_start) != span` returns
**zero** mismatches, and zero duplicate primary keys.

### Known gaps

- **`validate.py` does not scale past roughly 20M lines.** It accumulates every
  record in memory for the group and corpus checks, and has been killed on four
  consecutive large builds. Every sentence is still structurally verified at
  write time by `SpanBuilder` — offsets by construction, bounds, ordering,
  overlap policy, NFC — so a failing sentence raises rather than being written;
  what is missing is the corpus-level pass. Lines for one sentence are always
  contiguous, so a streaming validator could run every §14 check in constant
  memory. That is the fix, not another retry.
- No validation report exists for the three-pass corpus.
- Non-English *prose* is not implemented. `language` is `en` on every line by
  construction; only the PHI varies by language. Frames for Swahili, Kinyarwanda,
  Hausa and Yoruba clinical register need native-speaker authorship.
- Evaluation should not run on synthetic data alone. The `source` field exists so
  a real, human-annotated held-out set can be distinguished; without one you
  measure how well the model learned this generator.

## Loading into a database

`load_turso.py` covers libsql/Turso. For Postgres, note the sizing before
planning: 235,992,587 rows is roughly 200 GB with indexes in the flat layout, or
about 110 GB normalised into separate `sentences` and `spans` tables — the flat
layout repeats the sentence text on every span row, which normalising removes.
That exceeds every free tier and most laptops. A subset (one pass, or a
stratified sample across passes) is usually enough for pipeline development;
streaming the JSONL directly is faster than a database read for training itself.
