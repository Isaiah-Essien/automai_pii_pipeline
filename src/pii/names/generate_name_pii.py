#!/usr/bin/env python3
"""
Name PII Generator - African Names
==================================

Generates 10,000 sentences for each NAME variation format.
Total output: 13 formats × 10,000 sentences = 130,000 sentences

Features:
- African names from 15+ countries
- 13 variation formats (first/middle/last name combinations)
- Medical/healthcare context sentences
- Entity annotations with character offsets

Usage:
    python generate_name_pii.py
    
Output:
    name_pii_dataset.json - Complete dataset with entities
"""

import json
import random
from typing import List, Dict, Tuple


class NamePIIGenerator:
    """Generate name PII variations with sentences."""
    
    def __init__(self, 
                 names_path: str = "african_names.json",
                 schema_path: str = "../pii_variation_schema.json"):
        """Initialize with names and schema files."""
        
        # Load African names
        with open(names_path, 'r', encoding='utf-8') as f:
            self.names_data = json.load(f)
        
        # Try to load schema (optional, for reference)
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
                self.name_config = schema.get('pii_types', {}).get('NAME', {})
        except:
            self.name_config = {}
        
        # Extract names
        self.titles = self.names_data.get('titles', [])
        self.suffixes = self.names_data.get('suffixes', [])
        
        # Flatten first names
        self.first_names = []
        for region_data in self.names_data['first_names'].values():
            if isinstance(region_data, dict):
                for country_names in region_data.values():
                    self.first_names.extend(country_names)
            else:
                self.first_names.extend(region_data)
        
        # Flatten middle names
        self.middle_names = []
        for region_names in self.names_data['middle_names'].values():
            self.middle_names.extend(region_names)
        
        # Flatten last names
        self.last_names = []
        for region_data in self.names_data['last_names'].values():
            if isinstance(region_data, dict):
                for country_names in region_data.values():
                    self.last_names.extend(country_names)
            else:
                self.last_names.extend(region_data)
        
        # Variation formats
        self.variation_formats = [
            "{first_name} {last_name}",
            "{first_name} {middle_initial}. {last_name}",
            "{first_name} {middle_name} {last_name}",
            "{title} {first_name} {last_name}",
            "{title} {first_name} {middle_initial}. {last_name}",
            "{last_name}, {first_name}",
            "{last_name}, {first_name} {middle_initial}.",
            "{first_initial}. {last_name}",
            "{first_initial}. {middle_initial}. {last_name}",
            "{first_initial} {last_name}",
            "{first_name} {last_name} {suffix}",
            "{title} {first_name} {middle_name} {last_name} {suffix}",
            "{last_name}, {first_name} {middle_initial}."
        ]
        
        self.phi_label = "PERSON"
        
        # Sentence templates for medical/healthcare context
        self.sentence_templates = [
            "The patient {NAME} was admitted to the ward.",
            "Patient {NAME} arrived at the clinic this morning.",
            "Dr. {NAME} is responsible for this case.",
            "The nurse {NAME} assisted with the procedure.",
            "Medical record for {NAME} has been updated.",
            "Next of kin is {NAME}.",
            "Emergency contact: {NAME}.",
            "{NAME} was diagnosed with the condition.",
            "The physician {NAME} recommended treatment.",
            "Patient {NAME} is scheduled for surgery.",
            "Consultation with {NAME} completed.",
            "Lab results sent to {NAME}.",
            "Prescription issued to {NAME}.",
            "Appointment confirmed for {NAME}.",
            "Insurance information for {NAME} verified.",
            "Hospital staff member {NAME} on duty today.",
            "The attending physician is {NAME}.",
            "Discharge summary for {NAME} prepared.",
            "Follow-up appointment for {NAME} scheduled.",
            "Referral letter sent to {NAME}.",
            "Medical decision made by {NAME}.",
            "{NAME} consented to the procedure.",
            "Vital signs recorded for {NAME}.",
            "Physical exam performed on {NAME}.",
            "Chart review completed for {NAME}.",
            "Case discussed with {NAME}.",
            "Treatment plan approved by {NAME}.",
            "Patient education provided to {NAME}.",
            "Medication prescribed for {NAME}.",
            "Home health care arranged for {NAME}.",
            "Rehabilitation therapy for {NAME} initiated.",
            "Imaging study scheduled for {NAME}.",
            "Lab work ordered for {NAME}.",
            "Specialist consultation with {NAME} complete.",
            "Immunization administered to {NAME}.",
            "Allergy information for {NAME} documented.",
            "Surgical consent signed by {NAME}.",
            "Anesthesia cleared for {NAME}.",
            "Post-operative care for {NAME} initiated.",
            "Recovery room assignment for {NAME}.",
            "Intensive care monitoring started for {NAME}.",
            "Telemetry monitoring for {NAME} ordered.",
            "Medication list updated for {NAME}.",
            "Dietary restrictions documented for {NAME}.",
            "Nursing care plan developed for {NAME}.",
            "Quality review conducted by {NAME}.",
            "Staff competency assessment by {NAME}.",
            "Performance evaluation for {NAME} completed.",
            "Training provided to {NAME}.",
            "Credentialing documentation for {NAME} submitted.",
            "Credentials verified for {NAME}.",
            "{NAME} completed orientation training.",
            "Clinical supervision provided to {NAME}.",
            "Mentor assigned: {NAME}.",
            "Preceptorship program for {NAME} started.",
            "Continuing education attended by {NAME}.",
            "Compliance training for {NAME} scheduled.",
            "Background check completed for {NAME}.",
            "Drug screening for {NAME} completed.",
            "Vaccination records for {NAME} reviewed.",
            "Health screening for {NAME} performed.",
            "Fitness-for-duty evaluation for {NAME}.",
            "Return-to-work clearance for {NAME} issued.",
            "Workers' compensation claim by {NAME}.",
            "Occupational health visit for {NAME}.",
            "Incident report filed by {NAME}.",
            "Accident report involving {NAME}.",
            "Safety training attended by {NAME}.",
            "Equipment training for {NAME} completed.",
            "Protocol review with {NAME}.",
            "Ethics consultation requested by {NAME}.",
            "Infection control training for {NAME}.",
            "Hand hygiene audit by {NAME}.",
            "Patient safety officer {NAME} on call.",
            "Quality improvement meeting with {NAME}.",
            "Departmental meeting led by {NAME}.",
            "Case conference presentation by {NAME}.",
            "Grand rounds presentation by {NAME}.",
            "Journal club discussion led by {NAME}.",
            "Research protocol reviewed by {NAME}.",
            "Patient advocate {NAME} contacted.",
            "Social work consult ordered for {NAME}.",
            "Chaplain {NAME} provided spiritual support.",
            "Pharmacy consult with {NAME} completed.",
            "Nutrition assessment by {NAME}.",
            "Physical therapy evaluation by {NAME}.",
            "Occupational therapy started for {NAME}.",
            "Speech therapy for {NAME} initiated.",
            "Mental health evaluation for {NAME}.",
            "Psychological assessment by {NAME}.",
            "Substance abuse screening for {NAME}.",
            "Pain management plan for {NAME} created.",
            "Palliative care consultation with {NAME}.",
            "End-of-life planning with {NAME}.",
            "Advance directive reviewed with {NAME}.",
            "DNR status discussed with {NAME}.",
            "Family meeting held with {NAME}.",
            "Caregiver training provided to {NAME}.",
            "Custody evaluation by {NAME}.",
            "Court order compliance documented by {NAME}.",
            "Telemedicine consultation with {NAME}.",
            "Remote monitoring for {NAME} activation.",
            "Patient portal setup for {NAME}.",
            "Electronic health record created for {NAME}.",
        ]
    
    def get_name_components(self) -> Dict:
        """Generate random name components."""
        first_name = random.choice(self.first_names)
        middle_name = random.choice(self.middle_names)
        last_name = random.choice(self.last_names)
        title = random.choice(self.titles)
        suffix = random.choice(self.suffixes)
        
        return {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'first_initial': first_name[0],
            'middle_initial': middle_name[0],
            'title': title,
            'suffix': suffix
        }
    
    def apply_format(self, components: Dict, format_pattern: str) -> str:
        """Apply format pattern to name components."""
        try:
            return format_pattern.format(**components)
        except KeyError:
            # Handle case where a placeholder is missing
            return format_pattern
    
    def create_sentence(self, name_value: str) -> Dict:
        """Create sentence with name PII and entity annotation."""
        
        # Select random sentence template
        template = random.choice(self.sentence_templates)
        
        # Replace {NAME} with actual name value
        sentence = template.replace('{NAME}', name_value)
        
        # Find entity position
        start_pos = sentence.find(name_value)
        end_pos = start_pos + len(name_value)
        
        return {
            'text': sentence,
            'entities': [{
                'start': start_pos,
                'end': end_pos,
                'label': self.phi_label,
                'value': name_value
            }]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, 
                                    num_sentences: int = 10000,
                                    start_id: int = 1) -> List[Dict]:
        """Generate dataset for one name format variation."""
        
        dataset = []
        
        for i in range(num_sentences):
            # Generate name components
            components = self.get_name_components()
            
            # Apply format pattern
            name_value = self.apply_format(components, format_pattern)
            
            # Create sentence
            sentence_data = self.create_sentence(name_value)
            
            # Add ID in format "name_000001"
            sentence_id = start_id + i
            sentence_data['id'] = f"name_{sentence_id:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict:
        """Generate complete dataset for all name format variations."""
        
        print(f"Generating {sentences_per_format} sentences for each of {len(self.variation_formats)} formats...")
        print("=" * 80)
        
        all_data = {
            'metadata': {
                'total_formats': len(self.variation_formats),
                'sentences_per_format': sentences_per_format,
                'total_sentences': len(self.variation_formats) * sentences_per_format,
                'phi_type': 'PERSON',
                'phi_label': self.phi_label,
                'african_countries': 15,
                'first_names_count': len(set(self.first_names)),
                'middle_names_count': len(set(self.middle_names)),
                'last_names_count': len(set(self.last_names))
            },
            'formats': {}
        }
        
        current_id = 1  # Track continuous ID across all formats
        
        for idx, format_pattern in enumerate(self.variation_formats, 1):
            print(f"[{idx:2d}/{len(self.variation_formats)}] Generating format: {format_pattern[:60]}")
            
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
            
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: name_{current_id-len(dataset):06d} to name_{current_id-1:06d})")
        
        print("=" * 80)
        print(f"✓ Total sentences generated: {all_data['metadata']['total_sentences']:,}")
        
        return all_data
    
    def save_dataset(self, dataset: Dict, output_path: str = "name_pii_dataset.json"):
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
    
    def save_template_dataset(self, dataset: Dict, output_path: str = "name_pii_templates.json"):
        """Save dataset with {NAME} placeholder instead of actual values."""
        print(f"\nCreating template dataset with {{NAME}} placeholders...")
        
        template_data = {
            'metadata': dataset['metadata'].copy(),
            'formats': {}
        }
        
        for format_key, format_data in dataset['formats'].items():
            template_sentences = []
            
            for sentence in format_data['sentences']:
                # Replace actual name value with {NAME} placeholder
                original_text = sentence['text']
                entity = sentence['entities'][0]
                name_value = entity['value']
                
                # Create template by replacing name value with {NAME}
                template_text = original_text.replace(name_value, '{NAME}')
                
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
    print("NAME PII DATASET GENERATOR - AFRICAN NAMES")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = NamePIIGenerator()
    
    # Show configuration
    print("Configuration:")
    print(f"  - Name formats: {len(generator.variation_formats)}")
    print(f"  - Sentence templates: {len(generator.sentence_templates)}")
    print(f"  - Unique first names: {len(set(generator.first_names))}")
    print(f"  - Unique middle names: {len(set(generator.middle_names))}")
    print(f"  - Unique last names: {len(set(generator.last_names))}")
    print(f"  - Sentences per format: 10,000")
    print(f"  - Total output: {len(generator.variation_formats) * 10000:,} sentences")
    print()
    
    # Show sample formats
    print("Name Format Variations:")
    for i, fmt in enumerate(generator.variation_formats, 1):
        print(f"  {i:2d}. {fmt}")
    print()
    
    # Generate dataset
    dataset = generator.generate_complete_dataset(sentences_per_format=10000)
    
    # Save to file
    generator.save_dataset(dataset, "name_pii_dataset.json")
    
    # Save template version with {NAME} placeholders
    generator.save_template_dataset(dataset, "name_pii_templates.json")
    
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
        print(f"  Name: '{entity['value']}'")
        print(f"  Sentence: {sample['text']}")
        
        # Show template version
        template_text = sample['text'].replace(entity['value'], '{NAME}')
        print(f"  Template: {template_text}")
    print()


if __name__ == "__main__":
    main()
