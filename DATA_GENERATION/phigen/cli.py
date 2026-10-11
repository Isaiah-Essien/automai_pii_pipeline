"""Command line entry point: `python -m phigen build --config config/default.json`."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load_config
from .generate import Generator
from .lexicons import check_floors, load_lexicons
from .validate import validate_build


def cmd_build(args) -> int:
    config = load_config(args.config)
    if args.target_lines:
        config.target_lines = args.target_lines
    if args.start_sentence_id:
        config.start_sentence_id = args.start_sentence_id
    if args.id_per_line:
        config.id_per_line = True
    out = Path(args.out or config.out_dir)
    if out.exists():
        for stale in list(out.glob("part-*.jsonl")) + list(out.glob("negatives-*.jsonl")):
            stale.unlink()

    lex = load_lexicons()
    floors = check_floors(lex, config.diversity.min_lexicon_entries)
    failed_floors = {k: v for k, v in floors.items() if not v[1]}
    if failed_floors:
        print(f"lexicon floor not met: {failed_floors}")
        return 1

    gen = Generator(config, lex)
    stats = gen.run(out)

    report = validate_build(
        out,
        start_sentence_id=config.start_sentence_id,
        id_per_line=config.id_per_line,
    )
    diversity = gen.diversity.report()

    reports_dir = out / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "validation.json").write_text(
        json.dumps(
            {
                "summary": report.summary(),
                "failures": [
                    {
                        "scope": f.scope,
                        "check": f.check,
                        "reason": f.reason,
                        "shard": f.shard,
                        "line_number": f.line_number,
                    }
                    for f in report.failures[:500]
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (reports_dir / "diversity.json").write_text(json.dumps(diversity, indent=2), encoding="utf-8")
    (reports_dir / "generation.json").write_text(
        json.dumps(
            {
                "lines": stats.lines,
                "sentences": stats.sentences,
                "negatives": stats.negatives,
                "notes": stats.notes,
                "decisions": stats.decisions,
                "phi_types": dict(sorted(stats.phi_types.items())),
                "build_failures": stats.build_failures,
                "start_sentence_id": config.start_sentence_id,
                "next_sentence_id": gen.next_sentence_id,
                "highest_sentence_id": gen.next_sentence_id - 1,
                "lexicon_floors": {k: v[0] for k, v in floors.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    total = sum(stats.decisions.values()) or 1
    print(f"lines={stats.lines} sentences={stats.sentences} negatives={stats.negatives}")
    print(
        f"decision mix: REDACT={stats.decisions.get('REDACT', 0) / total:.2%} "
        f"PRESERVE={stats.decisions.get('PRESERVE', 0) / total:.2%}"
    )
    print(f"validation: {'PASS' if report.passed else f'FAIL ({len(report.failures)})'}")
    n_violations = len(diversity["violations"])
    print(f"diversity:  {'PASS' if diversity['passed'] else f'FAIL ({n_violations})'}")
    print(f"reports in {reports_dir}")
    return 0 if (report.passed and diversity["passed"]) else 2


def cmd_validate(args) -> int:
    report = validate_build(args.out, start_sentence_id=args.start_sentence_id)
    print(json.dumps(report.summary(), indent=2))
    return 0 if report.passed else 2


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="phigen")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="generate, validate, and report")
    build.add_argument("--config", default="config/default.json")
    build.add_argument("--out", default=None)
    build.add_argument("--target-lines", type=int, default=None)
    build.add_argument(
        "--id-per-line",
        action="store_true",
        default=None,
        help="give every emitted line its own consecutive sentence_id and keep "
             "the sentence's id in group_id",
    )
    build.add_argument(
        "--start-sentence-id",
        type=int,
        default=None,
        help="first sentence_id to emit; use one past the previous build's highest "
             "id when extending an existing corpus",
    )
    build.set_defaults(func=cmd_build)

    val = sub.add_parser("validate", help="validate an existing build")
    val.add_argument("--out", default="out")
    val.add_argument("--start-sentence-id", type=int, default=1)
    val.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
