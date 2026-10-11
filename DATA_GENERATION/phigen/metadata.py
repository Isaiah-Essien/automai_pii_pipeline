"""Per-note and per-sentence metadata (Section 12)."""

from __future__ import annotations

import random
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class NoteContext:
    """Metadata shared by every sentence in one synthetic clinical note."""

    note_id: str
    patient_id: str
    language: str
    source: str


def new_patient_id() -> str:
    """Mint a fresh pseudonymous patient id.

    Section 12 is explicit that this is never a real hospital identifier and
    never a hash of one, since a low-entropy identifier is reversible by
    enumeration.  We therefore draw from the OS CSPRNG with no input at all --
    there is nothing to invert because nothing went in.
    """
    return f"pt_{secrets.token_hex(16)}"


def new_note_id() -> str:
    return f"note_{secrets.token_hex(12)}"


def pick_language(rng: random.Random, language_mix: dict[str, float]) -> str:
    r = rng.random()
    cumulative = 0.0
    for lang, share in language_mix.items():
        cumulative += share
        if r <= cumulative:
            return lang
    return next(iter(language_mix))


def make_note_context(
    rng: random.Random, language_mix: dict[str, float], source: str
) -> NoteContext:
    return NoteContext(
        note_id=new_note_id(),
        patient_id=new_patient_id(),
        language=pick_language(rng, language_mix),
        source=source,
    )
