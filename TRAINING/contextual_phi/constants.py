"""Shared labels and environment keys for the de-identification training pipeline."""

from __future__ import annotations

import os
from typing import Final, Set

# Types we treat as PHI in Stage 1 BIO tagging (high-recall NER).
REDACT_ENTITY_TYPES: Final[Set[str]] = {
    "PERSON",
    "PHONE",
    "EMAIL",
    "DATE",
    "LOCATION",
    "ADDRESS",
    "NATIONAL_ID",
    "MEDICAL_RECORD",
}

VALID_DECISIONS: Final[Set[str]] = {"REDACT", "PRESERVE"}

# Override shard/checkpoint roots without changing code (local HDD or Colab Drive).
PROJECT_ROOT_ENV: Final[str] = "PHI_DEID_PROJECT_ROOT"


def project_root_from_env() -> str | None:
    """
    Read the optional project root from the environment.

    Returns:
        The path string if PHI_DEID_PROJECT_ROOT is set, else None.
    """
    return os.environ.get(PROJECT_ROOT_ENV)