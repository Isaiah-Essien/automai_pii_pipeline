#!/usr/bin/env python3
"""
Medical Record Number (MRN) PII Generator
==========================================

Generates 10,000 sentences for each MRN variation format.
Total output: 5 formats × 10,000 sentences = 50,000 sentences

Features:
- Multiple MRN format variations
- Realistic medical/healthcare context sentences
- Random numeric and alphanumeric components
- Entity annotations with character offsets

Usage:
    python generate_mrn_pii.py
    
Output:
    mrn_pii_dataset.json - Complete dataset with entities
"""

import json
import random
from typing import List, Dict


class MRNPIIGenerator:
    """Generate MRN PII variations with sentences."""
    
    def __init__(self):
        """Initialize MRN generator with formats and templates."""
        
        # MRN variation formats
        self.variation_formats = [
            "{prefix}{number}",           # MRN123456
            "{prefix}-{number}",          # MRN-123456
            "{prefix} {number}",          # MRN 123456
            "{number}{suffix}",           # 123456MR
            "{prefix}{number}{suffix}"    # MRN123456R
        ]
        
        # MRN prefixes (common abbreviations)
        self.prefixes = [
            "MRN",
            "MR",
            "PT",
            "ID",
            "CHART",
            "REC",
            "PAT",
            "HOSP",
            "CLIN",
            "HC"
        ]
        
        # MRN suffixes
        self.suffixes = [
            "MR",
            "R",
            "A",
            "B",
            "C",
            "X",
            "Z"
        ]
        
        self.phi_label = "ID_MEDICAL"
        
        # Sentence templates for medical/healthcare context
        self.sentence_templates = [
            "Patient MRN: {MRN}.",
            "{NAME}'s medical record is {MRN}.",
            "Chart number {MRN} updated.",
            "Refer to medical record {MRN}.",
            "{NAME} (MRN: {MRN}) admitted.",
            "Record {MRN} shows history of diabetes.",
            "Pull chart {MRN} for review.",
            "Patient ID {MRN} matched.",
            "MRN {MRN} flagged for follow-up.",
            "File under {MRN}.",
            "Medical record {MRN} accessed.",
            "Chart {MRN} retrieved successfully.",
            "Patient record number: {MRN}.",
            "MRN {MRN} verified in system.",
            "Update medical record {MRN}.",
            "Chart {MRN} reviewed by physician.",
            "Refer to {MRN} for previous records.",
            "Patient {NAME} identified by MRN {MRN}.",
            "Medical record {MRN} linked to admission.",
            "Scan {MRN} into electronic system.",
            "Cross-reference with {MRN}.",
            "MRN index updated with {MRN}.",
            "Record {MRN} contains discharge summary.",
            "Chart {MRN} shows allergy history.",
            "Patient chart {MRN} complete.",
            "MRN {MRN} created on admission.",
            "Link appointment to {MRN}.",
            "Attach lab results to {MRN}.",
            "Medical record {MRN} purged after 7 years.",
            "Archive {MRN} to cold storage.",
            "Retrieve archived record {MRN}.",
            "MRN {MRN} flagged as duplicate.",
            "Merge {MRN} with primary record.",
            "Chart {MRN} incomplete.",
            "Complete medical record {MRN}.",
            "MRN {MRN} stored in EHR.",
            "Access controlled for {MRN}.",
            "Audit trail for {MRN} reviewed.",
            "Patient authorization required for {MRN}.",
            "Billing links to {MRN}.",
            "Insurance verification for {MRN}.",
            "Authorization code {MRN} processed.",
            "Medical record {MRN} released to patient.",
            "Request copies of {MRN}.",
            "Fax {MRN} to referring physician.",
            "Email {MRN} to primary care doctor.",
            "MRN {MRN} transferred to new facility.",
            "Continuity of care documented in {MRN}.",
            "Discharge plan in {MRN}.",
            "Follow-up instructions in {MRN}.",
            "Medication list in {MRN}.",
            "Problem list documented in {MRN}.",
            "Immunization record in {MRN}.",
            "Vital signs recorded in {MRN}.",
            "Physical exam findings documented in {MRN}.",
            "Lab results filed in {MRN}.",
            "Imaging studies in {MRN}.",
            "Surgical reports in {MRN}.",
            "Pathology reports in {MRN}.",
            "Consultant notes in {MRN}.",
            "Progress notes in {MRN}.",
            "Nursing documentation in {MRN}.",
            "Respiratory therapy notes in {MRN}.",
            "Physical therapy notes in {MRN}.",
            "Dietary notes in {MRN}.",
            "Social work notes in {MRN}.",
            "Mental health documentation in {MRN}.",
            "Substance abuse screening in {MRN}.",
            "Allergy documentation in {MRN}.",
            "Medication reconciliation in {MRN}.",
            "Drug interaction check for {MRN}.",
            "Adverse event reported in {MRN}.",
            "Quality assurance review of {MRN}.",
            "Compliance audit of {MRN}.",
            "Medical necessity review for {MRN}.",
            "Prior authorization attached to {MRN}.",
            "Insurance explanation in {MRN}.",
            "Payment posting to {MRN}.",
            "Outstanding balance for {MRN}.",
            "Statement sent for {MRN}.",
            "Collections action on {MRN}.",
            "Refund processed for {MRN}.",
            "Tax reporting for {MRN}.",
            "Research use approved for {MRN}.",
            "IRB study protocol linked to {MRN}.",
            "Consent form signed for {MRN}.",
            "Data extraction from {MRN}.",
            "Privacy impact assessment for {MRN}.",
            "HIPAA violation investigation of {MRN}.",
            "Security incident involving {MRN}.",
            "Breach notification for {MRN}.",
            "Data integrity check for {MRN}.",
            "Backup verification including {MRN}.",
            "Disaster recovery test with {MRN}.",
            "System restoration of {MRN}.",
            "Third-party access logged for {MRN}.",
            "Family member access to {MRN}.",
            "Power of attorney authorization for {MRN}.",
            "Minor's guardian authorization for {MRN}.",
            "Competency assessment documented in {MRN}.",
            "Advance directive in {MRN}.",
            "Do Not Resuscitate order in {MRN}.",
            "POLST form in {MRN}.",
            "Living will documentation in {MRN}.",
            "Organ donation status in {MRN}.",
            "Autopsy request in {MRN}.",
            "Death notification for {MRN}.",
            "Post-mortem documentation in {MRN}.",
            "Legacy preservation of {MRN}.",
        ]
    
    def generate_random_number(self, digits: int = 6) -> str:
        """Generate random number with specified digits."""
        return str(random.randint(10**(digits-1), 10**digits - 1))
    
    def generate_mrn_components(self) -> Dict:
        """Generate random MRN components."""
        return {
            'prefix': random.choice(self.prefixes),
            'number': self.generate_random_number(random.choice([5, 6, 7, 8])),
            'suffix': random.choice(self.suffixes)
        }
    
    def apply_format(self, components: Dict, format_pattern: str) -> str:
        """Apply format pattern to MRN components."""
        try:
            return format_pattern.format(**components)
        except KeyError:
            return None
    
    def create_sentence(self, mrn_value: str) -> Dict:
        """Create sentence with MRN PII and entity annotation."""
        
        # Select random sentence template
        template = random.choice(self.sentence_templates)
        
        # Replace {MRN} with actual MRN value
        sentence = template.replace('{MRN}', mrn_value)
        
        # Replace {NAME} if present with a random name
        if '{NAME}' in sentence:
            # Use simple names for variety
            first_names = ['John', 'Mary', 'James', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
                          'Kamau', 'Wanjiru', 'Ochieng', 'Njoki', 'Otieno', 'Kipchoge', 'Amara', 'Kwame']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                         'Mwangi', 'Kiplagat', 'Okonkwo', 'Mensah', 'Nkosi', 'Dlamini', 'Tesfaye', 'Girma']
            name = f"{random.choice(first_names)} {random.choice(last_names)}"
            sentence = sentence.replace('{NAME}', name)
        
        # Find entity position
        start_pos = sentence.find(mrn_value)
        end_pos = start_pos + len(mrn_value)
        
        return {
            'text': sentence,
            'entities': [{
                'start': start_pos,
                'end': end_pos,
                'label': self.phi_label,
                'value': mrn_value
            }]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, 
                                    num_sentences: int = 10000,
                                    start_id: int = 1) -> List[Dict]:
        """Generate dataset for one MRN format variation."""
        
        dataset = []
        
        for i in range(num_sentences):
            # Generate MRN components
            components = self.generate_mrn_components()
            
            # Apply format pattern
            mrn_value = self.apply_format(components, format_pattern)
            
            if mrn_value is None:
                continue
            
            # Create sentence
            sentence_data = self.create_sentence(mrn_value)
            
            # Add ID in format "mrn_000001"
            sentence_id = start_id + i
            sentence_data['id'] = f"mrn_{sentence_id:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict:
        """Generate complete dataset for all MRN format variations."""
        
        print(f"Generating {sentences_per_format} sentences for each of {len(self.variation_formats)} formats...")
        print("=" * 80)
        
        all_data = {
            'metadata': {
                'total_formats': len(self.variation_formats),
                'sentences_per_format': sentences_per_format,
                'total_sentences': len(self.variation_formats) * sentences_per_format,
                'phi_type': 'MEDICAL_RECORD',
                'phi_label': self.phi_label,
                'total_prefixes': len(self.prefixes),
                'total_suffixes': len(self.suffixes)
            },
            'formats': {}
        }
        
        current_id = 1  # Track continuous ID across all formats
        
        for idx, format_pattern in enumerate(self.variation_formats, 1):
            print(f"[{idx}/{len(self.variation_formats)}] Generating format: {format_pattern}")
            
            dataset = self.generate_dataset_for_format(
                format_pattern, 
                sentences_per_format,
                start_id=current_id
            )
            
            # Store by format pattern
            format_key = f"format_{idx:02d}"
            all_data['formats'][format_key] = {
                'pattern': format_pattern,
                'num_sentences': len(dataset),
                'sentences': dataset
            }
            
            # Update ID counter
            current_id += len(dataset)
            
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: mrn_{current_id-len(dataset):06d} to mrn_{current_id-1:06d})")
        
        print("=" * 80)
        print(f"✓ Total sentences generated: {all_data['metadata']['total_sentences']:,}")
        
        return all_data
    
    def save_dataset(self, dataset: Dict, output_path: str = "mrn_pii_dataset.json"):
        """Save dataset to JSON file."""
        print(f"\nSaving to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        
        # Calculate file size
        import os
        file_size = os.path.getsize(output_path)
        size_mb = file_size / (1024 * 1024)
        
        print(f"✓ Saved successfully!")
        print(f"  File size: {size_mb:.2f} MB")
        print(f"  Location: {output_path}")
    
    def save_template_dataset(self, dataset: Dict, output_path: str = "mrn_pii_templates.json"):
        """Save dataset with {MRN} placeholder instead of actual values."""
        print(f"\nCreating template dataset with {{MRN}} placeholders...")
        
        template_data = {
            'metadata': dataset['metadata'].copy(),
            'formats': {}
        }
        
        for format_key, format_data in dataset['formats'].items():
            template_sentences = []
            
            for sentence in format_data['sentences']:
                # Replace actual MRN value with {MRN} placeholder
                original_text = sentence['text']
                entity = sentence['entities'][0]
                mrn_value = entity['value']
                
                # Create template by replacing MRN value with {MRN}
                template_text = original_text.replace(mrn_value, '{MRN}')
                
                template_sentences.append({
                    'id': sentence['id'],
                    'text': template_text
                })
            
            template_data['formats'][format_key] = {
                'pattern': format_data['pattern'],
                'num_sentences': len(template_sentences),
                'sentences': template_sentences
            }
        
        # Save template file
        print(f"Saving templates to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        # Calculate file size
        import os
        file_size = os.path.getsize(output_path)
        size_mb = file_size / (1024 * 1024)
        
        print(f"✓ Template file saved successfully!")
        print(f"  File size: {size_mb:.2f} MB")
        print(f"  Location: {output_path}")


def main():
    """Main execution function."""
    
    print("=" * 80)
    print("MEDICAL RECORD NUMBER (MRN) PII DATASET GENERATOR")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = MRNPIIGenerator()
    
    # Show configuration
    print("Configuration:")
    print(f"  - MRN formats: {len(generator.variation_formats)}")
    print(f"  - Sentence templates: {len(generator.sentence_templates)}")
    print(f"  - MRN prefixes: {len(generator.prefixes)}")
    print(f"  - MRN suffixes: {len(generator.suffixes)}")
    print(f"  - Sentences per format: 10,000")
    print(f"  - Total output: {len(generator.variation_formats) * 10000:,} sentences")
    print()
    
    # Show sample formats
    print("MRN Format Variations:")
    for i, fmt in enumerate(generator.variation_formats, 1):
        print(f"  {i}. {fmt}")
    print()
    
    # Show sample prefixes and suffixes
    print(f"Sample Prefixes: {', '.join(generator.prefixes[:5])} ...")
    print(f"Sample Suffixes: {', '.join(generator.suffixes[:5])}")
    print()
    
    # Generate dataset - 20,000 sentences per format (5 formats × 20,000 = 100,000 total)
    dataset = generator.generate_complete_dataset(sentences_per_format=20000)
    
    # Save to file
    generator.save_dataset(dataset, "mrn_pii_dataset.json")
    
    # Save template version with {MRN} placeholders
    generator.save_template_dataset(dataset, "mrn_pii_templates.json")
    
    print()
    print("=" * 80)
    print("GENERATION COMPLETE!")
    print("=" * 80)
    print()
    
    # Show sample sentences
    print("Sample sentences from each format:")
    print("-" * 80)
    for format_key, format_data in list(dataset['formats'].items())[:3]:
        sample = format_data['sentences'][0]
        print(f"\nFormat: {format_data['pattern']}")
        entity = sample['entities'][0]
        print(f"  MRN: '{entity['value']}'")
        print(f"  Sentence: {sample['text']}")
        
        # Show template version
        template_text = sample['text'].replace(entity['value'], '{MRN}')
        print(f"  Template: {template_text}")
    print()


if __name__ == "__main__":
    main()
