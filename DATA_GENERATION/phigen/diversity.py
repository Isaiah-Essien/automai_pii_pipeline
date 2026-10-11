"""Section 15 diversity floors: tracking during generation, and reporting.

Two of the floors are enforced *while* generating (a template's draw weight is
damped as its share rises, and the neediest surface-form family is preferred),
because a purely post-hoc check can only tell you the build already failed.  The
rest are measured and reported.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import DiversityConfig


@dataclass
class DiversityTracker:
    config: DiversityConfig
    template_counts: dict[str, int] = field(default_factory=dict)
    template_by_phi: dict[str, dict[str, int]] = field(default_factory=dict)
    phi_counts: dict[str, int] = field(default_factory=dict)
    lexical_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    surface_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    sentence_lengths: list[int] = field(default_factory=list)
    # Surface forms belonging to a curated ambiguous set, recorded so the report
    # can exempt them from the lexical ceiling.
    ambiguous_entries: set[str] = field(default_factory=set)

    # ------------------------------------------------------------- recording

    def note_ambiguous_entries(self, entries) -> None:
        """Register the surface forms that come from the curated hard-case sets."""
        self.ambiguous_entries.update(entries)

    def record_line(self, template: str, phi_type: str, span_text: str, surface_form: str) -> None:
        self.template_counts[template] = self.template_counts.get(template, 0) + 1
        self.phi_counts[phi_type] = self.phi_counts.get(phi_type, 0) + 1
        by_phi = self.template_by_phi.setdefault(phi_type, {})
        by_phi[template] = by_phi.get(template, 0) + 1
        lex = self.lexical_counts.setdefault(phi_type, {})
        lex[span_text] = lex.get(span_text, 0) + 1
        if phi_type in ("PHONE", "EMAIL"):
            fam = self.surface_counts.setdefault(phi_type, {})
            fam[surface_form] = fam.get(surface_form, 0) + 1

    def record_sentence(self, sentence: str) -> None:
        self.sentence_lengths.append(len(sentence.split()))

    # -------------------------------------------------------------- steering

    def template_damping(self, template: str, total_lines: int) -> float:
        """Down-weight a template that is approaching its share ceiling."""
        if total_lines < 200:
            return 1.0
        share = self.template_counts.get(template, 0) / max(total_lines, 1)
        ceiling = self.config.max_template_share_within_phi_type
        if share <= ceiling:
            return 1.0
        return max(0.01, ceiling / share)

    def neediest_family(self, phi_type: str, families: tuple[str, ...], rng) -> str:
        """Return the family furthest below its floor, breaking ties randomly."""
        counts = self.surface_counts.get(phi_type, {})
        total = sum(counts.values())
        if total == 0:
            return families[rng.randrange(len(families))]
        deficits = []
        for fam in families:
            share = counts.get(fam, 0) / total
            deficits.append((share - self.config.min_variant_family_share, fam))
        deficits.sort()
        # Mostly take the neediest; occasionally sample freely so the corpus does
        # not lock into a rigid rotation.
        if rng.random() < 0.8:
            return deficits[0][1]
        return families[rng.randrange(len(families))]

    # ------------------------------------------------------------- reporting

    def report(self) -> dict:
        """Measure every Section 15 floor.

        A ceiling expressed as a share is only *satisfiable* above a certain
        volume: a lexical entry that appears even once is 1/N of its type, so
        the 0.1 percent ceiling cannot be met until a type has 1,000 lines, and
        the 0.5 percent template ceiling needs 200 templates touching a type.
        Below those thresholds we report the floor as `not_yet_applicable`
        rather than as a violation, so that a genuine concentration fault at
        full scale is not buried under arithmetic that was never satisfiable.
        """
        total_lines = sum(self.phi_counts.values())
        violations: list[str] = []
        not_applicable: list[str] = []
        exempted: list[str] = []
        lexical_min_lines = int(round(1 / self.config.max_lexical_entry_share_within_type))
        template_min_templates = int(
            round(1 / self.config.max_template_share_within_phi_type)
        )
        distinct_templates = len(self.template_counts)
        # The template ceiling needs two things to be satisfiable: enough
        # distinct templates to divide the share among, AND enough lines of the
        # type that a single appearance is not already over the ceiling.  A type
        # with 159 lines puts one appearance at 0.63 percent no matter how many
        # templates exist.
        template_min_lines = template_min_templates
        have_enough_templates = distinct_templates >= template_min_templates

        template_shares = {}
        for phi_type, templates in self.template_by_phi.items():
            phi_total = self.phi_counts.get(phi_type, 0) or 1
            for name, count in templates.items():
                share = count / phi_total
                template_shares[f"{phi_type}/{name}"] = round(share, 5)
                if share > self.config.max_template_share_within_phi_type:
                    message = (
                        f"template {name} is {share:.3%} of {phi_type} "
                        f"(ceiling {self.config.max_template_share_within_phi_type:.3%})"
                    )
                    reachable = have_enough_templates and phi_total >= template_min_lines
                    if reachable:
                        violations.append(message)
                    else:
                        not_applicable.append(message)

        lexical_top = {}
        for phi_type, entries in self.lexical_counts.items():
            phi_total = self.phi_counts.get(phi_type, 0) or 1
            top = sorted(entries.items(), key=lambda kv: -kv[1])[:5]
            lexical_top[phi_type] = [
                {"entry": e, "count": c, "share": round(c / phi_total, 5)} for e, c in top
            ]
            for entry, count in entries.items():
                share = count / phi_total
                if share > self.config.max_lexical_entry_share_within_type:
                    message = (
                        f"lexical entry {entry!r} is {share:.3%} of {phi_type} "
                        f"(ceiling {self.config.max_lexical_entry_share_within_type:.3%})"
                    )
                    exempt_type = phi_type in self.config.lexical_ceiling_exempt_types
                    exempt_entry = (
                        self.config.exempt_ambiguous_entries
                        and any(
                            entry == a or entry.startswith(a + " ")
                            for a in self.ambiguous_entries
                        )
                    )
                    if exempt_type or exempt_entry:
                        exempted.append(message)
                    elif phi_total >= lexical_min_lines:
                        violations.append(message)
                    else:
                        not_applicable.append(message)

        surface_shares = {}
        for phi_type, families in self.surface_counts.items():
            total = sum(families.values()) or 1
            surface_shares[phi_type] = {
                fam: round(count / total, 4) for fam, count in sorted(families.items())
            }
            for fam, count in families.items():
                share = count / total
                if share < self.config.min_variant_family_share:
                    violations.append(
                        f"surface family {phi_type}/{fam} is {share:.2%} "
                        f"(floor {self.config.min_variant_family_share:.0%})"
                    )

        lengths = sorted(self.sentence_lengths)
        long_tail = sum(1 for n in lengths if n > self.config.long_tail_token_target)
        long_tail_share = long_tail / len(lengths) if lengths else 0.0
        if lengths and long_tail_share < self.config.min_long_tail_share:
            violations.append(
                f"long tail past {self.config.long_tail_token_target} tokens is "
                f"{long_tail_share:.2%} (floor {self.config.min_long_tail_share:.0%})"
            )

        return {
            "total_lines": total_lines,
            "distinct_templates": len(self.template_counts),
            "template_shares_within_phi_type": template_shares,
            "phi_type_counts": dict(sorted(self.phi_counts.items())),
            "lexical_top5_by_type": lexical_top,
            "surface_form_shares": surface_shares,
            "sentence_length": {
                "count": len(lengths),
                "min": lengths[0] if lengths else 0,
                "median": lengths[len(lengths) // 2] if lengths else 0,
                "p90": lengths[int(len(lengths) * 0.9)] if lengths else 0,
                "max": lengths[-1] if lengths else 0,
                "share_over_target": round(long_tail_share, 4),
            },
            "feasibility": {
                "lexical_ceiling_needs_lines_per_type": lexical_min_lines,
                "template_ceiling_needs_templates": template_min_templates,
                "distinct_templates": distinct_templates,
                "template_ceiling_needs_lines_per_type": template_min_lines,
                "have_enough_templates": have_enough_templates,
                "types_below_lexical_threshold": sorted(
                    t for t, n in self.phi_counts.items() if n < lexical_min_lines
                ),
                "types_below_template_threshold": sorted(
                    t for t, n in self.phi_counts.items() if n < template_min_lines
                ),
            },
            "exempt_from_lexical_ceiling": {
                "types": sorted(self.config.lexical_ceiling_exempt_types),
                "rationale": (
                    "closed vocabularies (finite ages, body parts, ward labels) and "
                    "curated ambiguous surface forms; padding them would teach a "
                    "false distribution"
                ),
                "count": len(exempted),
            },
            "violations": violations,
            "not_yet_applicable_count": len(not_applicable),
            "not_yet_applicable_sample": not_applicable[:5],
            "passed": not violations,
        }
