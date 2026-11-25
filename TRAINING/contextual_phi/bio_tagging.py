"""Character BIO tags aligned to Hugging Face subword tokenization."""

from __future__ import annotations

from typing import Dict, List, Set, Tuple

from contextual_phi.constants import REDACT_ENTITY_TYPES
from contextual_phi.span_io import GroupedSentenceSpans


class BioTagVocabulary:
    """
    Label map for token classification (O, B-PERSON, I-PERSON, ...).

    Entity list defaults to REDACT_ENTITY_TYPES from constants.
    """

    def __init__(self, entity_types: Set[str] | None = None) -> None:
        sorted_types = sorted(entity_types or REDACT_ENTITY_TYPES)
        labels = ["O"]
        for entity in sorted_types:
            labels.append(f"B-{entity}")
            labels.append(f"I-{entity}")
        self.label_to_id = {label: idx for idx, label in enumerate(labels)}
        self.id_to_label = {idx: label for label, idx in self.label_to_id.items()}

    @property
    def label_count(self) -> int:
        return len(self.label_to_id)


class NerSequenceEncoder:
    """
    Turn grouped sentences into input_ids, attention_mask, and label ids.

    Algorithm:
      1. Paint character-level BIO tags from gold span offsets.
      2. Tokenize with return_offsets_mapping.
      3. For each subword, take the tag at the token's start char ( -100 for specials).
    """

    def __init__(self, tokenizer, vocabulary: BioTagVocabulary, max_length: int = 256) -> None:
        self.tokenizer = tokenizer
        self.vocabulary = vocabulary
        self.max_length = max_length

    def build_character_bio_tags(
        self, text: str, entity_spans: List[Tuple[int, int, str]]
    ) -> List[str]:
        """
        Assign a BIO label to every character index in text.

        Overlapping spans are not expected in our schema; last write wins if they appear.
        """
        tags = ["O"] * len(text)
        for start, end, phi_type in entity_spans:
            if start >= len(text):
                continue
            tags[start] = f"B-{phi_type}"
            for char_index in range(start + 1, min(end, len(text))):
                tags[char_index] = f"I-{phi_type}"
        return tags

    def encode_one_sentence(
        self, text: str, entity_spans: List[Tuple[int, int, str]]
    ) -> Dict[str, List]:
        """Tokenize one sentence and align labels to subwords."""
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            return_offsets_mapping=True,
        )
        offset_pairs = encoding.pop("offset_mapping")
        char_tags = self.build_character_bio_tags(text, entity_spans)
        label_ids: List[int] = []
        for char_start, char_end in offset_pairs:
            if char_start == char_end:
                label_ids.append(-100)
            else:
                tag = char_tags[char_start] if char_start < len(char_tags) else "O"
                label_ids.append(self.vocabulary.label_to_id.get(tag, 0))
        encoding["labels"] = label_ids
        return encoding

    def encode_sentence_groups(
        self,
        groups: Dict[int, GroupedSentenceSpans],
        span_extractor,
    ) -> Dict[str, List]:
        """
        Batch-encode all sentences that have at least one NER span.

        Args:
            groups: sentence_id -> GroupedSentenceSpans.
            span_extractor: Callable taking GroupedSentenceSpans -> list of (start, end, type).
        """
        batch: Dict[str, List] = {"input_ids": [], "attention_mask": [], "labels": []}
        for grouped in groups.values():
            spans = span_extractor(grouped)
            if not spans:
                continue
            encoded = self.encode_one_sentence(grouped.sentence_text, spans)
            for key in batch:
                batch[key].append(encoded[key])
        return batch