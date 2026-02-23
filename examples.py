#!/usr/bin/env python3
"""
Example: Custom Usage of Synthetic PHI Generator
================================================

This script demonstrates various ways to use the generator
programmatically with custom configurations.
"""

from generate_synthetic_phi import SyntheticPHIGenerator, print_annotated_record, print_frequency_report
import json


def example_1_basic_generation():
    """Example 1: Basic dataset generation"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Dataset Generation")
    print("="*80)
    
    generator = SyntheticPHIGenerator(seed=123)
    dataset = generator.generate_dataset(n_records=10, verbose=True)
    generator.write_jsonl(dataset, "example_basic.jsonl")
    
    print(f"\nGenerated {len(dataset)} records")
    print_annotated_record(dataset[0])


def example_2_custom_probabilities():
    """Example 2: Customize entity probabilities"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Custom Entity Probabilities")
    print("="*80)
    
    generator = SyntheticPHIGenerator(
        seed=456,
        min_entities_per_record=8,
        max_entities_per_record=20
    )
    
    # Increase probability of long-tail identifiers
    generator.entity_probabilities.update({
        "BIOMETRIC": 0.8,
        "IMAGE_REF": 0.7,
        "ID_VEHICLE": 0.6,
        "ID_DEVICE": 0.7,
        "URL": 0.6,
        "IP": 0.5,
    })
    
    dataset = generator.generate_dataset(n_records=50, verbose=True)
    
    # Check coverage
    report = generator.generate_entity_frequency_report(dataset)
    print_frequency_report(report)


def example_3_bio_tagging():
    """Example 3: BIO tagging for token classification"""
    print("\n" + "="*80)
    print("EXAMPLE 3: BIO Tagging for Token Classification")
    print("="*80)
    
    generator = SyntheticPHIGenerator(seed=789)
    dataset = generator.generate_dataset(n_records=5)
    
    # Convert to BIO format
    for i, record in enumerate(dataset[:2]):
        print(f"\nRecord {i+1}:")
        bio_tags = generator.convert_to_bio_tagging(record)
        
        print("Token".ljust(25), "Tag")
        print("-" * 50)
        for token, tag in bio_tags[:30]:  # Show first 30 tokens
            print(f"{token[:24].ljust(25)} {tag}")
        print(f"... ({len(bio_tags)} total tokens)")


def example_4_train_test_split():
    """Example 4: Create train/dev/test splits"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Train/Dev/Test Split")
    print("="*80)
    
    generator = SyntheticPHIGenerator(seed=111)
    full_dataset = generator.generate_dataset(n_records=1000, verbose=True)
    
    # Split into train/dev/test
    train, dev, test = generator.split_dataset(
        full_dataset,
        train_ratio=0.7,
        dev_ratio=0.15,
        test_ratio=0.15,
        shuffle=True
    )
    
    print(f"\nDataset split:")
    print(f"  Training:   {len(train):5d} records ({len(train)/len(full_dataset)*100:.1f}%)")
    print(f"  Development: {len(dev):5d} records ({len(dev)/len(full_dataset)*100:.1f}%)")
    print(f"  Test:        {len(test):5d} records ({len(test)/len(full_dataset)*100:.1f}%)")
    
    # Write splits
    generator.write_jsonl(train, "example_train_70.jsonl")
    generator.write_jsonl(dev, "example_dev_15.jsonl")
    generator.write_jsonl(test, "example_test_15.jsonl")


def example_5_validation():
    """Example 5: Built-in validation"""
    print("\n" + "="*80)
    print("EXAMPLE 5: Automatic Validation")
    print("="*80)
    
    generator = SyntheticPHIGenerator(seed=222)
    dataset = generator.generate_dataset(n_records=100, verbose=True)
    
    # Validate all records
    print("\nValidating all records...")
    errors = 0
    for record in dataset:
        try:
            generator.validate_entities(record["text"], record["entities"])
        except ValueError as e:
            print(f"❌ Validation error in {record['id']}: {e}")
            errors += 1
    
    if errors == 0:
        print(f"✓ All {len(dataset)} records passed validation!")
    else:
        print(f"❌ Found {errors} validation errors")
    
    # Verify offsets manually
    print("\nVerifying offset accuracy for first record:")
    record = dataset[0]
    for ent in record["entities"][:5]:
        extracted = record["text"][ent["start"]:ent["end"]]
        print(f"  [{ent['start']:4d}:{ent['end']:4d}] {ent['label']:15s} → \"{extracted}\"")


def example_6_coverage_analysis():
    """Example 6: HIPAA coverage analysis"""
    print("\n" + "="*80)
    print("EXAMPLE 6: HIPAA Safe Harbor Coverage Analysis")
    print("="*80)
    
    generator = SyntheticPHIGenerator(
        seed=333,
        min_entities_per_record=10,
        max_entities_per_record=20,
        include_long_tail_identifiers=True
    )
    
    # Generate larger dataset for better coverage
    dataset = generator.generate_dataset(n_records=500, verbose=True)
    
    # Analyze coverage
    report = generator.generate_entity_frequency_report(dataset)
    
    print(f"\nHIPAA Identifier Coverage:")
    print(f"  Total labels in schema: 26")
    print(f"  Labels found in dataset: {report['label_coverage']}")
    print(f"  Coverage: {report['label_coverage']/26*100:.1f}%")
    
    if report['missing_labels']:
        print(f"\n  Missing labels ({len(report['missing_labels'])}):")
        for label in report['missing_labels']:
            print(f"    - {label}")
        print("\n  💡 Tip: Generate more records or increase entity probabilities")
    else:
        print("\n  ✓ Complete HIPAA Safe Harbor coverage achieved!")
    
    # Show distribution
    print(f"\nEntity distribution:")
    sorted_labels = sorted(
        report['label_distribution'].items(),
        key=lambda x: -x[1]
    )
    for label, count in sorted_labels[:10]:
        pct = 100 * count / report['total_entities']
        bar = "█" * int(pct)
        print(f"  {label:20s} {count:5d} ({pct:5.2f}%) {bar}")


def example_7_single_record():
    """Example 7: Generate a single record"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Single Record Generation")
    print("="*80)
    
    generator = SyntheticPHIGenerator(seed=444)
    
    # Generate single record
    record = generator.build_record("custom_record_001")
    
    # Pretty print
    print_annotated_record(record)
    
    # Save as JSON (formatted)
    with open("example_single_record.json", "w") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    print("\n✓ Saved to example_single_record.json")


def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("SYNTHETIC PHI GENERATOR - USAGE EXAMPLES")
    print("="*80)
    
    examples = [
        ("Basic Generation", example_1_basic_generation),
        ("Custom Probabilities", example_2_custom_probabilities),
        ("BIO Tagging", example_3_bio_tagging),
        ("Train/Test Split", example_4_train_test_split),
        ("Validation", example_5_validation),
        ("Coverage Analysis", example_6_coverage_analysis),
        ("Single Record", example_7_single_record),
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nRunning all examples...\n")
    
    for name, example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("✓ ALL EXAMPLES COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()
