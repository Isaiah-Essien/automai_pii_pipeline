"""Placeholder inference: NER proposals + adjudicator + string redaction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

from contextual_phi.adjudication_finetune import RedactPreserveClassifier


@dataclass
class ProposedSpan:
    """One candidate span before we apply redaction placeholders."""

    char_start: int
    char_end: int
    entity_type: str
    redact_probability: float


class ClinicalTextDeidentifier:
    """
    Glue Stage 1 token classifier and Stage 2 adjudicator for demo redaction.

    BIO span decoding is still a stub — replace _collect_span_candidates once NER eval
    looks good on eval_100k.
    """

    def __init__(
        self,
        ner_model_directory: str,
        adjudication_encoder_name: str,
        adjudication_weights_path: str,
        device: str | None = None,
    ) -> None:
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.ner_tokenizer = AutoTokenizer.from_pretrained(ner_model_directory)
        self.ner_model = AutoModelForTokenClassification.from_pretrained(ner_model_directory)
        self.ner_model.to(self.device)
        self.ner_model.eval()

        self.adjudication_model = RedactPreserveClassifier(adjudication_encoder_name)
        self.adjudication_model.to(self.device)
        checkpoint = torch.load(adjudication_weights_path, map_location=self.device)
        self.adjudication_model.load_state_dict(checkpoint["model_state"])
        self.adjudication_model.eval()
        self.adjudication_tokenizer = AutoTokenizer.from_pretrained(adjudication_encoder_name)

    def redact_text(self, clinical_text: str, decision_threshold: float = 0.5) -> str:
        """
        Return text with adjudicated spans replaced by [TYPE] placeholders.

        Replacements run from the end of the string toward the start so offsets stay valid.
        """
        candidates = self._collect_span_candidates(clinical_text)
        to_redact = [
            span for span in candidates if span.redact_probability >= decision_threshold
        ]
        result = clinical_text
        for span in sorted(to_redact, key=lambda item: -item.char_start):
            placeholder = f"[{span.entity_type}]"
            result = result[: span.char_start] + placeholder + result[span.char_end :]
        return result

    def _collect_span_candidates(self, text: str) -> List[ProposedSpan]:
        """
        Run NER forward pass and attach adjudicator scores.

        TODO: decode B-/I- spans properly instead of treating each token as a span.
        """
        encoded = self.ner_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            return_offsets_mapping=True,
        )
        offset_mapping = encoded.pop("offset_mapping")[0].tolist()
        with torch.no_grad():
            outputs = self.ner_model(
                input_ids=encoded["input_ids"].to(self.device),
                attention_mask=encoded["attention_mask"].to(self.device),
            )
        predicted_label_ids = outputs.logits.argmax(dim=-1).squeeze(0).tolist()
        candidates: List[ProposedSpan] = []
        for token_index, label_id in enumerate(predicted_label_ids):
            if label_id == 0:
                continue
            char_start, char_end = offset_mapping[token_index]
            if char_start == char_end:
                continue
            window_left = max(0, char_start - 80)
            window_right = min(len(text), char_end + 80)
            snippet = text[window_left:window_right]
            redact_prob = self._score_redact(snippet)
            candidates.append(
                ProposedSpan(
                    char_start=char_start,
                    char_end=char_end,
                    entity_type="PHI",
                    redact_probability=redact_prob,
                )
            )
        return candidates

    def _score_redact(self, context_snippet: str) -> float:
        """Return P(REDACT) from the Stage 2 head."""
        encoded = self.adjudication_tokenizer(
            context_snippet,
            truncation=True,
            max_length=128,
            padding="max_length",
            return_tensors="pt",
        )
        with torch.no_grad():
            logits = self.adjudication_model(
                encoded["input_ids"].to(self.device),
                encoded["attention_mask"].to(self.device),
            )
            probabilities = torch.softmax(logits, dim=-1)
        return float(probabilities[0, 1].cpu())