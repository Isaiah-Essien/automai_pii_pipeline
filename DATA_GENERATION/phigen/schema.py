"""The schema's type lists and the decision they imply.

Section 4 types are always REDACT; Section 5 types are always PRESERVE.  The
mapping is derived from these two sets rather than written per-template, so a
template cannot accidentally emit AGE as REDACT.
"""

from __future__ import annotations

REDACT_TYPES = frozenset(
    {
        "PERSON",
        "PHONE",
        "EMAIL",
        "DATE",
        "LOCATION",
        "ADDRESS",
        "NATIONAL_ID",
        "MEDICAL_RECORD",
    }
)

PRESERVE_TYPES = frozenset(
    {
        "DISEASE",
        "DRUG",
        "AGE",
        "FACILITY_GENERIC",
        "ANATOMY",
        "NON_PHI",
    }
)

ALL_TYPES = REDACT_TYPES | PRESERVE_TYPES

AMBIGUITY_TYPES = frozenset(
    {
        "none",
        "person_disease",
        "person_drug",
        "person_place",
        "eponym",
        "role_ambiguous",
        "orthographic",
    }
)

SURFACE_FORMS = frozenset({"standard", "local", "spoken", "mixed"})

# Languages the PHI lexicons draw on.  The prose is always English; these tag
# the names and places embedded in it, so `code_switched` can be reported from
# what a sentence actually contains rather than sampled from a rate.
PHI_LANGUAGES = frozenset(
    {"en", "ig", "yo", "ha", "sw", "rw", "ki", "zu", "ny", "ak", "ff", "lg", "ach", "dag"}
)

REQUIRED_FIELDS = (
    "sentence_id",
    "sentence",
    "span_start",
    "span_end",
    "span",
    "phi_type",
    "decision",
)

METADATA_FIELDS = (
    "phi_languages",
    "note_id",
    "patient_id",
    "sentence_index",
    "source",
    "language",
    "code_switched",
    "ambiguity_type",
    "surface_form",
)

# Section 13.3: negative sentences carry only these keys.
NEGATIVE_FIELDS = (
    "sentence_id",
    "sentence",
    "note_id",
    "sentence_index",
    "source",
    "language",
)


def decision_for(phi_type: str) -> str:
    """Return the decision implied by the type's schema section."""
    if phi_type in REDACT_TYPES:
        return "REDACT"
    if phi_type in PRESERVE_TYPES:
        return "PRESERVE"
    raise ValueError(f"unknown phi_type {phi_type!r}")
