#!/usr/bin/env python3
"""
Pretty Print JSONL Records
==========================

Utility to display JSONL records in a human-readable format.
"""

import json
import sys


def print_record_pretty(record: dict, show_full_text: bool = False):
    """Pretty print a single record."""
    print("\n" + "="*80)
    print(f"📄 Record ID: {record['id']}")
    print("="*80)
    
    # Metadata
    print(f"\n📋 Metadata:")
    print(f"   Source:   {record.get('source', 'N/A')}")
    print(f"   Domain:   {record.get('domain', 'N/A')}")
    print(f"   Language: {record.get('lang', 'N/A')}")
    
    # Text
    text = record.get('text', '')
    print(f"\n📝 Text ({len(text)} characters):")
    print("-" * 80)
    if show_full_text or len(text) <= 500:
        print(text)
    else:
        print(text[:500] + "\n... (truncated)")
    print("-" * 80)
    
    # Entities
    entities = record.get('entities', [])
    print(f"\n🏷️  Entities ({len(entities)} total):")
    print(f"{'Start':>6} {'End':>6}  {'Label':20}  Entity Text")
    print("-" * 80)
    
    for ent in entities:
        start = ent['start']
        end = ent['end']
        label = ent['label']
        entity_text = text[start:end]
        
        # Truncate long entity text
        if len(entity_text) > 40:
            entity_text = entity_text[:37] + "..."
        
        print(f"{start:6d} {end:6d}  {label:20}  \"{entity_text}\"")
    
    # Entity type distribution
    label_counts = {}
    for ent in entities:
        label = ent['label']
        label_counts[label] = label_counts.get(label, 0) + 1
    
    print(f"\n📊 Entity Distribution:")
    for label, count in sorted(label_counts.items(), key=lambda x: -x[1]):
        print(f"   {label:20} × {count}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python pretty_print.py <jsonl_file> [record_number]")
        print("\nExamples:")
        print("  python pretty_print.py synthetic_phi_sample.jsonl")
        print("  python pretty_print.py synthetic_phi_sample.jsonl 5")
        sys.exit(1)
    
    filepath = sys.argv[1]
    record_num = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print("="*80)
    print(f"📂 File: {filepath}")
    print("="*80)
    
    # Load records
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
    
    print(f"\nLoaded {len(records)} records")
    
    # Display specific record or first 3
    if record_num is not None:
        if 1 <= record_num <= len(records):
            print_record_pretty(records[record_num - 1], show_full_text=True)
        else:
            print(f"\n❌ Error: Record number must be between 1 and {len(records)}")
            sys.exit(1)
    else:
        # Show first 3 records
        num_to_show = min(3, len(records))
        print(f"\nShowing first {num_to_show} records:\n")
        for i in range(num_to_show):
            print_record_pretty(records[i])
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
