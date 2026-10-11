"""Renumber sentence_id so every line carries its own consecutive id.

By default the corpus emits one line per span, and all lines for a sentence
share a sentence_id (schema §7).  This tool rewrites that so each line gets a
distinct consecutive id instead.

The original grouping is preserved in a `group_id` field rather than discarded.
Without it there is no way to tell which lines came from one sentence, which
Stage 1 NER needs (a sentence's spans are one training example) and which four
of the §14.2 group checks are defined over.  Keeping it also makes the rewrite
reversible.

Streams shard by shard: memory stays flat regardless of corpus size.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def renumber_dir(
    src: Path,
    dst: Path,
    start_id: int = 1,
    pattern: str = "part-*.jsonl",
    negatives_pattern: str = "negatives-*.jsonl",
) -> dict:
    """Rewrite every shard, assigning one consecutive sentence_id per line.

    Positive and negative shards draw from a single counter so the ids stay
    globally consecutive across both files, as they were before.
    """
    dst.mkdir(parents=True, exist_ok=True)
    next_id = start_id
    stats = {"positive_lines": 0, "negative_lines": 0, "groups": 0, "files": 0}

    # Negatives first: one line each, so they are trivially one-id-per-line.
    for shard in sorted(src.glob(negatives_pattern)):
        out = dst / shard.name
        with shard.open(encoding="utf-8") as fin, out.open("w", encoding="utf-8") as fout:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                record["group_id"] = record["sentence_id"]
                record["sentence_id"] = next_id
                next_id += 1
                stats["negative_lines"] += 1
                stats["groups"] += 1
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
        stats["files"] += 1
        print(f"  {shard.name}: {stats['negative_lines']:,} lines so far", flush=True)

    for shard in sorted(src.glob(pattern)):
        out = dst / shard.name
        seen_group = None
        with shard.open(encoding="utf-8") as fin, out.open("w", encoding="utf-8") as fout:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                group = record["sentence_id"]
                if group != seen_group:
                    stats["groups"] += 1
                    seen_group = group
                record["group_id"] = group
                record["sentence_id"] = next_id
                next_id += 1
                stats["positive_lines"] += 1
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
        stats["files"] += 1
        print(
            f"  {shard.name}: {stats['positive_lines']:,} lines, id now {next_id:,}",
            flush=True,
        )

    stats["first_id"] = start_id
    stats["last_id"] = next_id - 1
    stats["next_id"] = next_id
    return stats


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Give every line its own consecutive sentence_id")
    ap.add_argument("--src", required=True, help="directory holding the shards to rewrite")
    ap.add_argument("--dst", required=True, help="directory to write the renumbered shards to")
    ap.add_argument("--start-id", type=int, default=1)
    args = ap.parse_args(argv)

    src, dst = Path(args.src), Path(args.dst)
    if not src.is_dir():
        print(f"source directory not found: {src}", file=sys.stderr)
        return 1
    if dst.resolve() == src.resolve():
        # Rewriting in place would corrupt a shard partway through on failure.
        print("destination must differ from source", file=sys.stderr)
        return 1

    stats = renumber_dir(src, dst, args.start_id)
    total = stats["positive_lines"] + stats["negative_lines"]
    print()
    print(f"rewrote {stats['files']} shards")
    print(f"lines       : {total:,} ({stats['positive_lines']:,} span + {stats['negative_lines']:,} negative)")
    print(f"sentences   : {stats['groups']:,} (preserved in group_id)")
    print(f"id range    : {stats['first_id']:,} .. {stats['last_id']:,}")
    print(f"next free id: {stats['next_id']:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
