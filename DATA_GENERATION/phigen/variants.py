"""Surface-form generators for PHONE and EMAIL (Section 6).

Each generator returns the literal text to place plus the `surface_form` tag
that goes in the metadata.  The four families -- standard, local, spoken, mixed
-- each have to reach 15 percent of their type, so the caller drives the choice
of family rather than letting it fall out of a single random draw here.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

DIGIT_WORDS = {
    "0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
    "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine",
}

# Country calling codes and national prefixes for the target regions.
COUNTRY_CODES = {
    "ng": ("+234", "0", ["803", "805", "806", "810", "812", "813", "814", "816", "703", "706"]),
    "ke": ("+254", "0", ["701", "702", "710", "711", "720", "721", "722", "733", "740", "748"]),
    "rw": ("+250", "0", ["780", "781", "782", "783", "788", "789", "725", "726", "727", "728"]),
    "gh": ("+233", "0", ["200", "240", "244", "246", "540", "544", "550", "554", "570", "590"]),
    "tz": ("+255", "0", ["712", "713", "714", "715", "754", "755", "765", "767", "784", "789"]),
}

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "email.com"]
ORG_DOMAINS = [
    "hospital.ng", "clinic.ke", "health.rw", "teachinghospital.ng", "medcentre.gh",
    "referral.tz", "healthpost.ke", "district.rw", "generalhospital.ng", "care.gh",
]

PHONE_FAMILIES = ("standard", "local", "spoken", "mixed")
EMAIL_FAMILIES = ("standard", "spoken", "mixed", "local")


@dataclass(frozen=True)
class Variant:
    """A rendered surface form and the tag describing how it was rendered."""

    text: str
    surface_form: str


def _subscriber_digits(rng: random.Random) -> str:
    return "".join(str(rng.randrange(10)) for _ in range(7))


def spell_digits(digits: str) -> str:
    """Render a digit string as spoken words: '0812' -> 'zero eight one two'."""
    return " ".join(DIGIT_WORDS[d] for d in digits if d.isdigit())


def make_phone(rng: random.Random, family: str, region: str = "ng") -> Variant:
    """Build one PHONE surface form in the requested family."""
    if family not in PHONE_FAMILIES:
        raise ValueError(f"unknown phone family {family!r}")
    cc, natl, prefixes = COUNTRY_CODES.get(region, COUNTRY_CODES["ng"])
    prefix = prefixes[rng.randrange(len(prefixes))]
    sub = _subscriber_digits(rng)

    if family == "standard":
        # +234 812 957 4830
        text = f"{cc} {prefix} {sub[:3]} {sub[3:]}"
    elif family == "local":
        # 08129574830
        text = f"{natl}{prefix}{sub}"
    elif family == "spoken":
        # zero eight one two nine five seven four eight three zero
        text = spell_digits(f"{natl}{prefix}{sub}")
    else:  # mixed: part written, part spoken
        style = rng.randrange(3)
        if style == 0:
            text = f"{cc} {prefix} {spell_digits(sub)}"
        elif style == 1:
            text = f"{natl}{prefix} {spell_digits(sub)}"
        else:
            text = f"{spell_digits(natl + prefix)} {sub[:3]} {sub[3:]}"
    return Variant(text=text, surface_form=family)


def _local_part(rng: random.Random, given: str, surname: str) -> tuple[str, str]:
    """Return (written_local_part, dotted_words) for an email address.

    The bare-given-name style is deliberately rare: short names like "zola"
    otherwise collide across many different people and concentrate a single
    address well above its Section 15 share.
    """
    g, s = given.lower(), surname.lower()
    style = rng.randrange(8)
    if style == 0:
        return g, g
    if style in (1, 2):
        return f"{g}.{s}", f"{g} dot {s}"
    if style == 3:
        return f"{g}{s[0]}", f"{g}{s[0]}"
    if style == 4:
        return f"{g[0]}{s}", f"{g[0]}{s}"
    if style == 5:
        return f"{g}_{s}", f"{g} underscore {s}"
    if style == 6:
        n = rng.randrange(10, 100)
        return f"{g}.{s}{n}", f"{g} dot {s}{n}"
    n = rng.randrange(100, 1000)
    return f"{g}{n}", f"{g}{n}"


def make_email(rng: random.Random, family: str, given: str, surname: str) -> Variant:
    """Build one EMAIL surface form in the requested family."""
    if family not in EMAIL_FAMILIES:
        raise ValueError(f"unknown email family {family!r}")
    written, spoken_local = _local_part(rng, given, surname)

    if family == "standard":
        # victor.adeyemi@gmail.com
        domain = EMAIL_DOMAINS[rng.randrange(len(EMAIL_DOMAINS))]
        text = f"{written}@{domain}"
    elif family == "spoken":
        # victor at gmail dot com
        domain = EMAIL_DOMAINS[rng.randrange(len(EMAIL_DOMAINS))]
        host, tld = domain.rsplit(".", 1)
        text = f"{spoken_local} at {host} dot {tld}"
    elif family == "mixed":
        # victor dot adeyemi at hospital dot ng
        domain = ORG_DOMAINS[rng.randrange(len(ORG_DOMAINS))]
        host, tld = domain.rsplit(".", 1)
        text = f"{spoken_local} at {host} dot {tld}"
    else:  # local: organisational address written in full
        domain = ORG_DOMAINS[rng.randrange(len(ORG_DOMAINS))]
        text = f"{written}@{domain}"
    return Variant(text=text, surface_form=family)


def make_national_id(rng: random.Random, region: str = "ng") -> Variant:
    """NIN / Ghana Card / NIDA-style identifiers."""
    if region == "gh":
        text = f"GHA-{rng.randrange(100000000, 999999999)}-{rng.randrange(0, 10)}"
    elif region == "rw":
        text = f"1{rng.randrange(1980, 2006)}8{rng.randrange(1000000, 9999999)}{rng.randrange(10, 99)}"
    else:
        text = "".join(str(rng.randrange(10)) for _ in range(11))
    return Variant(text=text, surface_form="standard")


def make_medical_record(rng: random.Random) -> Variant:
    """MRN / hospital file / clinic registration numbers."""
    codes = ["KNH", "LUTH", "UCH", "CHUK", "KATH", "MNH", "UTH", "JOOTRH", "AKTH", "ABUTH"]
    code = codes[rng.randrange(len(codes))]
    style = rng.randrange(3)
    if style == 0:
        text = f"{code}-{rng.randrange(2015, 2026)}-{rng.randrange(10000, 99999)}"
    elif style == 1:
        text = f"{code}/{rng.randrange(100000, 999999)}"
    else:
        text = f"{code}{rng.randrange(1000000, 9999999)}"
    return Variant(text=text, surface_form="standard")


def make_date(rng: random.Random) -> Variant:
    """Person-linked dates in several written styles."""
    day, month, year = rng.randrange(1, 29), rng.randrange(1, 13), rng.randrange(1990, 2026)
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    style = rng.randrange(4)
    if style == 0:
        text = f"{day:02d}/{month:02d}/{year}"
    elif style == 1:
        text = f"{year}-{month:02d}-{day:02d}"
    elif style == 2:
        text = f"{day} {months[month - 1]} {year}"
    else:
        text = f"{months[month - 1]} {day}, {year}"
    return Variant(text=text, surface_form="standard")


def make_address(rng: random.Random, place: str) -> Variant:
    """Street / compound / house-number addresses."""
    n = rng.randrange(1, 300)
    kinds = ["Street", "Road", "Close", "Crescent", "Avenue", "Lane"]
    style = rng.randrange(3)
    if style == 0:
        text = f"{n} {place} {kinds[rng.randrange(len(kinds))]}"
    elif style == 1:
        text = f"House {n}, {place}"
    else:
        text = f"No. {n} {place} {kinds[rng.randrange(len(kinds))]}"
    return Variant(text=text, surface_form="standard")


def make_age(rng: random.Random) -> Variant:
    """AGE is always PRESERVE -- numeric age expressions only."""
    n = rng.randrange(1, 96)
    style = rng.randrange(4)
    if style == 0:
        text = f"{n}-year-old"
    elif style == 1:
        text = f"{n} years"
    elif style == 2:
        text = f"aged {n}"
    else:
        text = f"{n} year old"
    return Variant(text=text, surface_form="standard")
