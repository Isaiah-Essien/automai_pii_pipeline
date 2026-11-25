"""Put TRAINING/ on sys.path so scripts can import contextual_phi without pip install."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_training_package_on_path() -> Path:
    """
    Add the TRAINING directory to sys.path once.

    Returns:
        The TRAINING root path (parent of contextual_phi/).
    """
    training_root = Path(__file__).resolve().parents[1]
    training_root_str = str(training_root)
    if training_root_str not in sys.path:
        sys.path.insert(0, training_root_str)
    return training_root