"""Configuration loading.

Config is JSON rather than YAML so the pipeline runs with no third-party
dependency beyond pytest for the test suite.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DiversityConfig:
    max_template_share_within_phi_type: float = 0.005
    max_lexical_entry_share_within_type: float = 0.001
    min_lexicon_entries: int = 2000
    long_tail_token_target: int = 60
    min_long_tail_share: float = 0.02
    min_variant_family_share: float = 0.15
    # Types drawn from a closed vocabulary cannot meet a share-based ceiling:
    # there are only ~95 human ages and ~78 body parts, so a single entry is
    # necessarily well above 0.1 percent of its type.  Padding these with
    # invented entries would teach the model a false distribution, so they are
    # exempted deliberately and the exemption is recorded in the report.
    lexical_ceiling_exempt_types: tuple[str, ...] = (
        "AGE",
        "ANATOMY",
        "NON_PHI",
        "FACILITY_GENERIC",
    )
    # Surface forms that collide by design (Malaria the name vs malaria the
    # disease).  Real collisions are finite -- there are perhaps a few hundred
    # worldwide -- and they *should* recur, since recurrence is what makes the
    # hard case learnable.
    exempt_ambiguous_entries: bool = True


@dataclass
class Config:
    seed: int = 20260827
    target_lines: int = 1000
    # First sentence_id to emit.  A corpus built in several passes must keep ids
    # globally consecutive with no duplicates (§14.2), so a later pass starts at
    # one past the highest id the previous pass reached rather than back at 1.
    start_sentence_id: int = 1
    # When true, every emitted line gets its own consecutive sentence_id and the
    # sentence's own id moves to `group_id`.  The schema's default (§7) shares
    # one sentence_id across a sentence's spans; this produces the flattened
    # layout instead, matching a corpus that was renumbered after the fact.
    id_per_line: bool = False
    decision_mix: dict[str, float] = field(
        default_factory=lambda: {"REDACT": 0.55, "PRESERVE": 0.45}
    )
    decision_mix_tolerance: float = 0.005
    language_mix: dict[str, float] = field(default_factory=lambda: {"en": 1.0})
    code_switch_rate: float = 0.0
    source: str = "synthetic"
    shard_lines: int = 250000
    negatives_ratio: float = 0.30
    diversity: DiversityConfig = field(default_factory=DiversityConfig)
    out_dir: str = "out"

    def __post_init__(self) -> None:
        total = sum(self.decision_mix.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"decision_mix must sum to 1.0, got {total}")
        total = sum(self.language_mix.values())
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"language_mix must sum to 1.0, got {total}")
        if self.source not in ("synthetic", "real"):
            raise ValueError("source must be 'synthetic' or 'real'")
        if self.shard_lines < 1:
            raise ValueError("shard_lines must be positive")
        if self.start_sentence_id < 1:
            raise ValueError("start_sentence_id must be >= 1")


def load_config(path: str | Path) -> Config:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    # Keys prefixed with "_" are documentation for whoever edits the file; every
    # other unknown key is still rejected, so a typo does not silently do nothing.
    raw = {k: v for k, v in raw.items() if not k.startswith("_")}
    diversity = DiversityConfig(**raw.pop("diversity", {}))
    return Config(diversity=diversity, **raw)
