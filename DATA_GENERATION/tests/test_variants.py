"""Tests for PHONE and EMAIL surface-form families."""

import random

import pytest

from phigen.variants import (
    EMAIL_FAMILIES,
    PHONE_FAMILIES,
    make_age,
    make_email,
    make_phone,
    spell_digits,
)


def test_spell_digits():
    assert spell_digits("0812") == "zero eight one two"
    assert spell_digits("+234") == "two three four"  # non-digits are skipped


@pytest.mark.parametrize("family", PHONE_FAMILIES)
def test_phone_families_render_and_tag(family):
    rng = random.Random(3)
    v = make_phone(rng, family)
    assert v.surface_form == family
    assert v.text.strip()


def test_phone_standard_and_local_shapes():
    rng = random.Random(11)
    assert make_phone(rng, "standard").text.startswith("+")
    local = make_phone(rng, "local").text
    assert local.isdigit() and local.startswith("0")


def test_phone_spoken_has_no_digits():
    rng = random.Random(5)
    assert not any(c.isdigit() for c in make_phone(rng, "spoken").text)


@pytest.mark.parametrize("family", EMAIL_FAMILIES)
def test_email_families_render_and_tag(family):
    rng = random.Random(3)
    v = make_email(rng, family, "Victor", "Adeyemi")
    assert v.surface_form == family
    assert v.text.strip()


def test_email_spoken_has_no_at_symbol():
    rng = random.Random(9)
    v = make_email(rng, "spoken", "Victor", "Adeyemi")
    assert "@" not in v.text and " at " in v.text and " dot " in v.text


def test_email_standard_has_at_symbol():
    rng = random.Random(9)
    assert "@" in make_email(rng, "standard", "Victor", "Adeyemi").text


def test_unknown_family_is_rejected():
    rng = random.Random(1)
    with pytest.raises(ValueError):
        make_phone(rng, "telepathy")
    with pytest.raises(ValueError):
        make_email(rng, "telepathy", "A", "B")


def test_age_is_numeric_expression():
    rng = random.Random(4)
    for _ in range(50):
        assert any(c.isdigit() for c in make_age(rng).text)
