#!/usr/bin/env python3
"""Display sample name PHI records."""

import json
import sys
import random


def show_names(filepath: str, num_samples: int = 5):
    """Show sample name records."""
    with open(filepath, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f if line.strip()]
    
    print(f"Name PHI Dataset: {len(records)} total records\n")
    
    # Randomly select records for variety
    samples = random.sample(records, min(num_samples, len(records)))
    
    for i, record in enumerate(samples, 1):
        print(f"[{i}] {record['text']}")
        names = [record['text'][e['start']:e['end']] for e in record['entities']]
        print(f"    Names: {', '.join(names)}\n")


if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "../generated_data/name_phi_data.jsonl"
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    show_names(filepath, num_samples)
