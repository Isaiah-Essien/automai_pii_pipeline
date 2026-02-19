#!/usr/bin/env python3
"""
JSONL Dataset Validator and Analyzer
====================================

Utility script to validate and analyze generated synthetic PHI datasets.
"""

import json
import sys
from collections import Counter
from typing import List, Dict


def load_jsonl(filepath: str) -> List[Dict]:
    """Load JSONL file."""
    records = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())
                records.append(record)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing line {line_num}: {e}")
    return records


def validate_record_schema(record: Dict, record_idx: int) -> List[str]:
    """Validate record against expected schema."""
    errors = []
    
    # Check required fields
    required_fields = ["id", "text", "entities", "source", "domain", "lang"]
    for field in required_fields:
        if field not in record:
            errors.append(f"Record {record_idx}: Missing required field '{field}'")
    
    # Validate entities structure
    if "entities" in record:
        if not isinstance(record["entities"], list):
            errors.append(f"Record {record_idx}: 'entities' must be a list")
        else:
            for ent_idx, entity in enumerate(record["entities"]):
                if not isinstance(entity, dict):
                    errors.append(f"Record {record_idx}, Entity {ent_idx}: Must be a dict")
                    continue
                
                # Check entity fields
                required_ent_fields = ["start", "end", "label"]
                for field in required_ent_fields:
                    if field not in entity:
                        errors.append(
                            f"Record {record_idx}, Entity {ent_idx}: Missing field '{field}'"
                        )
    
    return errors


def validate_entity_offsets(record: Dict, record_idx: int) -> List[str]:
    """Validate entity offsets match text."""
    errors = []
    text = record.get("text", "")
    entities = record.get("entities", [])
    
    for ent_idx, entity in enumerate(entities):
        start = entity.get("start")
        end = entity.get("end")
        label = entity.get("label")
        
        if start is None or end is None:
            continue
        
        # Check bounds
        if start < 0 or end > len(text):
            errors.append(
                f"Record {record_idx}, Entity {ent_idx}: "
                f"Offset [{start}:{end}] out of bounds for text length {len(text)}"
            )
            continue
        
        if start >= end:
            errors.append(
                f"Record {record_idx}, Entity {ent_idx}: "
                f"Invalid offset range [{start}:{end}]"
            )
            continue
        
        # Validate extraction
        extracted = text[start:end]
        if not extracted:
            errors.append(
                f"Record {record_idx}, Entity {ent_idx}: "
                f"Empty entity at [{start}:{end}]"
            )
    
    return errors


def check_overlapping_entities(record: Dict, record_idx: int) -> List[str]:
    """Check for overlapping entity spans."""
    errors = []
    entities = record.get("entities", [])
    
    for i, ent1 in enumerate(entities):
        for j, ent2 in enumerate(entities[i+1:], i+1):
            start1, end1 = ent1.get("start"), ent1.get("end")
            start2, end2 = ent2.get("start"), ent2.get("end")
            
            if start1 is None or end1 is None or start2 is None or end2 is None:
                continue
            
            # Check overlap
            if not (end1 <= start2 or end2 <= start1):
                errors.append(
                    f"Record {record_idx}: Overlapping entities at "
                    f"[{start1}:{end1}] and [{start2}:{end2}]"
                )
    
    return errors


def analyze_dataset(records: List[Dict]) -> Dict:
    """Generate comprehensive dataset statistics."""
    stats = {
        "total_records": len(records),
        "total_entities": 0,
        "label_counts": Counter(),
        "entities_per_record": [],
        "text_lengths": [],
        "sources": Counter(),
        "domains": Counter(),
        "languages": Counter(),
    }
    
    for record in records:
        entities = record.get("entities", [])
        stats["total_entities"] += len(entities)
        stats["entities_per_record"].append(len(entities))
        stats["text_lengths"].append(len(record.get("text", "")))
        
        for entity in entities:
            stats["label_counts"][entity.get("label")] += 1
        
        stats["sources"][record.get("source")] += 1
        stats["domains"][record.get("domain")] += 1
        stats["languages"][record.get("lang")] += 1
    
    # Calculate averages
    if stats["total_records"] > 0:
        stats["avg_entities_per_record"] = stats["total_entities"] / stats["total_records"]
        stats["avg_text_length"] = sum(stats["text_lengths"]) / stats["total_records"]
        stats["min_entities"] = min(stats["entities_per_record"])
        stats["max_entities"] = max(stats["entities_per_record"])
    
    return stats


