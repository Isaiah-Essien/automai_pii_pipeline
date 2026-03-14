#!/usr/bin/env python3
"""
Email PII Generator - African Names
====================================

Generates 10,000 sentences for each EMAIL variation format.
Total output: 6 formats × 10,000 sentences = 60,000 sentences

Features:
- African names from 15+ countries
- African healthcare and institutional email domains
- Commercial domains including @gmail.com
- Medical/healthcare context sentences
- Entity annotations with character offsets

Usage:
    python generate_email_pii.py
    
Output:
    email_pii_dataset.json - Complete dataset with entities
"""

import json
import random
from typing import List, Dict


class EmailPIIGenerator:
    """Generate email PII variations with sentences."""
    
    def __init__(self, 
                 names_path: str = "../names/african_names.json",
                 domains_path: str = "email_domains.json"):
        """Initialize with names and email domains."""
        
        # Load African names
        with open(names_path, 'r', encoding='utf-8') as f:
            self.names_data = json.load(f)
        
        # Load email domains
        with open(domains_path, 'r', encoding='utf-8') as f:
            self.domains_data = json.load(f)
        
        # Extract names
        self.first_names = []
        for region_data in self.names_data['first_names'].values():
            if isinstance(region_data, dict):
                for country_names in region_data.values():
                    self.first_names.extend(country_names)
            else:
                self.first_names.extend(region_data)
        
        self.last_names = []
        for region_data in self.names_data['last_names'].values():
            if isinstance(region_data, dict):
                for country_names in region_data.values():
                    self.last_names.extend(country_names)
            else:
                self.last_names.extend(region_data)
        
        # Collect all domains
        self.all_domains = (
            self.domains_data['healthcare_domains'] +
            self.domains_data['institutional_domains'] +
            self.domains_data['government_domains'] +
            self.domains_data['commercial_domains']
        )
        
        # Email variation formats
        self.variation_formats = [
            "{username}@{domain}",
            "{first_name}.{last_name}@{domain}",
            "{first_initial}{last_name}@{domain}",
            "{first_name}{last_initial}@{domain}",
            "{first_name}_{last_name}@{domain}",
            "{last_name}.{first_name}@{domain}"
        ]
        
        self.phi_label = "EMAIL"
        
        # Sentence templates for medical/healthcare context
        self.sentence_templates = [
            "Email results to {EMAIL}.",
            "{NAME}'s email is {EMAIL}.",
            "Send prescription to {EMAIL}.",
            "Patient portal login: {EMAIL}.",
            "Contact {NAME} at {EMAIL}.",
            "Billing inquiries: {EMAIL}.",
            "Lab reports sent to {EMAIL}.",
            "Patient email: {EMAIL}.",
            "For records, email {EMAIL}.",
            "{NAME} ({EMAIL}) requested appointment.",
            "Appointment confirmation sent to {EMAIL}.",
            "Medical records access: {EMAIL}.",
            "Telemedicine login: {EMAIL}.",
            "Patient {NAME} email: {EMAIL}.",
            "Referral letter to {EMAIL}.",
            "Insurance documentation to {EMAIL}.",
            "Doctor's office email: {EMAIL}.",
            "Hospital system: {EMAIL}.",
            "Clinic contact email: {EMAIL}.",
            "Pharmacy email: {EMAIL}.",
            "Lab facility: {EMAIL}.",
            "Radiology department: {EMAIL}.",
            "Physical therapy: {EMAIL}.",
            "Surgical center: {EMAIL}.",
            "Mental health services: {EMAIL}.",
            "Dental clinic: {EMAIL}.",
            "Vision center: {EMAIL}.",
            "Urgent care: {EMAIL}.",
            "Emergency department: {EMAIL}.",
            "ICU coordination: {EMAIL}.",
            "Patient advocate: {EMAIL}.",
            "Social work services: {EMAIL}.",
            "Nutritionist office: {EMAIL}.",
            "Speech therapy: {EMAIL}.",
            "Occupational therapy: {EMAIL}.",
            "Home health agency: {EMAIL}.",
            "Rehabilitation center: {EMAIL}.",
            "Hospice services: {EMAIL}.",
            "Medical device supplier: {EMAIL}.",
            "Prescription delivery: {EMAIL}.",
            "Medical records department: {EMAIL}.",
            "Billing department: {EMAIL}.",
            "Insurance verification: {EMAIL}.",
            "Patient education: {EMAIL}.",
            "Training materials sent to {EMAIL}.",
            "Compliance documentation: {EMAIL}.",
            "Quality assurance: {EMAIL}.",
            "Safety reporting: {EMAIL}.",
            "Incident investigation: {EMAIL}.",
            "Performance review: {EMAIL}.",
            "Staff development: {EMAIL}.",
            "Credentialing office: {EMAIL}.",
            "Human resources: {EMAIL}.",
            "Payroll department: {EMAIL}.",
            "Benefits administration: {EMAIL}.",
            "Office manager: {EMAIL}.",
            "Administrative assistant: {EMAIL}.",
            "{NAME}, RN email: {EMAIL}.",
            "{NAME}, MD email: {EMAIL}.",
            "{NAME}, PhD email: {EMAIL}.",
            "Department head: {EMAIL}.",
            "Clinical supervisor: {EMAIL}.",
            "Medical director: {EMAIL}.",
            "Chief nurse officer: {EMAIL}.",
            "Chief medical officer: {EMAIL}.",
            "Executive director: {EMAIL}.",
            "Board member: {EMAIL}.",
            "Research coordinator: {EMAIL}.",
            "Clinical trial: {EMAIL}.",
            "Data management: {EMAIL}.",
            "Statistics office: {EMAIL}.",
            "Publication team: {EMAIL}.",
            "Grant administration: {EMAIL}.",
            "Compliance officer: {EMAIL}.",
            "Privacy officer: {EMAIL}.",
            "Security team: {EMAIL}.",
            "IT support: {EMAIL}.",
            "Systems administrator: {EMAIL}.",
            "Database manager: {EMAIL}.",
            "EHR support: {EMAIL}.",
            "Help desk: {EMAIL}.",
            "Technical support: {EMAIL}.",
            "Customer service: {EMAIL}.",
            "Patient services: {EMAIL}.",
            "Appointment scheduling: {EMAIL}.",
            "Registration office: {EMAIL}.",
            "Health information: {EMAIL}.",
            "Medical coding: {EMAIL}.",
            "Clinical documentation: {EMAIL}.",
            "Care coordination: {EMAIL}.",
            "Case management: {EMAIL}.",
            "Discharge planning: {EMAIL}.",
            "Continuity of care: {EMAIL}.",
            "Quality improvement: {EMAIL}.",
            "Patient safety: {EMAIL}.",
            "Risk management: {EMAIL}.",
            "Legal department: {EMAIL}.",
            "Contracts office: {EMAIL}.",
            "Procurement: {EMAIL}.",
            "Supply chain: {EMAIL}.",
            "Logistics: {EMAIL}.",
            "Maintenance: {EMAIL}.",
            "Facilities management: {EMAIL}.",
            "Housekeeping: {EMAIL}.",
            "Environmental services: {EMAIL}.",
            "Infection prevention: {EMAIL}.",
            "Occupational health: {EMAIL}.",
            "Safety committee: {EMAIL}.",
            "Emergency preparedness: {EMAIL}.",
            "Crisis management: {EMAIL}.",
            "Public relations: {EMAIL}.",
            "Marketing department: {EMAIL}.",
            "Community outreach: {EMAIL}.",
            "Patient advocacy: {EMAIL}.",
            "Volunteer services: {EMAIL}.",
            "Donor relations: {EMAIL}.",
            "Fundraising: {EMAIL}.",
            "Development office: {EMAIL}.",
            "Alumni association: {EMAIL}.",
            "Medical school: {EMAIL}.",
            "Nursing school: {EMAIL}.",
            "Allied health programs: {EMAIL}.",
            "Residency program: {EMAIL}.",
            "Fellowship program: {EMAIL}.",
            "Continuing education: {EMAIL}.",
            "Professional development: {EMAIL}.",
            "Conference registration: {EMAIL}.",
            "Workshop coordination: {EMAIL}.",
            "Online portal: {EMAIL}.",
            "Patient app support: {EMAIL}.",
            "Mobile health: {EMAIL}.",
            "Telehealth platform: {EMAIL}.",
        ]
    
    def generate_email_components(self) -> Dict:
        """Generate random email components."""
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        domain = random.choice(self.all_domains)
        
        # Generate a simple username (could be any combination)
        username_options = [
            first_name.lower(),
            last_name.lower(),
            f"{first_name[0].lower()}{last_name.lower()}",
            f"{first_name.lower()}{last_name[0].lower()}",
            f"{first_name.lower().replace(' ', '')}{random.randint(1, 999)}",
        ]
        username = random.choice(username_options)
        
        return {
            'username': username,
            'first_name': first_name.lower(),
            'last_name': last_name.lower(),
            'first_initial': first_name[0].lower(),
            'last_initial': last_name[0].lower(),
            'domain': domain,
        }
    
    def apply_format(self, components: Dict, format_pattern: str) -> str:
        """Apply format pattern to email components."""
        try:
            return format_pattern.format(**components)
        except KeyError:
            return None
    
    def create_sentence(self, email_value: str) -> Dict:
        """Create sentence with email PII and entity annotation."""
        
        # Select random sentence template
        template = random.choice(self.sentence_templates)
        
        # Replace {EMAIL} with actual email value
        sentence = template.replace('{EMAIL}', email_value)
        
        # Replace {NAME} if present with a random African name
        if '{NAME}' in sentence:
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            full_name = f"{first_name} {last_name}"
            sentence = sentence.replace('{NAME}', full_name)
        
        # Find entity position
        start_pos = sentence.find(email_value)
        end_pos = start_pos + len(email_value)
        
        return {
            'text': sentence,
            'entities': [{
                'start': start_pos,
                'end': end_pos,
                'label': self.phi_label,
                'value': email_value
            }]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, 
                                    num_sentences: int = 10000,
                                    start_id: int = 1) -> List[Dict]:
        """Generate dataset for one email format variation."""
        
        dataset = []
        
        for i in range(num_sentences):
            # Generate email components
            components = self.generate_email_components()
            
            # Apply format pattern
            email_value = self.apply_format(components, format_pattern)
            
            if email_value is None:
                continue
            
            # Create sentence
            sentence_data = self.create_sentence(email_value)
            
            # Add ID in format "email_000001"
            sentence_id = start_id + i
            sentence_data['id'] = f"email_{sentence_id:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict:
        """Generate complete dataset for all email format variations."""
        
        print(f"Generating {sentences_per_format} sentences for each of {len(self.variation_formats)} formats...")
        print("=" * 80)
        
        all_data = {
            'metadata': {
                'total_formats': len(self.variation_formats),
                'sentences_per_format': sentences_per_format,
                'total_sentences': len(self.variation_formats) * sentences_per_format,
                'phi_type': 'EMAIL',
                'phi_label': self.phi_label,
                'total_domains': len(self.all_domains),
                'african_countries': 15,
                'unique_first_names': len(set(self.first_names)),
                'unique_last_names': len(set(self.last_names))
            },
            'formats': {}
        }
        
        current_id = 1  # Track continuous ID across all formats
        
        for idx, format_pattern in enumerate(self.variation_formats, 1):
            print(f"[{idx}/{len(self.variation_formats)}] Generating format: {format_pattern[:50]}")
            
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
            
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: email_{current_id-len(dataset):06d} to email_{current_id-1:06d})")
        
        print("=" * 80)
        print(f"✓ Total sentences generated: {all_data['metadata']['total_sentences']:,}")
        
        return all_data
    
    def save_dataset(self, dataset: Dict, output_path: str = "email_pii_dataset.json"):
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
    
    def save_template_dataset(self, dataset: Dict, output_path: str = "email_pii_templates.json"):
        """Save dataset with {EMAIL} placeholder instead of actual values."""
        print(f"\nCreating template dataset with {{EMAIL}} placeholders...")
        
        template_data = {
            'metadata': dataset['metadata'].copy(),
            'formats': {}
        }
        
        for format_key, format_data in dataset['formats'].items():
            template_sentences = []
            
            for sentence in format_data['sentences']:
                # Replace actual email value with {EMAIL} placeholder
                original_text = sentence['text']
                entity = sentence['entities'][0]
                email_value = entity['value']
                
                # Create template by replacing email value with {EMAIL}
                template_text = original_text.replace(email_value, '{EMAIL}')
                
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
    print("EMAIL PII DATASET GENERATOR - AFRICAN NAMES & DOMAINS")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = EmailPIIGenerator()
    
    # Show configuration
    print("Configuration:")
    print(f"  - Email formats: {len(generator.variation_formats)}")
    print(f"  - Sentence templates: {len(generator.sentence_templates)}")
    print(f"  - Email domains: {len(generator.all_domains)}")
    print(f"  - Unique first names: {len(set(generator.first_names))}")
    print(f"  - Unique last names: {len(set(generator.last_names))}")
    print(f"  - Sentences per format: 10,000")
    print(f"  - Total output: {len(generator.variation_formats) * 10000:,} sentences")
    print()
    
    # Show sample formats
    print("Email Format Variations:")
    for i, fmt in enumerate(generator.variation_formats, 1):
        print(f"  {i}. {fmt}")
    print()
    
    # Show sample domains
    print("Sample Email Domains (includes @gmail.com and African healthcare domains):")
    sample_domains = random.sample(generator.all_domains, min(15, len(generator.all_domains)))
    for domain in sample_domains:
        print(f"  - {domain}")
    print()
    
    # Generate dataset
    dataset = generator.generate_complete_dataset(sentences_per_format=10000)
    
    # Save to file
    generator.save_dataset(dataset, "email_pii_dataset.json")
    
    # Save template version with {EMAIL} placeholders
    generator.save_template_dataset(dataset, "email_pii_templates.json")
    
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
        print(f"  Email: '{entity['value']}'")
        print(f"  Sentence: {sample['text']}")
        
        # Show template version
        template_text = sample['text'].replace(entity['value'], '{EMAIL}')
        print(f"  Template: {template_text}")
    print()


if __name__ == "__main__":
    main()
