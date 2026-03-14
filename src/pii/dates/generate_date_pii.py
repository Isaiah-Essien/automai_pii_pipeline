#!/usr/bin/env python3
"""
Date PII Generator
==================

Generates 10,000 sentences for each DATE variation format.
Total output: 12 formats × 10,000 sentences = 120,000 sentences

Features:
- Multiple date formats (DD/MM/YYYY, MM/DD/YYYY, ISO 8601, text formats, etc.)
- Realistic medical/healthcare context sentences
- Date ranges covering 50+ years (1950-2026)
- Entity annotations with character offsets

Usage:
    python generate_date_pii.py
    
Output:
    date_pii_dataset.json - Complete dataset with entities
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class DatePIIGenerator:
    """Generate date PII variations with sentences."""
    
    def __init__(self):
        """Initialize date generator with formats and templates."""
        
        # Date variation formats - from pii_variation_schema.json
        self.variation_formats = [
            "{day}/{month}/{year}",           # 15/5/1990
            "{day}-{month}-{year}",           # 15-5-1990
            "{month}/{day}/{year}",           # 5/15/1990
            "{month}-{day}-{year}",           # 5-15-1990
            "{day} {month_name} {year}",      # 15 May 1990
            "{day} {month_abbr} {year}",      # 15 May 1990 (abbreviated)
            "{month_name} {day}, {year}",     # May 15, 1990
            "{day}.{month}.{year}",           # 15.5.1990
            "{year}-{month}-{day}",           # 1990-5-15 (ISO 8601 style)
            "{day_name}",                     # Tuesday
            "{day_name}, {day} {month_name} {year}",  # Tuesday, 15 May 1990
        ]
        
        self.month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        self.month_abbr = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        
        self.day_names = [
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        ]
        
        self.phi_label = "DATE"
        
        # Sentence templates for medical/healthcare context
        self.sentence_templates = [
            "Patient's date of birth: {DATE}.",
            "Date of admission: {DATE}.",
            "Date of discharge: {DATE}.",
            "Appointment scheduled for {DATE}.",
            "Appointment completed on {DATE}.",
            "Date of surgery: {DATE}.",
            "Date of lab test: {DATE}.",
            "Medication started on {DATE}.",
            "Follow-up scheduled for {DATE}.",
            "Patient last seen on {DATE}.",
            "Referral date: {DATE}.",
            "Consultation date: {DATE}.",
            "Diagnosis date: {DATE}.",
            "Date of injury: {DATE}.",
            "Date of vaccination: {DATE}.",
            "Immunization administered on {DATE}.",
            "Physical examination on {DATE}.",
            "Lab results from {DATE} received.",
            "Chart review from {DATE} completed.",
            "Medical record from {DATE} updated.",
            "Insurance verification as of {DATE}.",
            "Pre-operative evaluation on {DATE}.",
            "Post-operative follow-up on {DATE}.",
            "Hospital admission date: {DATE}.",
            "Clinical trial enrollment date: {DATE}.",
            "Start date of treatment: {DATE}.",
            "End date of treatment: {DATE}.",
            "Rehabilitation started on {DATE}.",
            "Therapy session on {DATE}.",
            "Patient education provided on {DATE}.",
            "Screening test completed on {DATE}.",
            "Annual physical scheduled for {DATE}.",
            "Return to work date: {DATE}.",
            "Sick leave from {DATE}.",
            "Medical leave until {DATE}.",
            "Disability evaluation date: {DATE}.",
            "Workers compensation claim date: {DATE}.",
            "Accident occurred on {DATE}.",
            "Incident reported on {DATE}.",
            "Event date documented as {DATE}.",
            "Date of service: {DATE}.",
            "Billing date: {DATE}.",
            "Invoice date: {DATE}.",
            "Date of payment: {DATE}.",
            "Last payment date: {DATE}.",
            "Expiration date: {DATE}.",
            "Renewal date: {DATE}.",
            "License expiration: {DATE}.",
            "Certification valid until {DATE}.",
            "Credential renewal date: {DATE}.",
            "Background check completed on {DATE}.",
            "Drug screening on {DATE}.",
            "Health screening on {DATE}.",
            "Staff meeting held on {DATE}.",
            "Training session on {DATE}.",
            "Continuing education on {DATE}.",
            "Competency assessment on {DATE}.",
            "Performance review on {DATE}.",
            "Orientation completed on {DATE}.",
            "Hire date: {DATE}.",
            "Resignation date: {DATE}.",
            "Termination date: {DATE}.",
            "Retirement date: {DATE}.",
            "On-call schedule from {DATE}.",
            "Shift assignment starting {DATE}.",
            "Rotation begins on {DATE}.",
            "Coverage from {DATE} to {DATE}.",
            "Deadline: {DATE}.",
            "Target date: {DATE}.",
            "Implementation date: {DATE}.",
            "Go-live date: {DATE}.",
            "Launch date: {DATE}.",
            "Release date: {DATE}.",
            "Effective date: {DATE}.",
            "Policy date: {DATE}.",
            "Compliance deadline: {DATE}.",
            "Audit date: {DATE}.",
            "Quality review on {DATE}.",
            "Inspection date: {DATE}.",
            "Accreditation renewal: {DATE}.",
            "Waiver effective {DATE}.",
            "Exception approval date: {DATE}.",
            "Protocol approved on {DATE}.",
            "Ethics approval date: {DATE}.",
            "IRB approval date: {DATE}.",
            "Research study start: {DATE}.",
            "Data collection from {DATE}.",
            "Analysis completed on {DATE}.",
            "Publication date: {DATE}.",
            "Presentation date: {DATE}.",
            "Conference attendance: {DATE}.",
            "Journal club meeting: {DATE}.",
            "Grand rounds: {DATE}.",
            "Case conference: {DATE}.",
            "Team meeting scheduled for {DATE}.",
            "Department meeting on {DATE}.",
            "Administrative review on {DATE}.",
            "Executive meeting: {DATE}.",
            "Board meeting: {DATE}.",
            "Stakeholder update: {DATE}.",
            "Community meeting: {DATE}.",
            "Patient advisory meeting: {DATE}.",
            "Family meeting scheduled: {DATE}.",
            "Discharge planning meeting: {DATE}.",
            "Multidisciplinary team meeting: {DATE}.",
            "Patient follow-up call: {DATE}.",
            "Home visit scheduled: {DATE}.",
            "Telehealth appointment: {DATE}.",
            "Virtual consultation: {DATE}.",
            "Phone call documented: {DATE}.",
            "Email correspondence: {DATE}.",
            "Visit duration from {DATE}.",
            "Duration: {DATE}.",
            "Service end date: {DATE}.",
            "Last contact: {DATE}.",
        ]
    
    def generate_random_date(self, 
                            start_year: int = 1950, 
                            end_year: int = 2026) -> datetime:
        """Generate random date between start and end year."""
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        
        # Handle different month lengths
        if month in [1, 3, 5, 7, 8, 10, 12]:
            max_day = 31
        elif month in [4, 6, 9, 11]:
            max_day = 30
        else:  # February
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                max_day = 29
            else:
                max_day = 28
        
        day = random.randint(1, max_day)
        
        return datetime(year, month, day)
    
    def get_date_components(self, date_obj: datetime = None) -> Dict:
        """Get date components for formatting."""
        if date_obj is None:
            date_obj = self.generate_random_date()
        
        return {
            'day': date_obj.day,
            'month': date_obj.month,
            'year': date_obj.year,
            'month_name': self.month_names[date_obj.month - 1],
            'month_abbr': self.month_abbr[date_obj.month - 1],
            'day_name': self.day_names[date_obj.weekday()],
        }
    
    def apply_format(self, components: Dict, format_pattern: str) -> str:
        """Apply format pattern to date components."""
        try:
            return format_pattern.format(**components)
        except (KeyError, IndexError, ValueError):
            return None
    
    def create_sentence(self, date_value: str) -> Dict:
        """Create sentence with date PII and entity annotation."""
        
        # Select random sentence template
        template = random.choice(self.sentence_templates)
        
        # Replace {DATE} with actual date value
        sentence = template.replace('{DATE}', date_value)
        
        # Handle case where template has multiple {DATE} placeholders
        if '{DATE}' in sentence:
            # Generate another date for range scenarios
            another_date = self.apply_format(
                self.get_date_components(),
                random.choice(self.variation_formats[:5])
            )
            sentence = sentence.replace('{DATE}', another_date, 1)
        
        # Find first entity position
        start_pos = sentence.find(date_value)
        end_pos = start_pos + len(date_value)
        
        return {
            'text': sentence,
            'entities': [{
                'start': start_pos,
                'end': end_pos,
                'label': self.phi_label,
                'value': date_value
            }]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, 
                                    num_sentences: int = 10000,
                                    start_id: int = 1) -> List[Dict]:
        """Generate dataset for one date format variation."""
        
        dataset = []
        
        for i in range(num_sentences):
            # Generate date
            date_obj = self.generate_random_date()
            components = self.get_date_components(date_obj)
            
            # Apply format pattern
            date_value = self.apply_format(components, format_pattern)
            
            if date_value is None:
                continue
            
            # Create sentence
            sentence_data = self.create_sentence(date_value)
            
            # Add ID in format "date_000001"
            sentence_id = start_id + i
            sentence_data['id'] = f"date_{sentence_id:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict:
        """Generate complete dataset for all date format variations."""
        
        print(f"Generating {sentences_per_format} sentences for each of {len(self.variation_formats)} formats...")
        print("=" * 80)
        
        all_data = {
            'metadata': {
                'total_formats': len(self.variation_formats),
                'sentences_per_format': sentences_per_format,
                'total_sentences': len(self.variation_formats) * sentences_per_format,
                'phi_type': 'DATE',
                'phi_label': self.phi_label,
                'date_range': '1950-2026',
                'year_span': 76
            },
            'formats': {}
        }
        
        current_id = 1  # Track continuous ID across all formats
        
        for idx, format_pattern in enumerate(self.variation_formats, 1):
            print(f"[{idx:2d}/{len(self.variation_formats)}] Generating format: {format_pattern[:55]}")
            
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
            
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: date_{current_id-len(dataset):06d} to date_{current_id-1:06d})")
        
        print("=" * 80)
        print(f"✓ Total sentences generated: {all_data['metadata']['total_sentences']:,}")
        
        return all_data
    
    def save_dataset(self, dataset: Dict, output_path: str = "date_pii_dataset.json"):
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
    
    def save_template_dataset(self, dataset: Dict, output_path: str = "date_pii_templates.json"):
        """Save dataset with {DATE} placeholder instead of actual values."""
        print(f"\nCreating template dataset with {{DATE}} placeholders...")
        
        template_data = {
            'metadata': dataset['metadata'].copy(),
            'formats': {}
        }
        
        for format_key, format_data in dataset['formats'].items():
            template_sentences = []
            
            for sentence in format_data['sentences']:
                # Replace actual date value with {DATE} placeholder
                original_text = sentence['text']
                entity = sentence['entities'][0]
                date_value = entity['value']
                
                # Create template by replacing date value with {DATE}
                template_text = original_text.replace(date_value, '{DATE}')
                
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
    print("DATE PII DATASET GENERATOR")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = DatePIIGenerator()
    
    # Show configuration
    print("Configuration:")
    print(f"  - Date formats: {len(generator.variation_formats)}")
    print(f"  - Sentence templates: {len(generator.sentence_templates)}")
    print(f"  - Date range: 1950-2026 (76 years)")
    print(f"  - Sentences per format: 10,000")
    print(f"  - Total output: {len(generator.variation_formats) * 10000:,} sentences")
    print()
    
    # Show sample formats
    print("Date Format Variations:")
    for i, fmt in enumerate(generator.variation_formats, 1):
        print(f"  {i:2d}. {fmt}")
    print()
    
    # Generate dataset
    dataset = generator.generate_complete_dataset(sentences_per_format=10000)
    
    # Save to file
    generator.save_dataset(dataset, "date_pii_dataset.json")
    
    # Save template version with {DATE} placeholders
    generator.save_template_dataset(dataset, "date_pii_templates.json")
    
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
        print(f"  Date: '{entity['value']}'")
        print(f"  Sentence: {sample['text']}")
        
        # Show template version
        template_text = sample['text'].replace(entity['value'], '{DATE}')
        print(f"  Template: {template_text}")
    print()


if __name__ == "__main__":
    main()