def print_validation_report(
    records: List[Dict],
    schema_errors: List[str],
    offset_errors: List[str],
    overlap_errors: List[str]
):
    """Pretty print validation report."""
    print("\n" + "="*80)
    print("VALIDATION REPORT")
    print("="*80)
    
    total_errors = len(schema_errors) + len(offset_errors) + len(overlap_errors)
    
    print(f"\nTotal Records: {len(records)}")
    print(f"Total Errors: {total_errors}")
    
    if total_errors == 0:
        print("\n✅ ALL VALIDATIONS PASSED!")
    else:
        print("\n❌ VALIDATION FAILURES DETECTED\n")
        
        if schema_errors:
            print(f"Schema Errors ({len(schema_errors)}):")
            for error in schema_errors[:10]:
                print(f"  • {error}")
            if len(schema_errors) > 10:
                print(f"  ... and {len(schema_errors) - 10} more")
        
        if offset_errors:
            print(f"\nOffset Errors ({len(offset_errors)}):")
            for error in offset_errors[:10]:
                print(f"  • {error}")
            if len(offset_errors) > 10:
                print(f"  ... and {len(offset_errors) - 10} more")
        
        if overlap_errors:
            print(f"\nOverlap Errors ({len(overlap_errors)}):")
            for error in overlap_errors[:10]:
                print(f"  • {error}")
            if len(overlap_errors) > 10:
                print(f"  ... and {len(overlap_errors) - 10} more")


def print_analysis_report(stats: Dict):
    """Pretty print analysis report."""
    print("\n" + "="*80)
    print("DATASET ANALYSIS")
    print("="*80)
    
    print(f"\nDataset Overview:")
    print(f"  Total Records: {stats['total_records']:,}")
    print(f"  Total Entities: {stats['total_entities']:,}")
    print(f"  Avg Entities/Record: {stats.get('avg_entities_per_record', 0):.2f}")
    print(f"  Min Entities/Record: {stats.get('min_entities', 0)}")
    print(f"  Max Entities/Record: {stats.get('max_entities', 0)}")
    print(f"  Avg Text Length: {stats.get('avg_text_length', 0):.0f} characters")
    
    print(f"\nLabel Distribution ({len(stats['label_counts'])} unique labels):")
    sorted_labels = sorted(stats['label_counts'].items(), key=lambda x: -x[1])
    for label, count in sorted_labels:
        pct = 100 * count / stats['total_entities'] if stats['total_entities'] > 0 else 0
        bar = "█" * min(50, int(pct * 2))
        print(f"  {label:20s} {count:6,d} ({pct:5.2f}%) {bar}")
    
    print(f"\nMetadata:")
    print(f"  Sources: {dict(stats['sources'])}")
    print(f"  Domains: {dict(stats['domains'])}")
    print(f"  Languages: {dict(stats['languages'])}")


def main():
    """Main validation and analysis."""
    if len(sys.argv) < 2:
        print("Usage: python validate_dataset.py <jsonl_file>")
        print("\nExample:")
        print("  python validate_dataset.py synthetic_phi_full.jsonl")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    print("="*80)
    print(f"VALIDATING: {filepath}")
    print("="*80)
    
    # Load dataset
    print("\n[1] Loading dataset...")
    records = load_jsonl(filepath)
    print(f"✓ Loaded {len(records)} records")
    
    # Validate schema
    print("\n[2] Validating schema...")
    schema_errors = []
    for idx, record in enumerate(records):
        schema_errors.extend(validate_record_schema(record, idx))
    print(f"✓ Schema validation complete ({len(schema_errors)} errors)")
    
    # Validate offsets
    print("\n[3] Validating entity offsets...")
    offset_errors = []
    for idx, record in enumerate(records):
        offset_errors.extend(validate_entity_offsets(record, idx))
    print(f"✓ Offset validation complete ({len(offset_errors)} errors)")
    
    # Check overlaps
    print("\n[4] Checking for overlapping entities...")
    overlap_errors = []
    for idx, record in enumerate(records):
        overlap_errors.extend(check_overlapping_entities(record, idx))
    print(f"✓ Overlap check complete ({len(overlap_errors)} errors)")
    
    # Analyze dataset
    print("\n[5] Analyzing dataset statistics...")
    stats = analyze_dataset(records)
    print(f"✓ Analysis complete")
    
    # Print reports
    print_validation_report(records, schema_errors, offset_errors, overlap_errors)
    print_analysis_report(stats)
    
    print("\n" + "="*80)
    print("✓ VALIDATION AND ANALYSIS COMPLETE")
    print("="*80)
    
    # Exit code
    total_errors = len(schema_errors) + len(offset_errors) + len(overlap_errors)
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
