"""Composable frame parts for large-scale template diversity.

The hand-written templates in `templates.py` are monolithic: each one is a whole
sentence.  That does not scale -- Section 15 needs roughly 200 distinct frames
per phi_type, and writing 200 whole sentences per type by hand produces 200
near-identical sentences, which passes the arithmetic while teaching the model a
single shape.

Instead we decompose a sentence into independent axes and compose across them:

    REGISTER  x  OPENING  x  PHI-CLAUSE  x  CONNECTIVE  x  TAIL

Each axis is written once and reused, so ~200 hand-written parts yield thousands
of distinct frames.  Crucially the axes vary *structure*, not just wording: a
telegraphic ward note and a formal referral letter place their PHI in different
positions, and a model trained on only one shape fails on the other.

Every part is a callable that places text through the SpanBuilder, so offsets
remain a construction artefact exactly as in `templates.py`.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable

from .lexicons import Lexicons
from .spans import SpanBuilder

# A part places text on the builder.  It receives the shared slot-filler so that
# a clause can request "a PERSON" without knowing how names are drawn.
PartFn = Callable[[SpanBuilder, "Slots", random.Random], None]


@dataclass
class Part:
    """One composable fragment of a sentence.

    `continuation` records what may grammatically follow.  An opening that ends
    with a bare subject ("Patient X") can take a verb-initial clause ("and was
    admitted on D"); one that already carries its own predicate ("I am referring
    X to your unit") cannot, and must be followed by an independent clause.
    Ignoring this is what produces "I am referring X to your unit and was
    treated for malaria".
    """

    name: str
    fn: PartFn
    phi_types: tuple[str, ...] = ()
    register: tuple[str, ...] = ()  # empty = fits any register
    ambiguity_type: str = "none"
    # "verb"  -> a verb-initial clause may follow (subject is dangling)
    # "indep" -> only an independent clause may follow
    continuation: str = "verb"
    # True when the part's own text begins with punctuation (";", "|", ","),
    # which decides how it joins to whatever precedes it.
    opens_with_punctuation: bool = False


# Registers model how clinical text is actually written.  Real notes are not
# uniform prose: a handover line, a structured intake field, and a formal
# referral letter differ in punctuation, capitalisation, and where PHI sits.
# Types that describe one attribute of one patient: a sentence stating two
# different ages, or two national identifiers, is incoherent regardless of how
# well-formed the spans are.
SINGLETON_TYPES = frozenset({"AGE", "NATIONAL_ID", "MEDICAL_RECORD", "ADDRESS"})

REGISTERS = (
    "narrative",     # full prose sentences
    "telegraphic",   # ward shorthand: "47M, HTN, o/e chest clear."
    "structured",    # field-style: "Name: X | DOB: D | MRN: M"
    "handover",      # shift-handover list items
    "letter",        # referral / discharge correspondence
)


class Slots:
    """Places typed spans on a builder, hiding how each type is rendered.

    A clause says `slots.person(b)` and gets a correctly-labelled PERSON span
    with its offsets recorded.  This keeps clauses free of lexicon and variant
    detail, so the same clause works for any surface form the driver requests.
    """

    def __init__(self, lex: Lexicons, rng: random.Random, ctx: dict):
        self.lex = lex
        self.rng = rng
        self.ctx = ctx
        # Languages contributed by the PHI placed in this sentence.  The
        # surrounding prose is always English, so a sentence is code-switched
        # exactly when a span comes from something other than English.
        self.phi_languages: set[str] = set()

    def _tagged(self, pool):
        """Draw a language-tagged entry, recording the language it came from."""
        entry = pool[self.rng.randrange(len(pool))]
        self.phi_languages.add(entry.language)
        return entry.text

    def code_switched(self) -> bool:
        return any(lang != "en" for lang in self.phi_languages)

    # -- REDACT types ------------------------------------------------------

    def person(self, b, *, ambiguity_type="none", role="patient"):
        """Place a PERSON span built from language-tagged name parts.

        Given name and surname are drawn independently, which is how names
        actually combine in the region -- a Yoruba given name beside an Igbo
        surname is unremarkable -- and both languages are recorded.
        """
        given = self._tagged(self.lex.given_by_lang)
        surname = self._tagged(self.lex.surname_by_lang)
        name = f"{given} {surname}"
        self.lex._usage[name] = self.lex._usage.get(name, 0) + 1
        return b.span(name, "PERSON", ambiguity_type=ambiguity_type)

    def person_surname(self, b, *, ambiguity_type="none"):
        return b.span(
            self._tagged(self.lex.surname_by_lang),
            "PERSON",
            ambiguity_type=ambiguity_type,
        )

    def phone(self, b, *, family=None):
        from .variants import make_phone

        fam = family or self.ctx.get("phone_family", "standard")
        v = make_phone(self.rng, fam, region=self.ctx.get("region", "ng"))
        return b.span(v.text, "PHONE", surface_form=v.surface_form)

    def email(self, b, *, family=None):
        from .variants import make_email

        fam = family or self.ctx.get("email_family", "standard")
        full = self.lex.sample(self.lex.names_full, self.rng)
        parts = full.split(" ", 1)
        given, surname = (parts + ["Bello"])[:2]
        v = make_email(self.rng, fam, given, surname)
        return b.span(v.text, "EMAIL", surface_form=v.surface_form)

    def date(self, b):
        from .variants import make_date

        return b.span(make_date(self.rng).text, "DATE")

    def location(self, b, *, ambiguity_type="none"):
        # Real toponyms are a closed set of ~70, so drawing them half the time
        # puts each one well above its Section 15 share.  They stay in the mix
        # for language coverage, but the composed places (2,200 of them) carry
        # the bulk of LOCATION.
        if self.rng.random() < 0.12:
            text = self._tagged(self.lex.places_by_lang)
        else:
            text = self.lex.sample(self.lex.places, self.rng)
        return b.span(text, "LOCATION", ambiguity_type=ambiguity_type)

    def facility_named(self, b):
        return b.span(self.lex.sample(self.lex.facilities, self.rng), "LOCATION")

    def address(self, b):
        from .variants import make_address

        place = self.lex.sample(self.lex.places, self.rng).split()[0]
        return b.span(make_address(self.rng, place).text, "ADDRESS")

    def national_id(self, b):
        from .variants import make_national_id

        v = make_national_id(self.rng, region=self.ctx.get("region", "ng"))
        return b.span(v.text, "NATIONAL_ID")

    def medical_record(self, b):
        from .variants import make_medical_record

        return b.span(make_medical_record(self.rng).text, "MEDICAL_RECORD")

    # -- PRESERVE types ----------------------------------------------------

    def age(self, b, *, bare=False):
        """Place an AGE span.

        `bare` excludes the "aged N" phrasing, for clauses that already supply
        the copula -- "the stated age is aged 56" reads wrong.
        """
        from .variants import make_age

        text = make_age(self.rng).text
        while bare and text.startswith("aged "):
            text = make_age(self.rng).text
        return b.span(text, "AGE")

    def disease(self, b, *, ambiguity_type="none"):
        return b.span(
            self.lex.sample(self.lex.diseases, self.rng),
            "DISEASE",
            ambiguity_type=ambiguity_type,
        )

    def drug(self, b, *, ambiguity_type="none"):
        return b.span(
            self.lex.sample(self.lex.drugs, self.rng),
            "DRUG",
            ambiguity_type=ambiguity_type,
        )

    def facility_generic(self, b):
        return b.span(
            self.lex.sample(self.lex.facilities_generic, self.rng), "FACILITY_GENERIC"
        )

    def anatomy(self, b):
        return b.span(self.lex.sample(self.lex.anatomy, self.rng), "ANATOMY")

    def non_phi(self, b):
        return b.span(self.lex.sample(self.lex.non_phi, self.rng), "NON_PHI")


# ---------------------------------------------------------------------------
# OPENINGS -- how a note or sentence begins.
#
# Drawn from how clinical text is actually written across district hospitals,
# health centres, and referral facilities in West and East Africa: outpatient
# cards, antenatal registers, IDSR case forms, referral letters, ward handover
# sheets.  Vocabulary is deliberately regional -- "health centre" not "clinic",
# "sister" and "matron" as ward roles, CHEW/CHW community cadres, "book" for
# register, NHIS/NHIF scheme references.
# ---------------------------------------------------------------------------

OPENINGS: list[Part] = []


def opening(name, register=(), phi_types=(), continuation="verb"):
    def deco(fn):
        OPENINGS.append(Part(name, fn, phi_types, register, continuation=continuation))
        return fn

    return deco


# -- narrative openings ------------------------------------------------------

@opening("op_patient_presented", ("narrative",), ("PERSON",))
def _(b, s, rng):
    b.literal("Patient ")
    s.person(b)
    b.literal(" presented at the outpatient department")


@opening("op_seen_in_clinic", ("narrative",), ("PERSON",))
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" was seen in the general outpatient clinic")


@opening("op_brought_by_relative", ("narrative",), ("PERSON",))
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" was brought to the health centre by a relative")


@opening("op_self_referred", ("narrative",), ("PERSON",))
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" self-referred to the district hospital")


@opening("op_walked_in", ("narrative",), ("PERSON",))
def _(b, s, rng):
    b.literal("Client ")
    s.person(b)
    b.literal(" walked in without an appointment")


@opening("op_referred_from", ("narrative",), ("PERSON", "LOCATION"), continuation="indep")
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" was referred from ")
    s.facility_named(b)


@opening("op_reviewed_ward_round", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("During the morning ward round the team reviewed ")
    s.person(b)


@opening("op_readmitted", ("narrative",), ("PERSON", "DATE"), continuation="indep")
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" was readmitted on ")
    s.date(b)


@opening("op_chw_visit", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The community health extension worker visited ")
    s.person(b)


@opening("op_antenatal_booking", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" attended the antenatal booking visit")


@opening("op_under_five_clinic", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The mother of ")
    s.person(b)
    b.literal(" attended the under-five clinic")


@opening("op_immunisation_defaulter", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Immunisation defaulter tracing identified ")
    s.person(b)


@opening("op_records_officer", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The records officer retrieved the folder for ")
    s.person(b)


@opening("op_matron_noted", ("narrative",), ("PERSON",))
def _(b, s, rng):
    b.literal("The matron reviewed the file of ")
    s.person(b)


@opening("op_on_examination", ("narrative",), ())
def _(b, s, rng):
    b.literal("On examination the patient was found to be stable")


@opening("op_history_revealed", ("narrative",), ())
def _(b, s, rng):
    b.literal("History taking was completed for the patient")


@opening("op_laboratory", ("narrative",), ())
def _(b, s, rng):
    b.literal("Laboratory results were reviewed for the patient")


@opening("op_nurse_documented", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Sister ")
    s.person_surname(b)
    b.literal(" documented the assessment")


# -- telegraphic openings ----------------------------------------------------

@opening("op_telegraphic_age", ("telegraphic",), ("AGE",), continuation="indep")
def _(b, s, rng):
    s.age(b)
    b.literal(rng.choice([" M", " F", " male", " female"]))


@opening("op_telegraphic_pt", ("telegraphic",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Pt ")
    s.person(b)


@opening("op_telegraphic_ro", ("telegraphic",), ("DISEASE",), continuation="indep")
def _(b, s, rng):
    b.literal("R/O ")
    s.disease(b)


@opening("op_telegraphic_oe", ("telegraphic",), (), continuation="indep")
def _(b, s, rng):
    b.literal("O/E")


@opening("op_telegraphic_cc", ("telegraphic",), (), continuation="indep")
def _(b, s, rng):
    b.literal("C/O fever x3/7")


@opening("op_telegraphic_dx", ("telegraphic",), ("DISEASE",), continuation="indep")
def _(b, s, rng):
    b.literal("Dx: ")
    s.disease(b)


# -- structured / field-style openings --------------------------------------

@opening("op_field_name", ("structured",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Name: ")
    s.person(b)


@opening("op_field_patient", ("structured",), ("PERSON", "AGE"), continuation="indep")
def _(b, s, rng):
    b.literal("Patient: ")
    s.person(b)
    b.literal(" | Age: ")
    s.age(b, bare=True)


@opening("op_field_age_sex", ("structured",), ("AGE",), continuation="indep")
def _(b, s, rng):
    b.literal("Age: ")
    s.age(b, bare=True)
    b.literal(" | Sex: " + rng.choice(("M", "F")))


@opening("op_narrative_aged", ("narrative",), ("AGE", "PERSON"), continuation="indep")
def _(b, s, rng):
    b.literal("A patient ")
    s.age(b)
    b.literal(" attended the clinic accompanied by ")
    s.person(b)


@opening("op_telegraphic_age_sex", ("telegraphic",), ("AGE",), continuation="indep")
def _(b, s, rng):
    s.age(b)
    b.literal(rng.choice((" male", " female")) + ", reviewed")


@opening("op_handover_age", ("handover",), ("AGE", "PERSON"), continuation="indep")
def _(b, s, rng):
    b.literal(f"Bed {rng.randrange(1, 40)}: ")
    s.person(b)
    b.literal(", ")
    s.age(b)


@opening("op_letter_age", ("letter",), ("AGE", "PERSON"), continuation="indep")
def _(b, s, rng):
    b.literal("I am referring a patient, ")
    s.person(b)
    b.literal(", ")
    s.age(b)
    b.literal(", to your unit")


@opening("op_field_mrn", ("structured",), ("MEDICAL_RECORD",), continuation="indep")
def _(b, s, rng):
    b.literal("File No: ")
    s.medical_record(b)


@opening("op_field_facility", ("structured",), ("LOCATION",), continuation="indep")
def _(b, s, rng):
    b.literal("Facility: ")
    s.facility_named(b)


@opening("op_field_nok", ("structured",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Next of kin: ")
    s.person(b)


# -- handover openings -------------------------------------------------------

@opening("op_handover_bed", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal(f"Bed {rng.randrange(1, 40)}: ")
    s.person(b)


@opening("op_handover_night", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Night shift handover: ")
    s.person(b)


@opening("op_handover_forobs", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("For observation: ")
    s.person(b)


@opening("op_handover_awaiting", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Awaiting review: ")
    s.person(b)


# -- letter openings ---------------------------------------------------------

@opening("op_letter_referral", ("letter",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("I am referring ")
    s.person(b)
    b.literal(" to your unit")


@opening("op_letter_thankyou", ("letter",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Thank you for reviewing ")
    s.person(b)


@opening("op_letter_kindly", ("letter",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Kindly attend to ")
    s.person(b)


@opening("op_letter_discharge", ("letter",), ("PERSON", "DATE"), continuation="indep")
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" was discharged from our facility on ")
    s.date(b)


# ---------------------------------------------------------------------------
# CLAUSES -- the PHI-bearing middle of a sentence.
#
# These carry the spans the model must learn.  They vary not only in wording but
# in *where* the PHI sits: sentence-initial, mid-clause, inside a parenthetical,
# at the end of a list.  A model trained on PHI that always appears in the same
# position learns the position, not the entity.
# ---------------------------------------------------------------------------

CLAUSES: list[Part] = []


def clause(name, phi_types, register=(), ambiguity_type="none", requires="verb"):
    """`requires` states what the clause needs before it.

    "verb"  -> the clause is verb-initial ("and was admitted"), so it needs an
               opening that left its subject dangling.
    "indep" -> the clause is self-contained ("; the pharmacy dispensed X") and
               may follow anything.
    """

    def deco(fn):
        part = Part(name, fn, phi_types, register, ambiguity_type)
        part.continuation = requires
        CLAUSES.append(part)
        return fn

    return deco


# -- PHONE clauses -----------------------------------------------------------

@clause("cl_phone_reachable", ("PHONE",))
def _(b, s, rng):
    b.literal(" and can be reached on ")
    s.phone(b)


@clause("cl_phone_guardian", ("PHONE",), requires="indep")
def _(b, s, rng):
    b.literal("; the guardian asked that we call ")
    s.phone(b)


@clause("cl_phone_husband_called", ("PHONE",))
def _(b, s, rng):
    b.literal(" after the husband called from ")
    s.phone(b)


@clause("cl_phone_sms", ("PHONE",))
def _(b, s, rng):
    b.literal(" and an SMS reminder was sent to ")
    s.phone(b)


@clause("cl_phone_airtime", ("PHONE",), requires="indep")
def _(b, s, rng):
    b.literal("; the tracing team flashed ")
    s.phone(b)
    b.literal(" twice without response")


@clause("cl_phone_field", ("PHONE",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | Tel: ")
    s.phone(b)


@clause("cl_phone_telegraphic", ("PHONE",), ("telegraphic",), requires="indep")
def _(b, s, rng):
    b.literal(", contact ")
    s.phone(b)


@clause("cl_phone_two_numbers", ("PHONE",))
def _(b, s, rng):
    b.literal(" and left two numbers, ")
    s.phone(b)
    b.literal(" and ")
    s.phone(b, family="local")


# -- EMAIL clauses -----------------------------------------------------------

@clause("cl_email_contact", ("EMAIL",))
def _(b, s, rng):
    b.literal(" and gave the contact address ")
    s.email(b)


@clause("cl_email_results", ("EMAIL",), requires="indep")
def _(b, s, rng):
    b.literal("; results are to be sent to ")
    s.email(b)


@clause("cl_email_clerk", ("EMAIL",))
def _(b, s, rng):
    b.literal(" and the clerk recorded ")
    s.email(b)
    b.literal(" on the intake form")


@clause("cl_email_field", ("EMAIL",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | Email: ")
    s.email(b)


@clause("cl_email_scheme", ("EMAIL",), requires="indep")
def _(b, s, rng):
    b.literal("; the scheme correspondence goes to ")
    s.email(b)


# -- identifier clauses ------------------------------------------------------

@clause("cl_nin", ("NATIONAL_ID",), requires="indep")
def _(b, s, rng):
    b.literal(", NIN ")
    s.national_id(b)


@clause("cl_national_id_holds", ("NATIONAL_ID",))
def _(b, s, rng):
    b.literal(" and holds national identifier ")
    s.national_id(b)


@clause("cl_id_field", ("NATIONAL_ID",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | ID: ")
    s.national_id(b)


@clause("cl_mrn_file", ("MEDICAL_RECORD",))
def _(b, s, rng):
    b.literal(" under hospital file ")
    s.medical_record(b)


@clause("cl_mrn_registered", ("MEDICAL_RECORD",))
def _(b, s, rng):
    b.literal(" and was registered as ")
    s.medical_record(b)


@clause("cl_mrn_field", ("MEDICAL_RECORD",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | MRN: ")
    s.medical_record(b)


@clause("cl_mrn_folder_missing", ("MEDICAL_RECORD",), requires="indep")
def _(b, s, rng):
    b.literal("; the folder bearing ")
    s.medical_record(b)
    b.literal(" could not be traced in the registry")


# -- DATE clauses ------------------------------------------------------------

@clause("cl_date_admitted", ("DATE",))
def _(b, s, rng):
    b.literal(" and was admitted on ")
    s.date(b)


@clause("cl_date_appointment", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal("; the next appointment is ")
    s.date(b)


@clause("cl_date_dob", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal(", born ")
    s.date(b)


@clause("cl_date_field", ("DATE",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | DOB: ")
    s.date(b)


@clause("cl_date_lmp", ("DATE",))
def _(b, s, rng):
    b.literal(" with last menstrual period given as ")
    s.date(b)


@clause("cl_date_defaulted", ("DATE",))
def _(b, s, rng):
    b.literal(" but defaulted from treatment after ")
    s.date(b)


# -- LOCATION / ADDRESS clauses ---------------------------------------------

@clause("cl_location_home", ("LOCATION",))
def _(b, s, rng):
    b.literal(" and travelled from ")
    s.location(b)


@clause("cl_location_referred_to", ("LOCATION",))
def _(b, s, rng):
    b.literal(" and was referred onward to ")
    s.facility_named(b)


@clause("cl_address_resides", ("ADDRESS",), requires="indep")
def _(b, s, rng):
    b.literal(", residing at ")
    s.address(b)


@clause("cl_address_field", ("ADDRESS",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | Address: ")
    s.address(b)


@clause("cl_address_traced", ("ADDRESS", "LOCATION"), requires="indep")
def _(b, s, rng):
    b.literal("; the tracing team visited ")
    s.address(b)
    b.literal(" near ")
    s.location(b)


# -- PERSON clauses (relatives, staff, contacts) -----------------------------

@clause("cl_person_nok", ("PERSON",))
def _(b, s, rng):
    b.literal(" and named ")
    s.person(b)
    b.literal(" as next of kin")


@clause("cl_person_emergency", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; the emergency contact is ")
    s.person(b)


@clause("cl_person_attending", ("PERSON",))
def _(b, s, rng):
    b.literal(" and was attended by Dr ")
    s.person_surname(b)


@clause("cl_person_countersigned", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; the entry was countersigned by Sister ")
    s.person_surname(b)


@clause("cl_person_escort", ("PERSON",))
def _(b, s, rng):
    b.literal(" and was escorted by ")
    s.person(b)


@clause("cl_person_guardian_consent", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; consent was given by the guardian ")
    s.person(b)


# -- PRESERVE clauses --------------------------------------------------------

@clause("cl_disease_treated", ("DISEASE",))
def _(b, s, rng):
    b.literal(" and was treated for ")
    s.disease(b)


@clause("cl_disease_confirmed", ("DISEASE",), requires="indep")
def _(b, s, rng):
    b.literal("; the smear confirmed ")
    s.disease(b)


@clause("cl_disease_ro", ("DISEASE",), ("telegraphic",), requires="indep")
def _(b, s, rng):
    b.literal(", r/o ")
    s.disease(b)


@clause("cl_drug_started", ("DRUG",))
def _(b, s, rng):
    b.literal(" and was started on ")
    s.drug(b)


@clause("cl_drug_dispensed", ("DRUG",), requires="indep")
def _(b, s, rng):
    b.literal("; the pharmacy dispensed ")
    s.drug(b)


@clause("cl_drug_stock_out", ("DRUG",))
def _(b, s, rng):
    b.literal(" but ")
    s.drug(b)
    b.literal(" was out of stock at the facility")


@clause("cl_drug_adherence", ("DRUG",))
def _(b, s, rng):
    b.literal(" and adherence counselling for ")
    s.drug(b)
    b.literal(" was reinforced")


@clause("cl_age_only", ("AGE",), requires="indep")
def _(b, s, rng):
    b.literal(", ")
    s.age(b)
    b.literal(",")


@clause("cl_age_presented", ("AGE",))
def _(b, s, rng):
    b.literal(" who is ")
    s.age(b)


@clause("cl_anatomy_exam", ("ANATOMY",))
def _(b, s, rng):
    b.literal(" with tenderness over the ")
    s.anatomy(b)


@clause("cl_anatomy_swelling", ("ANATOMY",), requires="indep")
def _(b, s, rng):
    b.literal("; swelling was noted on the ")
    s.anatomy(b)


@clause("cl_facility_generic_moved", ("FACILITY_GENERIC",))
def _(b, s, rng):
    b.literal(" and was moved to the ")
    s.facility_generic(b)


@clause("cl_facility_generic_admitted", ("FACILITY_GENERIC",), requires="indep")
def _(b, s, rng):
    b.literal("; a bed was found on the ")
    s.facility_generic(b)


@clause("cl_non_phi_documented", ("NON_PHI",))
def _(b, s, rng):
    b.literal(" and ")
    s.non_phi(b)
    b.literal(" was completed")


@clause("cl_disease_drug_combo", ("DISEASE", "DRUG"))
def _(b, s, rng):
    b.literal(" and was managed for ")
    s.disease(b)
    b.literal(" with ")
    s.drug(b)


@clause("cl_age_disease_combo", ("AGE", "DISEASE"), requires="indep")
def _(b, s, rng):
    b.literal(", ")
    s.age(b)
    b.literal(", presenting with ")
    s.disease(b)


# ---------------------------------------------------------------------------
# AMBIGUITY CLAUSES -- the hard cases.
#
# These deliberately place a surface form in a context that decides its type.
# `ambiguity_type` labels the phenomenon for stratified reporting only; it is
# never read back during generation and is withheld from the models (12.1).
# ---------------------------------------------------------------------------

AMBIGUITY_CLAUSES: list[Part] = []


def ambiguity_clause(name, phi_types, ambiguity_type):
    def deco(fn):
        AMBIGUITY_CLAUSES.append(Part(name, fn, phi_types, (), ambiguity_type))
        return fn

    return deco


@ambiguity_clause("am_person_disease_smear", ("PERSON", "DISEASE"), "person_disease")
def _(b, s, rng):
    pair = s.lex.person_disease[rng.randrange(len(s.lex.person_disease))]
    surname = s.lex.sample(s.lex.names_surname, s.rng)
    b.literal("Patient ")
    b.span(f"{pair.person_form} {surname}", "PERSON", ambiguity_type="person_disease")
    b.literal(" was reviewed; the smear confirmed ")
    b.span(pair.other_form, "DISEASE", ambiguity_type="person_disease")


@ambiguity_clause("am_person_disease_ward", ("PERSON", "DISEASE"), "person_disease")
def _(b, s, rng):
    pair = s.lex.person_disease[rng.randrange(len(s.lex.person_disease))]
    b.literal("The register lists ")
    b.span(pair.person_form, "PERSON", ambiguity_type="person_disease")
    b.literal(" on the ward while the notes record ")
    b.span(pair.other_form, "DISEASE", ambiguity_type="person_disease")
    b.literal(" as the working diagnosis")


@ambiguity_clause("am_person_drug_nested", ("PERSON", "DRUG"), "person_drug")
def _(b, s, rng):
    """Canonical 13.2 case: PERSON containing an inner DRUG span."""
    pair = s.lex.person_drug[rng.randrange(len(s.lex.person_drug))]
    surname = s.lex.sample(s.lex.names_surname, s.rng)
    b.literal("Pharmacy dispensed ")
    b.span(pair.other_form, "DRUG", ambiguity_type="person_drug")
    b.literal(" while staff nurse ")
    b.nested(
        f"{pair.person_form} {surname}",
        "PERSON",
        pair.person_form,
        "DRUG",
        outer_ambiguity="person_drug",
        inner_ambiguity="person_drug",
    )
    b.literal(" documented the dose")


@ambiguity_clause("am_person_drug_prescriber", ("DRUG", "PERSON"), "person_drug")
def _(b, s, rng):
    pair = s.lex.person_drug[rng.randrange(len(s.lex.person_drug))]
    b.literal("The prescription listed ")
    b.span(pair.other_form, "DRUG", ambiguity_type="person_drug")
    b.literal(" and the prescriber was Dr ")
    b.span(pair.person_form, "PERSON", ambiguity_type="person_drug")


@ambiguity_clause("am_eponym_vs_doctor", ("DISEASE", "PERSON"), "eponym")
def _(b, s, rng):
    pair = s.lex.person_disease[rng.randrange(len(s.lex.person_disease))]
    b.literal("Assessment suggests ")
    b.span(pair.other_form, "DISEASE", ambiguity_type="eponym")
    b.literal(" and follow-up was arranged with Dr ")
    b.span(pair.person_form, "PERSON", ambiguity_type="eponym")


@ambiguity_clause("am_eponym_sign", ("DISEASE",), "eponym")
def _(b, s, rng):
    eponym, kind = s.lex.eponyms[rng.randrange(len(s.lex.eponyms))]
    b.literal("The clinical officer elicited ")
    b.span(eponym, kind if kind in ("DISEASE", "NON_PHI") else "DISEASE",
           ambiguity_type="eponym")
    b.literal(" during the examination")


@ambiguity_clause("am_person_place_home", ("PERSON", "LOCATION"), "person_place")
def _(b, s, rng):
    pair = s.lex.person_place[rng.randrange(len(s.lex.person_place))]
    surname = s.lex.sample(s.lex.names_surname, s.rng)
    b.literal("Nurse ")
    b.span(f"{pair.person_form} {surname}", "PERSON", ambiguity_type="person_place")
    b.literal(" escorted the patient home to ")
    b.span(pair.other_form, "LOCATION", ambiguity_type="person_place")


@ambiguity_clause("am_person_place_origin", ("LOCATION", "PERSON"), "person_place")
def _(b, s, rng):
    pair = s.lex.person_place[rng.randrange(len(s.lex.person_place))]
    b.literal("The patient travelled from ")
    b.span(pair.other_form, "LOCATION", ambiguity_type="person_place")
    b.literal(" accompanied by ")
    # The collision is the point, but repeating the bare form twice reads as a
    # typo rather than as an ambiguity; a surname disambiguates the person while
    # keeping the shared token.
    surname = s.lex.sample(s.lex.names_surname, s.rng)
    b.span(f"{pair.person_form} {surname}", "PERSON", ambiguity_type="person_place")


@ambiguity_clause("am_role_ambiguous_pair", ("PERSON",), "role_ambiguous")
def _(b, s, rng):
    b.literal("Dr ")
    b.span(s.lex.sample(s.lex.names_surname, s.rng), "PERSON",
           ambiguity_type="role_ambiguous")
    b.literal(" reviewed ")
    b.span(s.lex.sample(s.lex.role_ambiguous, s.rng), "PERSON",
           ambiguity_type="role_ambiguous")
    b.literal(" in the afternoon clinic")


@ambiguity_clause("am_role_ambiguous_unclear", ("PERSON",), "role_ambiguous")
def _(b, s, rng):
    b.literal("The note simply records ")
    b.span(s.lex.sample(s.lex.role_ambiguous, s.rng), "PERSON",
           ambiguity_type="role_ambiguous")
    b.literal(" without stating whether this is the patient or the caller")


@ambiguity_clause("am_orthographic_diacritic", ("PERSON",), "orthographic")
def _(b, s, rng):
    base = s.lex.sample(s.lex.names_full, s.rng)
    parts = base.split(" ", 1)
    given, surname = (parts + ["Bello"])[:2]
    swaps = {"e": "é", "o": "ô", "a": "à", "u": "ù", "i": "í"}
    marked = given
    for plain, accented in swaps.items():
        if plain in given.lower():
            idx = given.lower().index(plain)
            marked = given[:idx] + accented + given[idx + 1 :]
            break
    b.literal("The intake register spells the name ")
    b.span(f"{marked} {surname}", "PERSON", ambiguity_type="orthographic")
    b.literal(" although the national card reads it differently")


@ambiguity_clause("am_orthographic_translit", ("PERSON",), "orthographic")
def _(b, s, rng):
    base = s.lex.sample(s.lex.names_full, s.rng)
    b.literal("Two spellings appear in the folder for ")
    b.span(base, "PERSON", ambiguity_type="orthographic")
    b.literal(" and the clerk could not confirm which matches the card")


# ---------------------------------------------------------------------------
# CONNECTIVES and TAILS -- structural filler that varies sentence length.
# ---------------------------------------------------------------------------

CONNECTIVES = [
    " The team agreed to continue observation.",
    " The plan was explained to the family at the bedside.",
    " Vitals remained stable through the shift.",
    " A repeat review was booked for the following week.",
    " The findings were entered into the facility register.",
    " Counselling was offered before discharge.",
    " The case was discussed with the medical officer on call.",
    " Investigations were requested and samples sent to the laboratory.",
    " The attendant was advised on danger signs.",
    " Transport to the referral facility was arranged.",
    " The drug chart was updated accordingly.",
    " Fluid balance was charted hourly.",
    " Infection prevention measures were reinforced.",
    " The patient was counselled on adherence.",
    " A follow-up home visit was scheduled.",
    " The scheme card was verified at the desk.",
]

TAILS = [
    " Documentation was completed before handover.",
    " No further action was required at this visit.",
    " The register was reconciled at the end of the shift.",
    " The folder was returned to the records department.",
    " The outcome was recorded as satisfactory.",
    " The entry was signed and dated.",
    " Nothing further was outstanding.",
    " The summary was filed with the discharge papers.",
]


# ---------------------------------------------------------------------------
# COMPOSITION
# ---------------------------------------------------------------------------


def _compatible(part: Part, register: str) -> bool:
    """A part with no declared register fits any; otherwise it must match."""
    return not part.register or register in part.register


@dataclass
class ComposedFrame:
    """One frame: a register plus the parts that build it.

    The identity used for diversity accounting is the tuple of part names, so
    two frames differing in any axis count as distinct templates.
    """

    register: str
    opening: Part
    clauses: tuple[Part, ...]
    n_connectives: int
    n_tails: int

    @property
    def name(self) -> str:
        parts = "+".join(c.name for c in self.clauses)
        return f"{self.register}:{self.opening.name}+{parts}:c{self.n_connectives}t{self.n_tails}"

    @property
    def phi_types(self) -> tuple[str, ...]:
        types = set(self.opening.phi_types)
        for c in self.clauses:
            types.update(c.phi_types)
        return tuple(sorted(types))

    @property
    def ambiguity_type(self) -> str:
        for c in self.clauses:
            if c.ambiguity_type != "none":
                return c.ambiguity_type
        return "none"

    def render(self, b: SpanBuilder, slots: "Slots", rng: random.Random) -> None:
        """Place this frame's text and spans on the builder."""
        self.opening.fn(b, slots, rng)
        for c in self.clauses:
            # An ambiguity clause is a full sentence of its own, so close the
            # opening before it rather than running the two together.
            # Clauses carry their own leading punctuation, so a previous
            # clause ending in "," would otherwise yield ",;" at the seam.
            # Removing the comma entirely avoids leaving " ;" behind.
            if b.peek_last_char() == "," and c.opens_with_punctuation:
                b.drop_last_char()
            if c.ambiguity_type != "none":
                last = b.peek_last_char()
                if last in ",;:":
                    b.replace_last_char(".")
                elif last not in ".!?":
                    b.literal(".")
                b.literal(" ")
            c.fn(b, slots, rng)
        # A clause may already have ended in punctuation (", 53 year old,"); adding
        # a period there yields ",." so we terminate only when needed.
        tail_char = b.peek_last_char()
        if tail_char in ",;:":
            b.replace_last_char(".")
        elif tail_char not in ".!?":
            b.literal(".")
        for _ in range(self.n_connectives):
            b.literal(CONNECTIVES[rng.randrange(len(CONNECTIVES))])
        for _ in range(self.n_tails):
            b.literal(TAILS[rng.randrange(len(TAILS))])


def _probe_leading_punctuation(lex, rng) -> None:
    """Record, once, which clauses begin with punctuation.

    Rendering each clause in isolation and inspecting its first character is
    more reliable than annotating 53 parts by hand and keeping the annotations
    in sync with the text.
    """
    from .spans import SpanBuilder

    for part in CLAUSES + AMBIGUITY_CLAUSES:
        probe = SpanBuilder()
        slots = Slots(lex, rng, {})
        try:
            part.fn(probe, slots, rng)
            rendered = probe.text_so_far()
        except Exception:
            rendered = ""
        part.opens_with_punctuation = bool(rendered) and rendered[0] in ",;:|"


_PROBED = False


def ensure_probed(lex, rng) -> None:
    global _PROBED
    if not _PROBED:
        _probe_leading_punctuation(lex, rng)
        _PROBED = True


def compose_frame(rng: random.Random, want: str = "any") -> ComposedFrame:
    """Draw one frame by sampling each axis independently.

    `want` steers toward REDACT-dominant or PRESERVE-dominant frames so the
    driver can hold the 55/45 line ratio.
    """
    register = REGISTERS[rng.randrange(len(REGISTERS))]
    openings = [o for o in OPENINGS if _compatible(o, register)]
    opening = openings[rng.randrange(len(openings))]

    # One in six sentences is built around a hard case.
    if rng.random() < 0.17:
        clauses = (AMBIGUITY_CLAUSES[rng.randrange(len(AMBIGUITY_CLAUSES))],)
    else:
        pool = [
            c
            for c in CLAUSES
            if _compatible(c, register)
            and (opening.continuation == "verb" or c.continuation == "indep")
        ]
        if want == "REDACT":
            pool = [c for c in pool if any(t in REDACT_SET for t in c.phi_types)] or pool
        elif want == "PRESERVE":
            pool = [c for c in pool if any(t in PRESERVE_SET for t in c.phi_types)] or pool
        n = 1 if rng.random() < 0.55 else 2
        chosen = []
        for i in range(n):
            # Only the first clause may consume a dangling subject; anything
            # after it has to stand on its own.
            candidates = pool if i == 0 else [c for c in pool if c.continuation == "indep"]
            if not candidates:
                break
            cand = candidates[rng.randrange(len(candidates))]
            if cand in chosen:
                continue
            # A sentence must not state two different ages for one patient, so a
            # phi_type that can only sensibly appear once is not repeated.
            already = {t for c in chosen for t in c.phi_types} | set(opening.phi_types)
            if any(t in already for t in cand.phi_types if t in SINGLETON_TYPES):
                continue
            chosen.append(cand)
        clauses = tuple(chosen)

    # Length distribution with a long tail past 60 tokens.
    roll = rng.random()
    if roll < 0.55:
        n_conn, n_tail = 0, rng.randrange(0, 2)
    elif roll < 0.88:
        n_conn, n_tail = rng.randrange(1, 3), rng.randrange(0, 2)
    else:
        n_conn, n_tail = rng.randrange(3, 7), rng.randrange(1, 3)

    return ComposedFrame(register, opening, clauses, n_conn, n_tail)


# Imported here rather than at module top to keep the schema import local.
from .schema import PRESERVE_TYPES as PRESERVE_SET  # noqa: E402
from .schema import REDACT_TYPES as REDACT_SET  # noqa: E402


def count_possible_frames() -> dict:
    """Report the size of the composed frame space, per register.

    This is the number of distinct *skeletons*; the number of distinct
    *sentences* is far larger because every slot draws from a lexicon.
    """
    total = 0
    per_register = {}
    for register in REGISTERS:
        openings = len([o for o in OPENINGS if _compatible(o, register)])
        clauses = len([c for c in CLAUSES if _compatible(c, register)])
        # single-clause and ordered two-clause combinations, plus ambiguity ones
        clause_combos = clauses + clauses * (clauses - 1) + len(AMBIGUITY_CLAUSES)
        # length shapes: (n_connectives, n_tails) pairs actually reachable
        length_shapes = 2 + 2 * 2 + 4 * 2
        n = openings * clause_combos * length_shapes
        per_register[register] = n
        total += n
    return {"per_register": per_register, "total_frames": total}


# ---------------------------------------------------------------------------
# ADDITIONAL CLAUSES for thin types.
#
# The first pass left some types with only one or two clauses, which meant every
# frame carrying that type was a large share of it -- a Section 15 template
# violation caused by the part library, not by the sampler.  These even out the
# per-type clause counts.
# ---------------------------------------------------------------------------


@clause("cl_age_stated", ("AGE",), requires="indep")
def _(b, s, rng):
    b.literal("; the stated age is ")
    s.age(b, bare=True)


@clause("cl_age_recorded", ("AGE",), requires="indep")
def _(b, s, rng):
    b.literal("; the card records ")
    s.age(b, bare=True)


@clause("cl_age_estimated", ("AGE",), requires="indep")
def _(b, s, rng):
    b.literal("; the age was estimated as ")
    s.age(b, bare=True)
    b.literal(" because no birth record was available")


@clause("cl_age_field", ("AGE",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | Age: ")
    s.age(b, bare=True)


@clause("cl_age_discrepancy", ("AGE",), requires="indep")
def _(b, s, rng):
    b.literal("; the register and the card disagree, with the card giving ")
    s.age(b, bare=True)


@clause("cl_anatomy_referred_pain", ("ANATOMY",), requires="indep")
def _(b, s, rng):
    b.literal("; pain was referred to the ")
    s.anatomy(b)


@clause("cl_anatomy_normal", ("ANATOMY",), requires="indep")
def _(b, s, rng):
    b.literal("; the ")
    s.anatomy(b)
    b.literal(" appeared normal on palpation")


@clause("cl_anatomy_imaging", ("ANATOMY",), requires="indep")
def _(b, s, rng):
    b.literal("; imaging of the ")
    s.anatomy(b)
    b.literal(" was requested")


@clause("cl_anatomy_dressing", ("ANATOMY",))
def _(b, s, rng):
    b.literal(" and a dressing was applied over the ")
    s.anatomy(b)


@clause("cl_non_phi_handover", ("NON_PHI",), requires="indep")
def _(b, s, rng):
    b.literal("; ")
    s.non_phi(b)
    b.literal(" was scheduled for the next shift")


@clause("cl_non_phi_pending", ("NON_PHI",), requires="indep")
def _(b, s, rng):
    b.literal("; ")
    s.non_phi(b)
    b.literal(" remains outstanding")


@clause("cl_non_phi_offered", ("NON_PHI",))
def _(b, s, rng):
    b.literal(" and was offered ")
    s.non_phi(b)


@clause("cl_non_phi_declined", ("NON_PHI",), requires="indep")
def _(b, s, rng):
    b.literal("; the attendant declined ")
    s.non_phi(b)
    b.literal(" at this visit")


@clause("cl_facility_generic_transferred", ("FACILITY_GENERIC",))
def _(b, s, rng):
    b.literal(" and was transferred to the ")
    s.facility_generic(b)


@clause("cl_facility_generic_awaiting", ("FACILITY_GENERIC",), requires="indep")
def _(b, s, rng):
    b.literal("; the patient is awaiting a bed on the ")
    s.facility_generic(b)


@clause("cl_facility_generic_full", ("FACILITY_GENERIC",), requires="indep")
def _(b, s, rng):
    b.literal("; the ")
    s.facility_generic(b)
    b.literal(" was full at the time of admission")


@clause("cl_facility_generic_field", ("FACILITY_GENERIC",), ("structured",), requires="indep")
def _(b, s, rng):
    b.literal(" | Ward: ")
    s.facility_generic(b)


@clause("cl_national_id_verified", ("NATIONAL_ID",), requires="indep")
def _(b, s, rng):
    b.literal("; the identifier ")
    s.national_id(b)
    b.literal(" was verified against the card")


@clause("cl_national_id_scheme", ("NATIONAL_ID",), requires="indep")
def _(b, s, rng):
    b.literal("; the scheme number quoted was ")
    s.national_id(b)


@clause("cl_national_id_mismatch", ("NATIONAL_ID",), requires="indep")
def _(b, s, rng):
    b.literal("; the number on file, ")
    s.national_id(b)
    b.literal(", does not match the one presented")


@clause("cl_address_field_visit", ("ADDRESS",), requires="indep")
def _(b, s, rng):
    b.literal("; the household was located at ")
    s.address(b)


@clause("cl_address_moved", ("ADDRESS",), requires="indep")
def _(b, s, rng):
    b.literal("; the family has since moved to ")
    s.address(b)


@clause("cl_location_born", ("LOCATION",), requires="indep")
def _(b, s, rng):
    b.literal("; the patient was born in ")
    s.location(b)


@clause("cl_location_outreach", ("LOCATION",), requires="indep")
def _(b, s, rng):
    b.literal("; the outreach team covers ")
    s.location(b)


@clause("cl_location_transferred", ("LOCATION",))
def _(b, s, rng):
    b.literal(" and was transferred to ")
    s.facility_named(b)


@clause("cl_date_surgery", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal("; surgery is booked for ")
    s.date(b)


@clause("cl_date_last_seen", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal("; the patient was last seen on ")
    s.date(b)


@clause("cl_date_onset", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal("; symptoms began around ")
    s.date(b)


@clause("cl_mrn_cross_ref", ("MEDICAL_RECORD",), requires="indep")
def _(b, s, rng):
    b.literal("; cross-referenced with ")
    s.medical_record(b)


@clause("cl_mrn_duplicate", ("MEDICAL_RECORD",), requires="indep")
def _(b, s, rng):
    b.literal("; a duplicate folder ")
    s.medical_record(b)
    b.literal(" was found in the registry")


@clause("cl_drug_changed", ("DRUG",), requires="indep")
def _(b, s, rng):
    b.literal("; the regimen was changed to ")
    s.drug(b)


@clause("cl_drug_allergy", ("DRUG",), requires="indep")
def _(b, s, rng):
    b.literal("; a reaction to ")
    s.drug(b)
    b.literal(" was documented previously")


@clause("cl_disease_comorbid", ("DISEASE",), requires="indep")
def _(b, s, rng):
    b.literal("; the patient is also known to have ")
    s.disease(b)


@clause("cl_disease_ruled_out", ("DISEASE",), requires="indep")
def _(b, s, rng):
    b.literal("; ")
    s.disease(b)
    b.literal(" was ruled out on investigation")


@clause("cl_person_referred_by", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; the referring officer was ")
    s.person(b)


@clause("cl_person_interpreter", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; interpretation was provided by ")
    s.person(b)


@clause("cl_phone_alternate", ("PHONE",), requires="indep")
def _(b, s, rng):
    b.literal("; an alternate number, ")
    s.phone(b)
    b.literal(", was given by the neighbour")


@clause("cl_email_none", ("EMAIL",), requires="indep")
def _(b, s, rng):
    b.literal("; correspondence should go to ")
    s.email(b)
    b.literal(" until further notice")


# ---------------------------------------------------------------------------
# EXPANSION SET — additional openings and clauses.
#
# Row count alone does not create diversity: drawing 100M sentences from the
# existing skeletons reuses each one many times over.  These parts widen the
# structural space itself, and they deliberately reach into clinical settings
# the first pass under-covered: outreach and campaign work, maternity and
# newborn care, TB and HIV programmes, pharmacy and laboratory, mortuary and
# records, theatre, and the insurance/scheme desk.
# ---------------------------------------------------------------------------


# -- narrative openings ------------------------------------------------------

@opening("op_outreach_camp", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("At the outreach camp the screening team registered ")
    s.person(b)


@opening("op_mobile_clinic", ("narrative",), ("PERSON", "LOCATION"), continuation="indep")
def _(b, s, rng):
    b.literal("The mobile clinic team saw ")
    s.person(b)
    b.literal(" during the visit to ")
    s.location(b)


@opening("op_tb_programme", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The TB programme officer traced ")
    s.person(b)


@opening("op_art_clinic", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("At the ART clinic the counsellor reviewed ")
    s.person(b)


@opening("op_labour_ward", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The midwife admitted ")
    s.person(b)
    b.literal(" to the labour ward")


@opening("op_newborn", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The newborn of ")
    s.person(b)
    b.literal(" was reviewed by the paediatric team")


@opening("op_theatre_list", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The theatre list for the morning included ")
    s.person(b)


@opening("op_lab_specimen", ("narrative",), ("MEDICAL_RECORD",), continuation="indep")
def _(b, s, rng):
    b.literal("The laboratory received a specimen labelled ")
    s.medical_record(b)


@opening("op_pharmacy_counter", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("At the pharmacy counter the dispenser served ")
    s.person(b)


@opening("op_scheme_desk", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The insurance desk verified cover for ")
    s.person(b)


@opening("op_triage_nurse", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The triage nurse assessed ")
    s.person(b)
    b.literal(" on arrival")


@opening("op_ambulance", ("narrative",), ("PERSON", "LOCATION"), continuation="indep")
def _(b, s, rng):
    b.literal("The ambulance crew brought ")
    s.person(b)
    b.literal(" from ")
    s.location(b)


@opening("op_school_health", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The school health team screened ")
    s.person(b)


@opening("op_nutrition", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The nutrition officer enrolled ")
    s.person(b)
    b.literal(" in the feeding programme")


@opening("op_physio", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The physiotherapist reviewed ")
    s.person(b)


@opening("op_mental_health", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The mental health nurse followed up ")
    s.person(b)


@opening("op_dental", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("The dental officer treated ")
    s.person(b)


@opening("op_eye_camp", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("At the eye camp the ophthalmic nurse examined ")
    s.person(b)


@opening("op_records_audit", ("narrative",), ("MEDICAL_RECORD",), continuation="indep")
def _(b, s, rng):
    b.literal("The records audit flagged file ")
    s.medical_record(b)


@opening("op_consultant_opinion", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("A consultant opinion was sought for ")
    s.person(b)


@opening("op_second_visit", ("narrative",), ("PERSON", "DATE"), continuation="indep")
def _(b, s, rng):
    b.literal("")
    s.person(b)
    b.literal(" returned for review on ")
    s.date(b)


@opening("op_defaulter_traced", ("narrative",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Treatment defaulter tracing located ")
    s.person(b)


# -- telegraphic openings ----------------------------------------------------

@opening("op_tel_review", ("telegraphic",), (), continuation="indep")
def _(b, s, rng):
    b.literal("For review")


@opening("op_tel_plan", ("telegraphic",), ("DRUG",), continuation="indep")
def _(b, s, rng):
    b.literal("Plan: continue ")
    s.drug(b)


@opening("op_tel_imp", ("telegraphic",), ("DISEASE",), continuation="indep")
def _(b, s, rng):
    b.literal("Imp: ")
    s.disease(b)


@opening("op_tel_obs", ("telegraphic",), (), continuation="indep")
def _(b, s, rng):
    b.literal(f"BP {rng.randrange(90,181)}/{rng.randrange(50,111)}, PR {rng.randrange(50,131)}")


@opening("op_tel_seen", ("telegraphic",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Seen by Dr ")
    s.person_surname(b)


@opening("op_tel_admit", ("telegraphic",), ("FACILITY_GENERIC",), continuation="indep")
def _(b, s, rng):
    b.literal("Admit ")
    s.facility_generic(b)


# -- structured openings -----------------------------------------------------

@opening("op_field_visit", ("structured",), ("DATE",), continuation="indep")
def _(b, s, rng):
    b.literal("Visit date: ")
    s.date(b)


@opening("op_field_guardian", ("structured",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Guardian: ")
    s.person(b)


@opening("op_field_scheme", ("structured",), ("NATIONAL_ID",), continuation="indep")
def _(b, s, rng):
    b.literal("Scheme No: ")
    s.national_id(b)


@opening("op_field_address", ("structured",), ("ADDRESS",), continuation="indep")
def _(b, s, rng):
    b.literal("Residence: ")
    s.address(b)


@opening("op_field_referred_by", ("structured",), ("LOCATION",), continuation="indep")
def _(b, s, rng):
    b.literal("Referred by: ")
    s.facility_named(b)


# -- handover openings -------------------------------------------------------

@opening("op_handover_theatre", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("For theatre: ")
    s.person(b)


@opening("op_handover_discharge", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("For discharge: ")
    s.person(b)


@opening("op_handover_bloods", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Bloods pending: ")
    s.person(b)


@opening("op_handover_nbm", ("handover",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("Nil by mouth: ")
    s.person(b)


# -- letter openings ---------------------------------------------------------

@opening("op_letter_grateful", ("letter",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("I would be grateful if you could review ")
    s.person(b)


@opening("op_letter_transfer", ("letter",), ("PERSON", "LOCATION"), continuation="indep")
def _(b, s, rng):
    b.literal("We are transferring ")
    s.person(b)
    b.literal(" to ")
    s.facility_named(b)


@opening("op_letter_summary", ("letter",), ("PERSON",), continuation="indep")
def _(b, s, rng):
    b.literal("This discharge summary concerns ")
    s.person(b)


@opening("op_letter_followup", ("letter",), ("PERSON", "DATE"), continuation="indep")
def _(b, s, rng):
    b.literal("Please review ")
    s.person(b)
    b.literal(" at the clinic on ")
    s.date(b)


# -- expansion clauses: PHI-bearing -----------------------------------------

@clause("cl_phone_switchboard", ("PHONE",), requires="indep")
def _(b, s, rng):
    b.literal("; the switchboard holds ")
    s.phone(b)
    b.literal(" as the daytime number")


@clause("cl_phone_neighbour", ("PHONE",), requires="indep")
def _(b, s, rng):
    b.literal("; a neighbour can be reached on ")
    s.phone(b)


@clause("cl_phone_whatsapp", ("PHONE",), requires="indep")
def _(b, s, rng):
    b.literal("; results were sent by message to ")
    s.phone(b)


@clause("cl_phone_unreachable", ("PHONE",), requires="indep")
def _(b, s, rng):
    b.literal("; repeated calls to ")
    s.phone(b)
    b.literal(" went unanswered")


@clause("cl_email_lab", ("EMAIL",), requires="indep")
def _(b, s, rng):
    b.literal("; the laboratory report goes to ")
    s.email(b)


@clause("cl_email_employer", ("EMAIL",), requires="indep")
def _(b, s, rng):
    b.literal("; the employer contact given was ")
    s.email(b)


@clause("cl_email_appointment", ("EMAIL",), requires="indep")
def _(b, s, rng):
    b.literal("; the appointment reminder was emailed to ")
    s.email(b)


@clause("cl_date_next_dose", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal("; the next dose is due on ")
    s.date(b)


@clause("cl_date_discharged", ("DATE",))
def _(b, s, rng):
    b.literal(" and was discharged on ")
    s.date(b)


@clause("cl_date_edd", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal("; the expected date of delivery is ")
    s.date(b)


@clause("cl_date_test", ("DATE",), requires="indep")
def _(b, s, rng):
    b.literal("; the sample was collected on ")
    s.date(b)


@clause("cl_person_witness", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; consent was witnessed by ")
    s.person(b)


@clause("cl_person_treated_by", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; the procedure was performed by Dr ")
    s.person_surname(b)


@clause("cl_person_accompanied", ("PERSON",))
def _(b, s, rng):
    b.literal(" and was accompanied by ")
    s.person(b)


@clause("cl_person_traced_by", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; tracing was done by community volunteer ")
    s.person(b)


@clause("cl_person_donor", ("PERSON",), requires="indep")
def _(b, s, rng):
    b.literal("; the blood donor was recorded as ")
    s.person(b)


@clause("cl_location_catchment", ("LOCATION",), requires="indep")
def _(b, s, rng):
    b.literal("; the household falls in the ")
    s.location(b)
    b.literal(" catchment")


@clause("cl_location_workplace", ("LOCATION",), requires="indep")
def _(b, s, rng):
    b.literal("; the patient works in ")
    s.location(b)


@clause("cl_location_returned_from", ("LOCATION",), requires="indep")
def _(b, s, rng):
    b.literal("; there is a history of travel from ")
    s.location(b)


@clause("cl_address_landmark", ("ADDRESS",), requires="indep")
def _(b, s, rng):
    b.literal("; the home was described as ")
    s.address(b)


@clause("cl_mrn_theatre", ("MEDICAL_RECORD",), requires="indep")
def _(b, s, rng):
    b.literal("; the theatre register entry is ")
    s.medical_record(b)


@clause("cl_mrn_lab", ("MEDICAL_RECORD",), requires="indep")
def _(b, s, rng):
    b.literal("; the laboratory accession number is ")
    s.medical_record(b)


@clause("cl_national_id_guardian", ("NATIONAL_ID",), requires="indep")
def _(b, s, rng):
    b.literal("; the guardian presented identifier ")
    s.national_id(b)


# -- expansion clauses: PRESERVE --------------------------------------------

@clause("cl_drug_dose_adjusted", ("DRUG",), requires="indep")
def _(b, s, rng):
    b.literal("; the dose of ")
    s.drug(b)
    b.literal(" was adjusted for weight")


@clause("cl_drug_substituted", ("DRUG",), requires="indep")
def _(b, s, rng):
    b.literal("; ")
    s.drug(b)
    b.literal(" was substituted from the essential medicines list")


@clause("cl_drug_counselled", ("DRUG",))
def _(b, s, rng):
    b.literal(" and was counselled on taking ")
    s.drug(b)
    b.literal(" with food")


@clause("cl_drug_refused", ("DRUG",), requires="indep")
def _(b, s, rng):
    b.literal("; the attendant declined ")
    s.drug(b)


@clause("cl_disease_notified", ("DISEASE",), requires="indep")
def _(b, s, rng):
    b.literal("; ")
    s.disease(b)
    b.literal(" was notified to the surveillance officer")


@clause("cl_disease_screened", ("DISEASE",), requires="indep")
def _(b, s, rng):
    b.literal("; screening for ")
    s.disease(b)
    b.literal(" was negative")


@clause("cl_disease_history", ("DISEASE",), requires="indep")
def _(b, s, rng):
    b.literal("; there is a past history of ")
    s.disease(b)


@clause("cl_disease_outbreak", ("DISEASE",), requires="indep")
def _(b, s, rng):
    b.literal("; the case was linked to the ")
    s.disease(b)
    b.literal(" outbreak investigation")


@clause("cl_anatomy_wound", ("ANATOMY",), requires="indep")
def _(b, s, rng):
    b.literal("; a wound over the ")
    s.anatomy(b)
    b.literal(" was cleaned and dressed")


@clause("cl_anatomy_range", ("ANATOMY",), requires="indep")
def _(b, s, rng):
    b.literal("; range of movement at the ")
    s.anatomy(b)
    b.literal(" was limited")


@clause("cl_anatomy_scan", ("ANATOMY",), requires="indep")
def _(b, s, rng):
    b.literal("; an ultrasound of the ")
    s.anatomy(b)
    b.literal(" was reported as normal")


@clause("cl_facility_generic_discharged", ("FACILITY_GENERIC",), requires="indep")
def _(b, s, rng):
    b.literal("; the patient was discharged from the ")
    s.facility_generic(b)


@clause("cl_facility_generic_cleaned", ("FACILITY_GENERIC",), requires="indep")
def _(b, s, rng):
    b.literal("; the ")
    s.facility_generic(b)
    b.literal(" was fumigated overnight")


@clause("cl_age_weight_band", ("AGE",), requires="indep")
def _(b, s, rng):
    b.literal("; dosing followed the band for ")
    s.age(b)


@clause("cl_age_at_diagnosis", ("AGE",), requires="indep")
def _(b, s, rng):
    b.literal("; the age at diagnosis was ")
    s.age(b, bare=True)


@clause("cl_non_phi_audit", ("NON_PHI",), requires="indep")
def _(b, s, rng):
    b.literal("; ")
    s.non_phi(b)
    b.literal(" was included in the monthly audit")


@clause("cl_non_phi_training", ("NON_PHI",), requires="indep")
def _(b, s, rng):
    b.literal("; staff training on ")
    s.non_phi(b)
    b.literal(" was completed")


@clause("cl_non_phi_reinforced", ("NON_PHI",))
def _(b, s, rng):
    b.literal(" and ")
    s.non_phi(b)
    b.literal(" was reinforced with the team")


# -- expansion: additional hard cases ---------------------------------------

@ambiguity_clause("am_person_disease_register", ("PERSON", "DISEASE"), "person_disease")
def _(b, s, rng):
    pair = s.lex.person_disease[rng.randrange(len(s.lex.person_disease))]
    surname = s.lex.sample(s.lex.names_surname, s.rng)
    b.literal("The surveillance form names ")
    b.span(f"{pair.person_form} {surname}", "PERSON", ambiguity_type="person_disease")
    b.literal(" as the index case while the diagnosis field reads ")
    b.span(pair.other_form, "DISEASE", ambiguity_type="person_disease")


@ambiguity_clause("am_person_drug_chart", ("DRUG", "PERSON"), "person_drug")
def _(b, s, rng):
    pair = s.lex.person_drug[rng.randrange(len(s.lex.person_drug))]
    surname = s.lex.sample(s.lex.names_surname, s.rng)
    b.literal("The drug chart shows ")
    b.span(pair.other_form, "DRUG", ambiguity_type="person_drug")
    b.literal(" countersigned by Sister ")
    b.nested(
        f"{pair.person_form} {surname}",
        "PERSON",
        pair.person_form,
        "DRUG",
        outer_ambiguity="person_drug",
        inner_ambiguity="person_drug",
    )


@ambiguity_clause("am_eponym_investigation", ("DISEASE", "PERSON"), "eponym")
def _(b, s, rng):
    pair = s.lex.person_disease[rng.randrange(len(s.lex.person_disease))]
    b.literal("Investigations were requested to exclude ")
    b.span(pair.other_form, "DISEASE", ambiguity_type="eponym")
    b.literal(", and the request was signed by Dr ")
    b.span(pair.person_form, "PERSON", ambiguity_type="eponym")


@ambiguity_clause("am_person_place_ward", ("PERSON", "LOCATION"), "person_place")
def _(b, s, rng):
    pair = s.lex.person_place[rng.randrange(len(s.lex.person_place))]
    surname = s.lex.sample(s.lex.names_surname, s.rng)
    b.literal("The admission book lists ")
    b.span(f"{pair.person_form} {surname}", "PERSON", ambiguity_type="person_place")
    b.literal(" with home district recorded as ")
    b.span(pair.other_form, "LOCATION", ambiguity_type="person_place")


@ambiguity_clause("am_role_ambiguous_caller", ("PERSON",), "role_ambiguous")
def _(b, s, rng):
    b.literal("The entry records only ")
    b.span(s.lex.sample(s.lex.role_ambiguous, s.rng), "PERSON",
           ambiguity_type="role_ambiguous")
    b.literal(", so it is unclear whether this is the patient or the person who called")


@ambiguity_clause("am_orthographic_two_files", ("PERSON",), "orthographic")
def _(b, s, rng):
    base = s.lex.sample(s.lex.names_full, s.rng)
    b.literal("Two folders exist under variant spellings of ")
    b.span(base, "PERSON", ambiguity_type="orthographic")
    b.literal(" and the registry could not confirm which is current")


# Additional connectives and tails, so the trailing clauses vary as much as the
# PHI-bearing ones.
CONNECTIVES.extend([
    " The community health worker was asked to follow up at home.",
    " The case was entered into the facility register the same day.",
    " Stock levels were checked before dispensing.",
    " The attendant was shown how to complete the card.",
    " Transport arrangements were confirmed with the family.",
    " The supervising officer countersigned the entry.",
    " A repeat sample was requested from the laboratory.",
    " The outreach schedule was adjusted accordingly.",
    " Health education was given on danger signs.",
    " The referral form was completed in duplicate.",
    " The consent form was filed with the notes.",
    " Weight and height were recorded on the growth chart.",
])

TAILS.extend([
    " The file was returned to the shelf.",
    " No complications were recorded.",
    " The entry was checked against the daily tally.",
    " The shift closed without incident.",
    " The register was signed by the officer in charge.",
    " Follow-up was left open pending results.",
])
