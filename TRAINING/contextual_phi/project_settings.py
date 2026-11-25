"""Paths and hyperparameters for NER and adjudication fine-tuning runs."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

from contextual_phi.constants import PROJECT_ROOT_ENV

ShardProfile = Literal["3M", "5M"]

DEFAULT_ENCODER = "xlm-roberta-base"
DEFAULT_COLAB_DRIVE_ROOT = "/content/drive/MyDrive/phi_project"


@dataclass
class DeidDataPaths:
    """
    Locations for JSONL shards, model checkpoints, and EDA logs.

    Attributes:
        shard_root: Directory containing eval_100k, ner_*M, adj_400k, manifest.json.
        checkpoint_root: Hugging Face Trainer output and adj .pt weights.
        log_root: EDA plots and stats JSON.
    """

    shard_root: Path
    checkpoint_root: Path
    log_root: Path

    def shard_file(self, filename: str) -> Path:
        """Return the absolute path to a named shard file."""
        return self.shard_root / filename

    def checkpoint_dir(self, run_name: str) -> Path:
        """Return the directory for a named training run (e.g. ner_3M)."""
        return self.checkpoint_root / run_name


@dataclass
class FineTuningHyperparameters:
    """
    Shared knobs for Stage 1 and Stage 2 (not full LM pretraining).

    We fine-tune a public encoder; see TRAINING/README.md for why we skip pretraining.
    """

    profile: ShardProfile = "3M"
    encoder_name: str = DEFAULT_ENCODER
    max_sequence_length: int = 256
    per_device_batch_size: int = 8
    gradient_accumulation_steps: int = 4
    learning_rate: float = 3e-5
    random_seed: int = 42
    use_fp16: bool = True
    row_limit: Optional[int] = None

    @property
    def ner_shard_filename(self) -> str:
        """JSONL filename for the active NER shard profile."""
        return f"ner_{self.profile}.jsonl"

    @property
    def ner_epoch_count(self) -> int:
        """Fewer epochs on the larger shard to keep wall time reasonable."""
        return 4 if self.profile == "3M" else 2

    @property
    def evaluation_shard_filename(self) -> str:
        return "eval_100k.jsonl"

    @property
    def adjudication_shard_filename(self) -> str:
        return "adj_400k.jsonl"


@dataclass
class DeidProjectSettings:
    """
    Top-level settings object passed into trainers and EDA.

    Attributes:
        paths: Shard, checkpoint, and log directories.
        hyperparameters: Fine-tuning hyperparameters and shard profile.
        run_name: Subfolder name under checkpoint_root for Stage 1.
    """

    paths: DeidDataPaths
    hyperparameters: FineTuningHyperparameters = field(default_factory=FineTuningHyperparameters)
    run_name: str = "ner_3M"

    @classmethod
    def for_colab(
        cls,
        profile: ShardProfile = "3M",
        drive_project: Optional[str] = None,
    ) -> "DeidProjectSettings":
        """
        Build settings for a Colab notebook with Google Drive mounted.

        Args:
            profile: Either 3M or 5M NER shard naming.
            drive_project: Root folder on Drive; defaults to DEFAULT_COLAB_DRIVE_ROOT
                or PHI_DEID_PROJECT_ROOT when set.
        """
        root = drive_project or os.environ.get(PROJECT_ROOT_ENV, DEFAULT_COLAB_DRIVE_ROOT)
        base = Path(root)
        paths = DeidDataPaths(
            shard_root=base / "shards",
            checkpoint_root=base / "checkpoints",
            log_root=base / "logs",
        )
        hyperparameters = FineTuningHyperparameters(profile=profile)
        return cls(paths=paths, hyperparameters=hyperparameters, run_name=f"ner_{profile}")

    @classmethod
    def for_local_workspace(
        cls,
        project_root: Path,
        profile: ShardProfile = "3M",
    ) -> "DeidProjectSettings":
        """
        Build settings for a laptop or external HDD layout.

        Args:
            project_root: Folder that will contain shards/, checkpoints/, logs/.
            profile: 3M or 5M NER shard profile.
        """
        paths = DeidDataPaths(
            shard_root=project_root / "shards",
            checkpoint_root=project_root / "checkpoints",
            log_root=project_root / "logs",
        )
        hyperparameters = FineTuningHyperparameters(profile=profile)
        return cls(paths=paths, hyperparameters=hyperparameters, run_name=f"ner_{profile}")