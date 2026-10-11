"""Sentence templates with typed slots.

A template is a callable that receives a builder, the lexicons, and an RNG, and
places its own literal text and spans.  Expressing templates as code rather than
format strings is what lets offsets stay a construction artefact: a template
never hands back a finished string for someone else to search.

Each template declares the phi_types it exercises and the ambiguity_type it
produces.  `ambiguity_type` is *reporting* metadata -- it describes a template
that was already chosen for other reasons, and is never consulted to decide what
a span's label should be.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable

from .lexicons import Lexicons
from .spans import SpanBuilder
from .variants import (
    EMAIL_FAMILIES,
    PHONE_FAMILIES,
    make_address,
    make_age,
    make_date,
    make_email,
    make_medical_record,
    make_national_id,
    make_phone,
)

# A template mutates the builder in place; the driver supplies the family hints
# needed to hit the Section 15 variant floors.
TemplateFn = Callable[[SpanBuilder, Lexicons, random.Random, dict], None]


@dataclass
class Template:
    name: str
    fn: TemplateFn
    phi_types: tuple[str, ...]
    ambiguity_type: str = "none"
    decision_profile: str = "REDACT"  # dominant decision, used by the mix controller
    weight: float = 1.0


REGISTRY: list[Template] = []


def template(name, phi_types, ambiguity_type="none", decision_profile="REDACT", weight=1.0):
    def deco(fn: TemplateFn) -> TemplateFn:
        REGISTRY.append(
            Template(name, fn, tuple(phi_types), ambiguity_type, decision_profile, weight)
        )
        return fn

    return deco


def _name(lex, rng):
    return lex.sample(lex.names_full, rng)


def _split_name(full: str) -> tuple[str, str]:
    parts = full.split(" ", 1)
    return (parts[0], parts[1]) if len(parts) == 2 else (full, "Bello")


def _tail(b: SpanBuilder, rng: random.Random, extra_pool: list[str]) -> None:
    """Append a trailing clause sometimes, to spread sentence length.

    Section 15 asks for a distributed length with a long tail past 60 tokens, so
    a minority of sentences get several stacked clauses.
    """
    n = rng.random()
    if n < 0.45:
        return
    clauses = [
        " The note was countersigned during the ward round.",
        " Observations remained stable throughout the shift.",
        " The plan was discussed with the family at the bedside.",
        " A follow-up appointment was arranged before discharge.",
        " Documentation was completed in the paper file and the register.",
        " The team agreed to review the results at the morning handover.",
        " Nursing staff were asked to monitor intake and output hourly.",
        " Consent for the procedure was explained and recorded.",
    ]
    count = 1 if n < 0.85 else rng.randrange(3, 7)  # long tail past 60 tokens
    for _ in range(count):
        b.literal(clauses[rng.randrange(len(clauses))])


# ---------------------------------------------------------------- REDACT ----


@template("person_admission", ["PERSON", "DATE"], weight=3.0)
def t_person_admission(b, lex, rng, ctx):
    b.literal("Patient ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(" was admitted on ")
    b.span(make_date(rng).text, "DATE")
    b.literal(" with worsening symptoms.")
    _tail(b, rng, lex.non_phi)


@template("person_nin_date_phone", ["PERSON", "NATIONAL_ID", "DATE", "PHONE"], weight=2.0)
def t_person_nin_date_phone(b, lex, rng, ctx):
    fam = ctx.get("phone_family", "standard")
    b.literal("Patient ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(", NIN ")
    b.span(make_national_id(rng).text, "NATIONAL_ID")
    b.literal(", was admitted on ")
    b.span(make_date(rng).text, "DATE")
    b.literal(" after her husband called from ")
    v = make_phone(rng, fam)
    b.span(v.text, "PHONE", surface_form=v.surface_form)
    b.literal(" to report chest pain.")
    _tail(b, rng, lex.non_phi)


@template("emergency_contact_phone", ["PERSON", "PHONE"], weight=3.0)
def t_emergency_contact_phone(b, lex, rng, ctx):
    fam = ctx.get("phone_family", "spoken")
    b.literal("Emergency contact ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(" can be reached on ")
    v = make_phone(rng, fam)
    b.span(v.text, "PHONE", surface_form=v.surface_form)
    b.literal(" at any hour.")
    _tail(b, rng, lex.non_phi)


@template("guardian_spoken_phone", ["PHONE"], weight=2.5)
def t_guardian_spoken_phone(b, lex, rng, ctx):
    fam = ctx.get("phone_family", "spoken")
    b.literal("The guardian said we should call ")
    v = make_phone(rng, fam)
    b.span(v.text, "PHONE", surface_form=v.surface_form)
    b.literal(" if the fever persists overnight.")
    _tail(b, rng, lex.non_phi)


@template("next_of_kin_email", ["PERSON", "EMAIL"], weight=2.5)
def t_next_of_kin_email(b, lex, rng, ctx):
    fam = ctx.get("email_family", "spoken")
    full = _name(lex, rng)
    given, surname = _split_name(full)
    b.literal("Next of kin ")
    b.span(full, "PERSON")
    b.literal(" gave the contact address ")
    v = make_email(rng, fam, given, surname)
    b.span(v.text, "EMAIL", surface_form=v.surface_form)
    b.literal(" for correspondence.")
    _tail(b, rng, lex.non_phi)


@template("clerk_email_only", ["EMAIL"], weight=2.0)
def t_clerk_email_only(b, lex, rng, ctx):
    fam = ctx.get("email_family", "spoken")
    given, surname = _split_name(_name(lex, rng))
    b.literal("Registration clerk noted ")
    v = make_email(rng, fam, given, surname)
    b.span(v.text, "EMAIL", surface_form=v.surface_form)
    b.literal(" as the contact email on the intake form.")
    _tail(b, rng, lex.non_phi)


@template("mrn_update", ["PERSON", "MEDICAL_RECORD"], weight=2.5)
def t_mrn_update(b, lex, rng, ctx):
    b.literal("Records officer updated the file for ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(" under hospital file MRN ")
    b.span(make_medical_record(rng).text, "MEDICAL_RECORD")
    b.literal(" this morning.")
    _tail(b, rng, lex.non_phi)


@template("address_home_visit", ["PERSON", "ADDRESS", "LOCATION"], weight=2.0)
def t_address_home_visit(b, lex, rng, ctx):
    b.literal("Community health worker visited ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(" at ")
    b.span(make_address(rng, lex.sample(lex.places, rng).split()[0]).text, "ADDRESS")
    b.literal(" near ")
    b.span(lex.sample(lex.places, rng), "LOCATION")
    b.literal(" to complete the review.")
    _tail(b, rng, lex.non_phi)


@template("facility_referral", ["PERSON", "LOCATION"], weight=2.0)
def t_facility_referral(b, lex, rng, ctx):
    b.literal("Referral letter for ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(" was sent to ")
    b.span(lex.sample(lex.facilities, rng), "LOCATION")
    b.literal(" for specialist review.")
    _tail(b, rng, lex.non_phi)


@template("doctor_and_patient", ["PERSON"], ambiguity_type="role_ambiguous", weight=2.5)
def t_doctor_and_patient(b, lex, rng, ctx):
    b.literal("Dr ")
    b.span(lex.sample(lex.names_surname, rng), "PERSON", ambiguity_type="role_ambiguous")
    b.literal(" reviewed ")
    b.span(lex.sample(lex.role_ambiguous, rng), "PERSON", ambiguity_type="role_ambiguous")
    b.literal(" in the afternoon clinic.")
    _tail(b, rng, lex.non_phi)


@template("dob_registration", ["PERSON", "DATE", "NATIONAL_ID"], weight=2.0)
def t_dob_registration(b, lex, rng, ctx):
    b.literal("Registration confirmed that ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(" was born on ")
    b.span(make_date(rng).text, "DATE")
    b.literal(" and holds national identifier ")
    b.span(make_national_id(rng).text, "NATIONAL_ID")
    b.literal(".")
    _tail(b, rng, lex.non_phi)


# --------------------------------------------------------------- PRESERVE ---


@template("age_only", ["AGE"], decision_profile="PRESERVE", weight=3.0)
def t_age_only(b, lex, rng, ctx):
    b.literal("The ")
    b.span(make_age(rng).text, "AGE")
    b.literal(" male presented with ")
    b.span(lex.sample(lex.diseases, rng), "DISEASE")
    b.literal(" and was started on ")
    b.span(lex.sample(lex.drugs, rng), "DRUG")
    b.literal(".")
    _tail(b, rng, lex.non_phi)


@template("disease_and_drug", ["DISEASE", "DRUG"], decision_profile="PRESERVE", weight=3.0)
def t_disease_and_drug(b, lex, rng, ctx):
    b.literal("Treatment for ")
    b.span(lex.sample(lex.diseases, rng), "DISEASE")
    b.literal(" was changed to ")
    b.span(lex.sample(lex.drugs, rng), "DRUG")
    b.literal(" after the review.")
    _tail(b, rng, lex.non_phi)


@template("generic_ward", ["FACILITY_GENERIC", "ANATOMY"], decision_profile="PRESERVE", weight=2.5)
def t_generic_ward(b, lex, rng, ctx):
    b.literal("The patient was moved to the ")
    b.span(lex.sample(lex.facilities_generic, rng), "FACILITY_GENERIC")
    b.literal(" for observation of the ")
    b.span(lex.sample(lex.anatomy, rng), "ANATOMY")
    b.literal(".")
    _tail(b, rng, lex.non_phi)


@template("anatomy_exam", ["ANATOMY", "NON_PHI"], decision_profile="PRESERVE", weight=2.5)
def t_anatomy_exam(b, lex, rng, ctx):
    b.literal("Examination of the ")
    b.span(lex.sample(lex.anatomy, rng), "ANATOMY")
    b.literal(" was documented at ")
    b.span(lex.sample(lex.non_phi, rng), "NON_PHI")
    b.literal(" without new findings.")
    _tail(b, rng, lex.non_phi)


@template("age_disease_generic", ["AGE", "DISEASE", "FACILITY_GENERIC"],
          decision_profile="PRESERVE", weight=2.5)
def t_age_disease_generic(b, lex, rng, ctx):
    b.literal("A patient ")
    b.span(make_age(rng).text, "AGE")
    b.literal(" with ")
    b.span(lex.sample(lex.diseases, rng), "DISEASE")
    b.literal(" remains on the ")
    b.span(lex.sample(lex.facilities_generic, rng), "FACILITY_GENERIC")
    b.literal(".")
    _tail(b, rng, lex.non_phi)


# ------------------------------------------------- AMBIGUOUS / MIXED CASES ---


@template("person_vs_disease", ["PERSON", "DISEASE"], ambiguity_type="person_disease", weight=3.0)
def t_person_vs_disease(b, lex, rng, ctx):
    pair = lex.person_disease[rng.randrange(len(lex.person_disease))]
    surname = lex.sample(lex.names_surname, rng)
    b.literal("Patient ")
    b.span(f"{pair.person_form} {surname}", "PERSON", ambiguity_type="person_disease")
    b.literal(" was reviewed in clinic; peripheral smear confirms ")
    b.span(pair.other_form, "DISEASE", ambiguity_type="person_disease")
    b.literal(" with parasitemia.")
    _tail(b, rng, lex.non_phi)


@template("person_vs_drug_nested", ["PERSON", "DRUG"], ambiguity_type="person_drug", weight=3.0)
def t_person_vs_drug_nested(b, lex, rng, ctx):
    """The canonical Section 13.2 case: PERSON containing an inner DRUG span."""
    pair = lex.person_drug[rng.randrange(len(lex.person_drug))]
    surname = lex.sample(lex.names_surname, rng)
    b.literal("Pharmacy dispensed ")
    b.span(pair.other_form, "DRUG", ambiguity_type="person_drug")
    b.literal(" for otitis media; staff nurse ")
    b.nested(
        f"{pair.person_form} {surname}",
        "PERSON",
        pair.person_form,
        "DRUG",
        outer_ambiguity="person_drug",
        inner_ambiguity="person_drug",
    )
    b.literal(" documented the dose.")
    _tail(b, rng, lex.non_phi)


@template("eponym_vs_person", ["DISEASE", "PERSON"], ambiguity_type="eponym", weight=3.0)
def t_eponym_vs_person(b, lex, rng, ctx):
    pair = lex.person_disease[rng.randrange(len(lex.person_disease))]
    b.literal("Assessment suggests ")
    b.span(pair.other_form, "DISEASE", ambiguity_type="eponym")
    b.literal("; follow-up arranged with Dr ")
    b.span(pair.person_form, "PERSON", ambiguity_type="eponym")
    b.literal(" after patient ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(" completed the scale.")
    _tail(b, rng, lex.non_phi)


@template("person_vs_place", ["PERSON", "LOCATION"], ambiguity_type="person_place", weight=3.0)
def t_person_vs_place(b, lex, rng, ctx):
    pair = lex.person_place[rng.randrange(len(lex.person_place))]
    surname = lex.sample(lex.names_surname, rng)
    b.literal("Nurse ")
    b.span(f"{pair.person_form} {surname}", "PERSON", ambiguity_type="person_place")
    b.literal(" escorted the patient home to ")
    b.span(pair.other_form, "LOCATION", ambiguity_type="person_place")
    b.literal(" after the clinic closed.")
    _tail(b, rng, lex.non_phi)


@template("age_never_redacted", ["AGE", "PERSON"], decision_profile="PRESERVE", weight=2.0)
def t_age_never_redacted(b, lex, rng, ctx):
    """AGE stays PRESERVE even standing next to a PERSON that is redacted."""
    b.literal("Patient ")
    b.span(_name(lex, rng), "PERSON")
    b.literal(", ")
    b.span(make_age(rng).text, "AGE")
    b.literal(", was reviewed on the ward.")
    _tail(b, rng, lex.non_phi)


@template("drug_name_collision", ["DRUG", "PERSON"], ambiguity_type="person_drug", weight=2.0)
def t_drug_name_collision(b, lex, rng, ctx):
    pair = lex.person_drug[rng.randrange(len(lex.person_drug))]
    b.literal("The prescription listed ")
    b.span(pair.other_form, "DRUG", ambiguity_type="person_drug")
    b.literal(" while the attending clinician was Dr ")
    b.span(pair.person_form, "PERSON", ambiguity_type="person_drug")
    b.literal(".")
    _tail(b, rng, lex.non_phi)


@template("orthographic_variant", ["PERSON", "DISEASE"], ambiguity_type="orthographic", weight=2.0)
def t_orthographic_variant(b, lex, rng, ctx):
    """Diacritic and transliteration variation on an otherwise ordinary name."""
    base = lex.sample(lex.names_full, rng)
    given, surname = _split_name(base)
    swaps = {"e": "é", "o": "ô", "a": "à", "u": "ù", "i": "í"}
    marked = given
    for plain, accented in swaps.items():
        if plain in given.lower():
            idx = given.lower().index(plain)
            marked = given[:idx] + accented + given[idx + 1 :]
            break
    b.literal("Intake register spells the name ")
    b.span(f"{marked} {surname}", "PERSON", ambiguity_type="orthographic")
    b.literal(" although the card reads differently; treated for ")
    b.span(lex.sample(lex.diseases, rng), "DISEASE", ambiguity_type="orthographic")
    b.literal(".")
    _tail(b, rng, lex.non_phi)


NEGATIVE_FRAMES = [
    "The ward round was completed before midday and all notes were filed.",
    "Observations were within normal limits throughout the shift.",
    "The team agreed to review the results at the morning handover.",
    "Consent for the procedure was explained and recorded in the register.",
    "Supplies were restocked and the drug cupboard was checked.",
    "Handover was completed without outstanding actions.",
    "The register was reconciled against the attendance sheet.",
    "Equipment was serviced and returned to the department.",
    "Triage protocols were reviewed with the nursing team.",
    "The discharge summary template was updated this quarter.",
    "Infection control measures were reinforced during the briefing.",
    "Fluid balance charts were audited for completeness.",
    "The duty roster for the coming week was circulated.",
    "Waste segregation practice was observed and found satisfactory.",
    "Oxygen cylinders were checked and recorded as full.",
    "The emergency trolley was restocked after the shift.",
]


def negative_sentence(rng: random.Random) -> str:
    """A sentence with no candidate span at all (Section 13.3)."""
    text = NEGATIVE_FRAMES[rng.randrange(len(NEGATIVE_FRAMES))]
    if rng.random() < 0.3:
        text += " " + NEGATIVE_FRAMES[rng.randrange(len(NEGATIVE_FRAMES))]
    return text


def templates_by_decision(profile: str) -> list[Template]:
    return [t for t in REGISTRY if t.decision_profile == profile]
