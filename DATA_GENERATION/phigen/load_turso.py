"""Load the generated corpus into a libsql/Turso database.

Transfer runs over the HTTP pipeline API, batched and concurrent, because a
row-at-a-time load of a corpus this size is not practical: measured throughput
against a single connection is ~235 rows/s, versus ~1,400 rows/s at eight
workers.

The loader is resumable.  Progress is recorded per source file in a `_load_state`
table inside the target database itself, so an interrupted transfer continues
from the last committed batch rather than restarting or duplicating rows.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

# The seven required fields plus the Section 12 metadata, in column order.
COLUMNS = (
    "sentence_id",
    "sentence",
    "span_start",
    "span_end",
    "span",
    "phi_type",
    "decision",
    "note_id",
    "patient_id",
    "sentence_index",
    "source",
    "language",
    "code_switched",
    "ambiguity_type",
    "surface_form",
    "phi_languages",
)

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS spans (
    sentence_id    INTEGER NOT NULL,
    sentence       TEXT    NOT NULL,
    span_start     INTEGER NOT NULL,
    span_end       INTEGER NOT NULL,
    span           TEXT    NOT NULL,
    phi_type       TEXT    NOT NULL,
    decision       TEXT    NOT NULL,
    note_id        TEXT    NOT NULL,
    patient_id     TEXT    NOT NULL,
    sentence_index INTEGER NOT NULL,
    source         TEXT    NOT NULL,
    language       TEXT    NOT NULL,
    code_switched  INTEGER NOT NULL,
    ambiguity_type TEXT    NOT NULL,
    surface_form   TEXT    NOT NULL,
    phi_languages  TEXT    NOT NULL,
    PRIMARY KEY (sentence_id, span_start, span_end)
);
"""

# Indexes are created AFTER the bulk load: maintaining them during insert costs
# more than building them once at the end.
INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_spans_note ON spans(note_id)",
    "CREATE INDEX IF NOT EXISTS idx_spans_patient ON spans(patient_id)",
    "CREATE INDEX IF NOT EXISTS idx_spans_phi_type ON spans(phi_type)",
    "CREATE INDEX IF NOT EXISTS idx_spans_decision ON spans(decision)",
    "CREATE INDEX IF NOT EXISTS idx_spans_ambiguity ON spans(ambiguity_type)",
)

STATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS _load_state (
    source_file TEXT PRIMARY KEY,
    lines_done  INTEGER NOT NULL,
    updated_at  TEXT    NOT NULL
);
"""


@dataclass
class Endpoint:
    url: str
    token: str

    def pipeline(self, requests: list[dict], timeout: int = 120) -> dict:
        payload = json.dumps({"requests": requests}).encode()
        req = urllib.request.Request(
            self.url.rstrip("/") + "/v2/pipeline",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())

    def execute(self, sql: str, args: list[dict] | None = None, timeout: int = 120) -> dict:
        stmt: dict = {"sql": sql}
        if args:
            stmt["args"] = args
        body = self.pipeline([{"type": "execute", "stmt": stmt}, {"type": "close"}], timeout)
        first = body["results"][0]
        if first["type"] != "ok":
            raise RuntimeError(f"query failed: {first.get('error')}")
        return first["response"]["result"]


def to_arg(value) -> dict:
    """Encode one Python value in the libsql wire format."""
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "integer", "value": "1" if value else "0"}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, list):
        # phi_languages is stored as a JSON array so it survives a round trip.
        return {"type": "text", "value": json.dumps(value)}
    return {"type": "text", "value": str(value)}


def row_args(record: dict) -> list[dict]:
    return [to_arg(record.get(col)) for col in COLUMNS]


def insert_sql(n_rows: int) -> str:
    placeholder = "(" + ",".join("?" * len(COLUMNS)) + ")"
    values = ",".join([placeholder] * n_rows)
    # INSERT OR IGNORE makes a resumed batch idempotent: a row already committed
    # before an interruption is skipped rather than raising on the primary key.
    return f"INSERT OR IGNORE INTO spans ({','.join(COLUMNS)}) VALUES {values}"


def send_batch(endpoint: Endpoint, batch: list[dict], attempts: int = 5) -> int:
    """Insert one batch, retrying with backoff on transient failures."""
    args: list[dict] = []
    for record in batch:
        args.extend(row_args(record))
    sql = insert_sql(len(batch))
    delay = 2.0
    for attempt in range(attempts):
        try:
            endpoint.execute(sql, args, timeout=180)
            return len(batch)
        except (urllib.error.URLError, urllib.error.HTTPError, RuntimeError, TimeoutError) as exc:
            if attempt == attempts - 1:
                raise
            # A failed batch is retried whole; INSERT OR IGNORE means a partial
            # success followed by a retry cannot duplicate rows.
            print(f"  batch failed ({exc}); retrying in {delay:.0f}s", file=sys.stderr)
            time.sleep(delay)
            delay *= 2
    return 0


def load_file(
    endpoint: Endpoint,
    path: Path,
    batch_size: int,
    workers: int,
    already_done: int,
) -> int:
    """Load one JSONL shard, skipping the first `already_done` lines."""
    sent = already_done
    batches: list[list[dict]] = []
    current: list[dict] = []

    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh):
            if line_no < already_done:
                continue
            line = line.strip()
            if not line:
                continue
            current.append(json.loads(line))
            if len(current) >= batch_size:
                batches.append(current)
                current = []
    if current:
        batches.append(current)

    if not batches:
        return sent

    with ThreadPoolExecutor(max_workers=workers) as pool:
        for count in pool.map(lambda b: send_batch(endpoint, b), batches):
            sent += count
    return sent


def get_state(endpoint: Endpoint) -> dict[str, int]:
    result = endpoint.execute("SELECT source_file, lines_done FROM _load_state")
    state = {}
    for row in result["rows"]:
        state[row[0]["value"]] = int(row[1]["value"])
    return state


def set_state(endpoint: Endpoint, source_file: str, lines_done: int) -> None:
    endpoint.execute(
        "INSERT INTO _load_state(source_file, lines_done, updated_at) "
        "VALUES (?, ?, datetime('now')) "
        "ON CONFLICT(source_file) DO UPDATE SET lines_done=excluded.lines_done, "
        "updated_at=excluded.updated_at",
        [to_arg(source_file), to_arg(lines_done)],
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Load corpus shards into Turso")
    parser.add_argument("--url", default=os.environ.get("TURSO_DATABASE_URL"))
    parser.add_argument("--out", default="out", help="directory holding the shards")
    parser.add_argument("--pattern", default="part-*.jsonl")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit-files", type=int, default=None)
    parser.add_argument("--create-indexes", action="store_true")
    parser.add_argument(
        "--indexes-only",
        action="store_true",
        help="skip loading and only build the indexes (run after a bulk load)",
    )
    args = parser.parse_args(argv)

    token = os.environ.get("TURSO_AUTH_TOKEN")
    if not token:
        print("TURSO_AUTH_TOKEN is not set", file=sys.stderr)
        return 1
    if not args.url:
        print("pass --url or set TURSO_DATABASE_URL", file=sys.stderr)
        return 1

    url = args.url
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://") :]
    endpoint = Endpoint(url, token)

    endpoint.execute(SCHEMA.strip())
    endpoint.execute(STATE_SCHEMA.strip())
    state = get_state(endpoint)

    shards = sorted(Path(args.out).glob(args.pattern))
    if args.limit_files:
        shards = shards[: args.limit_files]
    if args.indexes_only:
        shards = []
    elif not shards:
        print(f"no files matched {args.pattern} in {args.out}", file=sys.stderr)
        return 1

    total_start = time.time()
    grand_total = 0
    for i, shard in enumerate(shards, start=1):
        done = state.get(shard.name, 0)
        n_lines = sum(1 for _ in shard.open(encoding="utf-8"))
        if done >= n_lines:
            print(f"[{i}/{len(shards)}] {shard.name}: already loaded, skipping")
            grand_total += n_lines
            continue
        started = time.time()
        sent = load_file(endpoint, shard, args.batch_size, args.workers, done)
        set_state(endpoint, shard.name, sent)
        elapsed = time.time() - started
        grand_total += sent
        rate = (sent - done) / elapsed if elapsed else 0
        print(
            f"[{i}/{len(shards)}] {shard.name}: {sent:,}/{n_lines:,} rows "
            f"({rate:,.0f} rows/s, {elapsed:.0f}s) | total {grand_total:,}",
            flush=True,
        )

    if args.create_indexes:
        print("creating indexes (this runs once, after the bulk load)...")
        for statement in INDEXES:
            t = time.time()
            endpoint.execute(statement, timeout=600)
            print(f"  {statement.split()[5]} in {time.time() - t:.0f}s")

    total_elapsed = time.time() - total_start
    print(f"\nloaded {grand_total:,} rows in {total_elapsed / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
