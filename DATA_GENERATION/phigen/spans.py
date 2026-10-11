"""Offset-by-construction sentence assembly.

The central invariant of this corpus is that ``sentence[span_start:span_end]``
equals ``span`` exactly.  We guarantee it structurally rather than by checking
after the fact: a sentence is built by appending fragments to a cursor, and each
span's offsets are recorded at the moment its fragment is placed.  Nothing here
ever searches the finished sentence for a substring.

Unicode is normalised to NFC on every fragment as it is appended, and the joined
result is asserted NFC-stable, so composition cannot shift an offset that was
recorded earlier.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Iterator, Sequence


class SpanError(ValueError):
    """Raised when a sentence violates a structural rule from the schema."""


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


@dataclass(frozen=True)
class Span:
    """One emitted span: a slice of the sentence plus its labels."""

    span_start: int
    span_end: int
    span: str
    phi_type: str
    ambiguity_type: str = "none"
    surface_form: str = "standard"

    @property
    def length(self) -> int:
        return self.span_end - self.span_start

    def contains(self, other: "Span") -> bool:
        """True when this span's range fully encloses ``other``'s range."""
        return self.span_start <= other.span_start and other.span_end <= self.span_end


def _overlaps(a: Span, b: Span) -> bool:
    return a.span_start < b.span_end and b.span_start < a.span_end


@dataclass
class SentenceBuild:
    """A finished sentence and its ordered spans."""

    sentence: str
    spans: list[Span]

    def __iter__(self) -> Iterator[Span]:
        return iter(self.spans)

    def __len__(self) -> int:
        return len(self.spans)


class SpanBuilder:
    """Assembles a sentence fragment by fragment, recording span offsets inline.

    Usage::

        b = SpanBuilder()
        b.literal("Patient ")
        b.span("Chioma Nwankwo", "PERSON")
        b.literal(" was admitted.")
        build = b.finish()

    Offsets come from the running cursor, never from a search over the result.
    """

    def __init__(self) -> None:
        self._parts: list[str] = []
        self._spans: list[Span] = []
        self._cursor = 0

    # ------------------------------------------------------------------ text

    def literal(self, text: str) -> "SpanBuilder":
        """Append text that carries no span."""
        if text:
            piece = nfc(text)
            self._parts.append(piece)
            self._cursor += len(piece)
        return self

    def span(
        self,
        text: str,
        phi_type: str,
        *,
        ambiguity_type: str = "none",
        surface_form: str = "standard",
    ) -> Span:
        """Append text and record it as a span, returning the recorded Span."""
        piece = nfc(text)
        if not piece.strip():
            raise SpanError("span must contain at least one non-whitespace character")
        start = self._cursor
        self._parts.append(piece)
        self._cursor += len(piece)
        recorded = Span(
            span_start=start,
            span_end=self._cursor,
            span=piece,
            phi_type=phi_type,
            ambiguity_type=ambiguity_type,
            surface_form=surface_form,
        )
        self._spans.append(recorded)
        return recorded

    def nested(
        self,
        outer_text: str,
        outer_phi_type: str,
        inner_text: str,
        inner_phi_type: str,
        *,
        outer_ambiguity: str = "none",
        inner_ambiguity: str = "none",
        outer_surface_form: str = "standard",
        inner_surface_form: str = "standard",
    ) -> tuple[Span, Span]:
        """Place a span that contains a second, shorter span.

        The canonical case from Section 13.2: "Amoxicillin Adeyemi" is a PERSON
        whose leading token "Amoxicillin" is independently a valid DRUG surface
        form.  Both are emitted, and containment holds by construction because
        the inner offsets are derived from the outer's placement.
        """
        offset = outer_text.find(inner_text)
        if offset < 0:
            raise SpanError(
                f"inner text {inner_text!r} does not occur in outer {outer_text!r}"
            )
        outer = self.span(
            outer_text,
            outer_phi_type,
            ambiguity_type=outer_ambiguity,
            surface_form=outer_surface_form,
        )
        # Derive the inner offsets from the outer's recorded start.  We locate
        # the inner text inside the *source* string, never inside the finished
        # sentence, so this stays a construction step rather than a search.
        inner_piece = nfc(inner_text)
        inner_start = outer.span_start + len(nfc(outer_text[:offset]))
        inner = Span(
            span_start=inner_start,
            span_end=inner_start + len(inner_piece),
            span=inner_piece,
            phi_type=inner_phi_type,
            ambiguity_type=inner_ambiguity,
            surface_form=inner_surface_form,
        )
        self._spans.append(inner)
        return outer, inner

    def text_so_far(self) -> str:
        """The sentence as placed up to this point."""
        return "".join(self._parts)

    def peek_last_char(self) -> str:
        """Last character placed so far, or "" when nothing has been placed."""
        for piece in reversed(self._parts):
            if piece:
                return piece[-1]
        return ""

    def replace_last_char(self, replacement: str) -> None:
        """Swap the final character, keeping the cursor and all offsets intact.

        Only ever used to fix trailing punctuation in literal text.  Replacing a
        character inside a recorded span would silently break that span's
        offsets, so this refuses to touch one.
        """
        for i in range(len(self._parts) - 1, -1, -1):
            if not self._parts[i]:
                continue
            end_of_piece = self._cursor - sum(len(x) for x in self._parts[i + 1 :])
            start_of_char = end_of_piece - 1
            for sp in self._spans:
                if sp.span_start <= start_of_char < sp.span_end:
                    raise SpanError(
                        "refusing to replace a character inside a recorded span"
                    )
            if len(replacement) != 1:
                raise SpanError("replacement must be exactly one character")
            self._parts[i] = self._parts[i][:-1] + replacement
            return

    def drop_last_char(self) -> None:
        """Remove the final character, shrinking the cursor by one.

        Used only to delete trailing punctuation in literal text at a clause
        seam.  Deleting inside a recorded span would invalidate that span's
        offsets, so this refuses to do it; every span placed so far ends at or
        before the cursor, so only the final character can be at risk.
        """
        for i in range(len(self._parts) - 1, -1, -1):
            if not self._parts[i]:
                continue
            start_of_char = self._cursor - 1
            for sp in self._spans:
                if sp.span_start <= start_of_char < sp.span_end:
                    raise SpanError("refusing to delete a character inside a recorded span")
            self._parts[i] = self._parts[i][:-1]
            self._cursor -= 1
            return

    # ----------------------------------------------------------------- build

    def finish(self) -> SentenceBuild:
        """Join, order, and structurally verify the sentence."""
        sentence = "".join(self._parts)
        if sentence != nfc(sentence):
            raise SpanError("joined sentence is not NFC-stable")
        if "\n" in sentence or "\r" in sentence:
            raise SpanError("sentence contains a literal newline")
        spans = order_spans(self._spans)
        verify_spans(sentence, spans)
        return SentenceBuild(sentence=sentence, spans=spans)


def order_spans(spans: Sequence[Span]) -> list[Span]:
    """Section 13.1: ascending span_start; ties broken by the shorter span first."""
    return sorted(spans, key=lambda s: (s.span_start, s.span_end))


def verify_spans(sentence: str, spans: Sequence[Span]) -> None:
    """Assert every structural rule that applies within one sentence.

    Covers the line-level offset/bounds checks and the group-level ordering,
    overlap, and duplicate-span rules from Section 14.
    """
    n = len(sentence)
    seen: set[tuple[int, int]] = set()

    for s in spans:
        if not (0 <= s.span_start < s.span_end <= n):
            raise SpanError(
                f"bounds violated: 0 <= {s.span_start} < {s.span_end} <= {n} is false"
            )
        if sentence[s.span_start : s.span_end] != s.span:
            raise SpanError(
                f"offset mismatch: sentence[{s.span_start}:{s.span_end}]="
                f"{sentence[s.span_start:s.span_end]!r} != {s.span!r}"
            )
        if not s.span.strip():
            raise SpanError("span has no non-whitespace character")
        key = (s.span_start, s.span_end)
        if key in seen:
            raise SpanError(f"duplicate span offsets {key}")
        seen.add(key)

    ordered = order_spans(spans)
    if list(spans) != ordered:
        raise SpanError("spans are not in ascending (span_start, span_end) order")

    check_overlap_policy(spans)


def check_overlap_policy(spans: Sequence[Span]) -> None:
    """Section 13.2.

    Two spans of the same phi_type must never overlap.  Spans of different
    phi_type may overlap only under containment; a partial (crossing) overlap is
    an annotation error.
    """
    for i, a in enumerate(spans):
        for b in spans[i + 1 :]:
            if not _overlaps(a, b):
                continue
            if a.phi_type == b.phi_type:
                raise SpanError(
                    f"same-type overlap for {a.phi_type}: "
                    f"({a.span_start},{a.span_end}) and ({b.span_start},{b.span_end})"
                )
            if not (a.contains(b) or b.contains(a)):
                raise SpanError(
                    f"partial overlap without containment: "
                    f"({a.span_start},{a.span_end}) and ({b.span_start},{b.span_end})"
                )
