"""Stage 1: fine-tune a pretrained encoder for PHI span detection (BIO tagging)."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from datasets import Dataset
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
)

from contextual_phi.bio_tagging import BioTagVocabulary, NerSequenceEncoder
from contextual_phi.project_settings import DeidProjectSettings
from contextual_phi.span_io import SentenceSpanGrouper, SpanJsonlReader


class NerFineTuningJob:
    """
    Load a NER shard, build a HF Dataset, and fine-tune (not pretrain from scratch).

    Checkpoints land under settings.paths.checkpoint_dir(run_name). We resume from the
    latest checkpoint-* folder when Colab disconnects.
    """

    def __init__(self, settings: DeidProjectSettings) -> None:
        self.settings = settings
        self.bio_vocabulary = BioTagVocabulary()
        self.tokenizer = AutoTokenizer.from_pretrained(settings.hyperparameters.encoder_name)

    def _ner_shard_path(self) -> Path:
        name = self.settings.hyperparameters.ner_shard_filename
        return self.settings.paths.shard_file(name)

    def load_span_rows(self) -> list:
        """Read the active NER JSONL shard, honoring row_limit for pilots."""
        reader = SpanJsonlReader(self._ner_shard_path())
        return reader.load_all(max_rows=self.settings.hyperparameters.row_limit)

    def build_training_dataset(self) -> Dataset:
        """Group spans by sentence and encode to token labels."""
        rows = self.load_span_rows()
        grouper = SentenceSpanGrouper()
        groups = grouper.group_by_sentence(rows)
        encoder = NerSequenceEncoder(
            self.tokenizer,
            self.bio_vocabulary,
            self.settings.hyperparameters.max_sequence_length,
        )
        batch = encoder.encode_sentence_groups(groups, grouper.redact_spans_for_ner)
        return Dataset.from_dict(batch)

    def build_token_classifier(self):
        """Attach a new classification head on top of the pretrained encoder weights."""
        hp = self.settings.hyperparameters
        return AutoModelForTokenClassification.from_pretrained(
            hp.encoder_name,
            num_labels=self.bio_vocabulary.label_count,
            id2label=self.bio_vocabulary.id_to_label,
            label2id=self.bio_vocabulary.label_to_id,
        )

    def checkpoint_output_dir(self) -> Path:
        return self.settings.paths.checkpoint_dir(self.settings.run_name)

    def latest_interrupt_checkpoint(self) -> Optional[str]:
        """
        Find the newest Hugging Face checkpoint subdirectory, if any.

        Returns:
            Path string suitable for Trainer.resume_from_checkpoint.
        """
        output_dir = self.checkpoint_output_dir()
        if not output_dir.exists():
            return None
        numbered = sorted(
            output_dir.glob("checkpoint-*"),
            key=lambda path: int(path.name.split("-")[-1]),
        )
        return str(numbered[-1]) if numbered else None

    def run(self) -> None:
        """Execute fine-tuning and write final/ under the run checkpoint dir."""
        train_dataset = self.build_training_dataset()
        model = self.build_token_classifier()
        hp = self.settings.hyperparameters
        training_args = TrainingArguments(
            output_dir=str(self.checkpoint_output_dir()),
            per_device_train_batch_size=hp.per_device_batch_size,
            gradient_accumulation_steps=hp.gradient_accumulation_steps,
            num_train_epochs=hp.ner_epoch_count,
            learning_rate=hp.learning_rate,
            fp16=hp.use_fp16,
            logging_steps=50,
            save_steps=500,
            save_total_limit=3,
            report_to="none",
            seed=hp.random_seed,
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=DataCollatorForTokenClassification(self.tokenizer),
        )
        resume_path = self.latest_interrupt_checkpoint()
        trainer.train(resume_from_checkpoint=resume_path)
        final_dir = self.checkpoint_output_dir() / "final"
        trainer.save_model(str(final_dir))
        self.tokenizer.save_pretrained(str(final_dir))