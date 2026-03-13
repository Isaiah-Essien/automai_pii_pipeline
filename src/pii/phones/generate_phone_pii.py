#!/usr/bin/env python3
"""
Phone PII Generator
==================

Generates 10,000 sentences for each PHONE variation format.
Total output: 8 formats × 10,000 sentences = 80,000 sentences

Usage:
    python generate_phone_pii.py
    
Output:
    phone_pii_dataset.json - Complete dataset with entities
"""

import json
import random
from typing import List, Dict, Tuple


class PhonePIIGenerator:
    """Generate phone PII variations with sentences."""
    
    def __init__(self, schema_path: str = "pii_variation_schema.json"):
        """Initialize with schema file."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            self.schema = json.load(f)
        
        self.phone_config = self.schema['pii_types']['PHONE']
        self.variation_formats = self.phone_config['variation_formats']
        self.sentence_templates = self.phone_config['sentence_templates']
        self.phi_label = self.phone_config['phi_label']
        
        # Sample data for names (used in templates)
        self.first_names = [
            'John', 'Mary', 'James', 'Sarah', 'Michael', 'Jennifer', 'David', 'Linda',
            'Amara', 'Kwame', 'Chinwe', 'Tendai', 'Fatima', 'Ahmed', 'Kamau', 'Wanjiru',
            'Thabo', 'Aminata', 'Abebe', 'Khadija', 'Yusuf', 'Aisha', 'Kofi', 'Ama',
            'Dele', 'Ngozi', 'Sipho', 'Nomsa', 'Omar', 'Zainab', 'Idris', 'Amina'
        ]
        
        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
            'Okonkwo', 'Mensah', 'Mwangi', 'Nkosi', 'Diallo', 'Moyo', 'Hassan',
            'Tesfaye', 'Kamara', 'Banda', 'Okeke', 'Afolayan', 'Mutombo', 'Osei'
        ]
        
        # Country codes for diversity (focusing on African countries)
        self.country_codes = [
            '1',    # USA/Canada
            '27',   # South Africa
            '233',  # Ghana
            '234',  # Nigeria
            '254',  # Kenya
            '255',  # Tanzania
            '256',  # Uganda
            '260',  # Zambia
            '263',  # Zimbabwe
            '267',  # Botswana
            '251',  # Ethiopia
            '252',  # Somalia
            '221',  # Senegal
            '225',  # Ivory Coast
            '212',  # Morocco
            '216',  # Tunisia
            '20',   # Egypt
        ]
    
    def generate_phone_number(self, country_code: str = None) -> Dict:
        """Generate random phone number components."""
        return {
            'country_code': country_code or random.choice(self.country_codes),
            'area_code': str(random.randint(200, 999)),
            'exchange': str(random.randint(200, 999)),
            'number': str(random.randint(1000, 9999))
        }
    
    def format_phone(self, components: Dict, format_pattern: str) -> str:
        """Format phone number using pattern."""
        return format_pattern.format(**components)
    
    def generate_name(self) -> str:
        """Generate random full name."""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        return f"{first} {last}"
    
    def create_sentence(self, phone_value: str, template: str = None) -> Dict:
        """Create sentence with phone PII and entity annotation (phone only, no names)."""
        
        # Full meaningful sentences with ONLY phone - no names
        meaningful_templates = [
            "The patient's phone number is {PHONE}.",
            "Please call {PHONE} for appointment scheduling.",
            "Emergency contact number: {PHONE}.",
            "The clinic can be reached at {PHONE}.",
            "For billing inquiries, please dial {PHONE}.",
            "The pharmacy fax number is {PHONE}.",
            "Patient contact number on file: {PHONE}.",
            "The hospital's main line is {PHONE}.",
            "Lab results can be requested by calling {PHONE}.",
            "The medical records department number is {PHONE}.",
            "To schedule a follow-up appointment, call {PHONE}.",
            "The nurse station can be contacted at {PHONE}.",
            "For prescription refills, please call {PHONE}.",
            "The doctor on call can be reached at {PHONE}.",
            "Reception desk phone number: {PHONE}.",
            "The referral coordinator's number is {PHONE}.",
            "To verify insurance, please call {PHONE}.",
            "The patient portal support line is {PHONE}.",
            "Radiology scheduling phone: {PHONE}.",
            "The cardiology department can be reached at {PHONE}.",
            "For test results, call the lab at {PHONE}.",
            "The outpatient surgery center number is {PHONE}.",
            "Physical therapy appointments: {PHONE}.",
            "The pediatrics clinic phone number is {PHONE}.",
            "For urgent matters, please contact {PHONE}.",
            "The patient's preferred contact number is {PHONE}.",
            "Home health services can be reached at {PHONE}.",
            "The oncology department's direct line is {PHONE}.",
            "To speak with a nurse, dial {PHONE}.",
            "The facility's 24-hour hotline is {PHONE}.",
            "Billing department contact: {PHONE}.",
            "The patient requested updates be sent to {PHONE}.",
            "For appointment changes or cancellations, call {PHONE}.",
            "The primary care clinic can be reached at {PHONE}.",
            "Patient transportation services: {PHONE}.",
            "The imaging center's phone number is {PHONE}.",
            "For same-day appointments, call {PHONE}.",
            "The patient advocate can be reached at {PHONE}.",
            "Medical equipment inquiries: {PHONE}.",
            "The surgical team contact number is {PHONE}.",
            "After-hours emergency line: {PHONE}.",
            "The maternity ward phone number is {PHONE}.",
            "Patient discharge coordinator: {PHONE}.",
            "The internal medicine department can be reached at {PHONE}.",
            "For referral authorizations, call {PHONE}.",
            "The intensive care unit contact number is {PHONE}.",
            "Registration desk phone: {PHONE}.",
            "The patient's emergency contact is {PHONE}.",
            "For medication questions, call the pharmacy at {PHONE}.",
            "The specialist's office number is {PHONE}."
        ]
        
        # Select template (use provided or random)
        if template is None:
            template = random.choice(meaningful_templates)
        
        # Replace {PHONE} with actual phone value
        sentence = template.replace('{PHONE}', phone_value)
        
        # Find entity position
        start_pos = sentence.find(phone_value)
        end_pos = start_pos + len(phone_value)
        
        return {
            'text': sentence,
            'entities': [{
                'start': start_pos,
                'end': end_pos,
                'label': self.phi_label,
                'value': phone_value
            }]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, 
                                    num_sentences: int = 10000,
                                    start_id: int = 1) -> List[Dict]:
        """Generate dataset for one phone format variation."""
        
        dataset = []
        
        for i in range(num_sentences):
            # Generate phone components
            components = self.generate_phone_number()
            
            # Format phone number
            phone_value = self.format_phone(components, format_pattern)
            
            # Create sentence
            sentence_data = self.create_sentence(phone_value)
            
            # Add ID in format "phone_000001"
            sentence_id = start_id + i
            sentence_data['id'] = f"phone_{sentence_id:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict:
        """Generate complete dataset for all phone format variations."""
        
        print(f"Generating {sentences_per_format} sentences for each of {len(self.variation_formats)} formats...")
        print("=" * 80)
        
        all_data = {
            'metadata': {
                'total_formats': len(self.variation_formats),
                'sentences_per_format': sentences_per_format,
                'total_sentences': len(self.variation_formats) * sentences_per_format,
                'phi_type': 'PHONE',
                'phi_label': self.phi_label
            },
            'formats': {}
        }
        
        current_id = 1  # Track continuous ID across all formats
        
        for idx, format_pattern in enumerate(self.variation_formats, 1):
            print(f"[{idx}/{len(self.variation_formats)}] Generating format: {format_pattern[:50]}...")
            
            dataset = self.generate_dataset_for_format(
                format_pattern, 
                sentences_per_format,
                start_id=current_id
            )
            
            # Store by format pattern
            format_key = f"format_{idx}"
            all_data['formats'][format_key] = {
                'pattern': format_pattern,
                'num_sentences': len(dataset),
                'sentences': dataset
            }
            
            # Update ID counter
            current_id += len(dataset)
            
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: phone_{current_id-len(dataset):06d} to phone_{current_id-1:06d})")
        
        print("=" * 80)
        print(f"✓ Total sentences generated: {all_data['metadata']['total_sentences']}")
        
        return all_data
    
    def save_dataset(self, dataset: Dict, output_path: str = "phone_pii_dataset.json"):
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
    
    def save_template_dataset(self, dataset: Dict, output_path: str = "phone_pii_templates.json"):
        """Save dataset with {PHONE} placeholder instead of actual values."""
        print(f"\nCreating template dataset with {{PHONE}} placeholders...")
        
        template_data = {
            'metadata': dataset['metadata'].copy(),
            'formats': {}
        }
        
        for format_key, format_data in dataset['formats'].items():
            template_sentences = []
            
            for sentence in format_data['sentences']:
                # Replace actual phone value with {PHONE} placeholder
                original_text = sentence['text']
                entity = sentence['entities'][0]
                phone_value = entity['value']
                
                # Create template by replacing phone value with {PHONE}
                template_text = original_text.replace(phone_value, '{PHONE}')
                
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
    print("PHONE PII DATASET GENERATOR")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = PhonePIIGenerator()
    
    # Show configuration
    print("Configuration:")
    print(f"  - Phone formats: {len(generator.variation_formats)}")
    print(f"  - Sentence templates: {len(generator.sentence_templates)}")
    print(f"  - Sentences per format: 10,000")
    print(f"  - Total output: {len(generator.variation_formats) * 10000:,} sentences")
    print()
    
    # Show sample formats
    print("Phone Format Variations:")
    for i, fmt in enumerate(generator.variation_formats, 1):
        print(f"  {i}. {fmt}")
    print()
    
    # Generate dataset
    dataset = generator.generate_complete_dataset(sentences_per_format=10000)
    
    # Save to file
    generator.save_dataset(dataset, "phone_pii_dataset.json")
    
    # Save template version with {PHONE} placeholders
    generator.save_template_dataset(dataset, "phone_pii_templates.json")
    
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
        print(f"  With value: {sample['text']}")
        entity = sample['entities'][0]
        print(f"  Phone: '{entity['value']}' [{entity['start']}:{entity['end']}]")
        
        # Show template version
        template_text = sample['text'].replace(entity['value'], '{PHONE}')
        print(f"  Template:   {template_text}")
    print()


if __name__ == "__main__":
    main()
