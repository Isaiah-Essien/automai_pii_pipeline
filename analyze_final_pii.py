#!/usr/bin/env python3
"""Brief analysis of merged PII data in data/final_pii/."""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "data" / "final_pii"


def analyze() -> None:
    """Print record counts and file sizes per PII type."""
    if not OUTPUT_DIR.exists():
        print(f"Output dir not found: {OUTPUT_DIR}")
        return

    files = sorted(OUTPUT_DIR.glob("*.json"))
    files = [f for f in files if f.name != ".merge_state.json"]

    print("PII Analysis")
    print("-" * 50)
    total_records = 0
    total_mb = 0.0

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = len(data)
        size_mb = path.stat().st_size / (1024 * 1024)
        total_records += count
        total_mb += size_mb
        name = path.stem.replace("_", " ").title()
        print(f"  {name:25} {count:>12,} records  {size_mb:>6.2f} MB")

    print("-" * 50)
    print(f"  {'Total':25} {total_records:>12,} records  {total_mb:>6.2f} MB")
    print(f"\nLocation: {OUTPUT_DIR}")


if __name__ == "__main__":
    analyze()
