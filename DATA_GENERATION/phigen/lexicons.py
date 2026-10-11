"""Lexicon loading and sampling.

Bulk lists come from data/lexicons/*.txt; the ambiguous overlap sets that carry
the hard cases come from hand-curated *.tsv files.  Sampling is weighted against
a running usage count so no single entry can run away with a disproportionate
share of its type (the Section 15 floor of 0.1 percent per entry).
"""

from __future__ import annotations

import random
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "lexicons"


def _read_lines(path: Path) -> list[str]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(unicodedata.normalize("NFC", line))
    return out


def _read_tsv(path: Path) -> list[tuple[str, ...]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        rows.append(tuple(unicodedata.normalize("NFC", c.strip()) for c in line.split("\t")))
    return rows


@dataclass(frozen=True)
class TaggedEntry:
    """A lexical entry together with the language it comes from."""

    text: str
    language: str


@dataclass
class AmbiguousPair:
    """A surface form that is valid as two different phi_types."""

    person_form: str
    other_form: str
    note: str = ""


@dataclass
class Lexicons:
    names_full: list[str] = field(default_factory=list)
    names_given: list[str] = field(default_factory=list)
    names_surname: list[str] = field(default_factory=list)
    drugs: list[str] = field(default_factory=list)
    diseases: list[str] = field(default_factory=list)
    places: list[str] = field(default_factory=list)
    facilities: list[str] = field(default_factory=list)
    facilities_generic: list[str] = field(default_factory=list)
    anatomy: list[str] = field(default_factory=list)
    non_phi: list[str] = field(default_factory=list)
    person_disease: list[AmbiguousPair] = field(default_factory=list)
    person_drug: list[AmbiguousPair] = field(default_factory=list)
    person_place: list[AmbiguousPair] = field(default_factory=list)
    eponyms: list[tuple[str, str]] = field(default_factory=list)
    role_ambiguous: list[str] = field(default_factory=list)
    # Language-tagged variants, used to report `language` and `code_switched`
    # honestly: the prose is English, but the PHI inside it is not.
    given_by_lang: list[TaggedEntry] = field(default_factory=list)
    surname_by_lang: list[TaggedEntry] = field(default_factory=list)
    places_by_lang: list[TaggedEntry] = field(default_factory=list)

    # Usage counters power the anti-concentration sampler.
    _usage: dict[str, int] = field(default_factory=dict, repr=False)

    def sample(self, pool: list[str], rng: random.Random, k: int = 8) -> str:
        """Pick the least-used of k random candidates.

        This keeps any single lexical entry from dominating its type without the
        cost of maintaining a full priority queue over thousands of entries.
        """
        best, best_count = None, None
        for _ in range(k):
            cand = pool[rng.randrange(len(pool))]
            count = self._usage.get(cand, 0)
            if best_count is None or count < best_count:
                best, best_count = cand, count
        self._usage[best] = self._usage.get(best, 0) + 1
        return best

    def usage(self) -> dict[str, int]:
        return dict(self._usage)


def load_lexicons(data_dir: Path | str = DATA_DIR) -> Lexicons:
    d = Path(data_dir)
    lex = Lexicons(
        names_full=_read_lines(d / "names_full.txt"),
        names_given=_read_lines(d / "names_given.txt"),
        names_surname=_read_lines(d / "names_surname.txt"),
        drugs=_read_lines(d / "drugs.txt"),
        diseases=_read_lines(d / "diseases.txt"),
        places=_read_lines(d / "places.txt"),
        facilities=_read_lines(d / "facilities.txt"),
        facilities_generic=_read_lines(d / "facilities_generic.txt"),
        anatomy=_read_lines(d / "anatomy.txt"),
        non_phi=_read_lines(d / "non_phi.txt"),
        role_ambiguous=_read_lines(d / "role_ambiguous.txt"),
    )
    lex.person_disease = [
        AmbiguousPair(r[0], r[1], r[2] if len(r) > 2 else "")
        for r in _read_tsv(d / "ambiguous_person_disease.tsv")
    ]
    lex.person_drug = [
        AmbiguousPair(r[0], r[1], r[2] if len(r) > 2 else "")
        for r in _read_tsv(d / "ambiguous_person_drug.tsv")
    ]
    lex.person_place = [
        AmbiguousPair(r[0], r[1], r[2] if len(r) > 2 else "")
        for r in _read_tsv(d / "ambiguous_person_place.tsv")
    ]
    lex.eponyms = [(r[0], r[1]) for r in _read_tsv(d / "eponyms.tsv")]
    lex.given_by_lang = [
        TaggedEntry(r[0], r[1]) for r in _read_tsv(d / "names_given_lang.tsv")
    ]
    lex.surname_by_lang = [
        TaggedEntry(r[0], r[1]) for r in _read_tsv(d / "names_surname_lang.tsv")
    ]
    lex.places_by_lang = [
        TaggedEntry(r[0], r[1]) for r in _read_tsv(d / "places_lang.tsv")
    ]
    return lex


def check_floors(lex: Lexicons, minimum: int = 2000) -> dict[str, tuple[int, bool]]:
    """Section 15: name, drug, disease, place, facility lists >= 2,000 entries."""
    required = {
        "names_full": lex.names_full,
        "drugs": lex.drugs,
        "diseases": lex.diseases,
        "places": lex.places,
        "facilities": lex.facilities,
    }
    return {k: (len(v), len(v) >= minimum) for k, v in required.items()}
