"""Stage 2: supervised REDACT vs PRESERVE on local context around each span."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModel, AutoTokenizer

from contextual_phi.project_settings import DeidProjectSettings
from contextual_phi.span_io import SpanJsonlReader, SpanTrainingRow


class AdjudicationExampleDataset(Dataset):
    """
    Torch dataset of tokenized context windows around gold spans.

    Each item is a snippet of sentence text (not the full note) so homograph
    context still fits in a short max length.
    """

    def __init__(
        self,
        rows: List[SpanTrainingRow],
        tokenizer,
        max_length: int = 128,
        context_margin_chars: int = 120,
    ) -> None:
        self.rows = rows
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.context_margin_chars = context_margin_chars

    def __len__(self) -> int:
        return len(self.rows)

    def _context_snippet(self, row: SpanTrainingRow) -> str:
        text = row.sentence
        left = max(0, row.span_start - self.context_margin_chars)
        right = min(len(text), row.span_end + self.context_margin_chars)
        return text[left:right]

    def __getitem__(self, index: int) -> Dict[str, torch.Tensor]:
        row = self.rows[index]
        snippet = self._context_snippet(row)
        encoded = self.tokenizer(
            snippet,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )
        label_id = 1 if row.decision == "REDACT" else 0
        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "labels": torch.tensor(label_id, dtype=torch.long),
        }


class RedactPreserveClassifier(nn.Module):
    """
    CLS-pooled encoder representation -> two-class head.

    Class 0 = PRESERVE clinical content; class 1 = REDACT PHI.
    """

    def __init__(self, encoder_name: str, hidden_dropout: float = 0.1) -> None:
        super().__init__()
        self.encoder = AutoModel.from_pretrained(encoder_name)
        hidden_size = self.encoder.config.hidden_size
        self.dropout = nn.Dropout(hidden_dropout)
        self.linear_head = nn.Linear(hidden_size, 2)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_vector = outputs.last_hidden_state[:, 0, :]
        cls_vector = self.dropout(cls_vector)
        return self.linear_head(cls_vector)


class AdjudicationFineTuningJob:
    """
    Train Stage 2 on adj_400k.jsonl and save adj_model.pt for inference.

    Uses simple class weights so REDACT examples are not drowned out when counts skew.
    """

    def __init__(self, settings: DeidProjectSettings, device: Optional[str] = None) -> None:
        self.settings = settings
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        encoder = settings.hyperparameters.encoder_name
        self.tokenizer = AutoTokenizer.from_pretrained(encoder)
        self.model = RedactPreserveClassifier(encoder).to(self.device)

    def load_adjudication_rows(self, max_rows: Optional[int] = None) -> List[SpanTrainingRow]:
        path = self.settings.paths.shard_file(
            self.settings.hyperparameters.adjudication_shard_filename
        )
        return SpanJsonlReader(path).load_all(max_rows=max_rows)

    def weights_file_path(self) -> Path:
        return self.settings.paths.checkpoint_dir("adj_supervised") / "adj_model.pt"

    def _balanced_class_weights(
        self, rows: List[SpanTrainingRow]
    ) -> torch.Tensor:
        """Inverse-frequency style weights for preserve vs redact."""
        redact_count = sum(1 for row in rows if row.decision == "REDACT")
        preserve_count = len(rows) - redact_count
        preserve_weight = 1.0
        redact_weight = 1.0
        total = redact_count + preserve_count
        if preserve_count > 0 and redact_count > 0:
            redact_weight = total / (2.0 * redact_count)
            preserve_weight = total / (2.0 * preserve_count)
        return torch.tensor([preserve_weight, redact_weight], device=self.device)

    def run(
        self,
        epoch_count: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        max_rows: Optional[int] = 50_000,
    ) -> None:
        """
        Full training loop with AdamW and CrossEntropyLoss.

        Args:
            max_rows: None means use the entire adj shard (set --full on the CLI).
        """
        rows = self.load_adjudication_rows(max_rows=max_rows)
        dataset = AdjudicationExampleDataset(rows, self.tokenizer)
        data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        loss_fn = nn.CrossEntropyLoss(weight=self._balanced_class_weights(rows))
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate)

        self.model.train()
        for epoch in range(epoch_count):
            epoch_loss = 0.0
            for batch in data_loader:
                input_ids = batch["input_ids"].to(self.device)
                attention_mask = batch["attention_mask"].to(self.device)
                labels = batch["labels"].to(self.device)
                optimizer.zero_grad()
                logits = self.model(input_ids, attention_mask)
                loss = loss_fn(logits, labels)
                loss.backward()
                optimizer.step()
                epoch_loss += loss.item()
            average = epoch_loss / max(len(data_loader), 1)
            print(f"adjudication epoch={epoch + 1} mean_loss={average:.4f}")

        output_path = self.weights_file_path()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "model_state": self.model.state_dict(),
                "encoder_name": self.settings.hyperparameters.encoder_name,
            },
            output_path,
        )