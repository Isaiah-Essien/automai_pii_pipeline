#!/usr/bin/env python3
"""
Geographic Subdivision (Healthcare Facility Location) PII Generator
Generates healthcare facility locations with African emphasis.
Creating sentences with facility names, types, and departments in medical contexts.
"""

import json
import random
import os
from typing import List, Dict, Any

class LocationGenerator:
    def __init__(self):
        """Initialize location generator with components and schema."""
        self.output_dir = None  # Will be set via set_output_dir()
        self.load_schema()
        self.load_components()
        
    def set_output_dir(self, output_dir: str):
        """Set custom output directory for generated files."""
        self.output_dir = output_dir

    def load_schema(self):
        """Load location schema from pii_variation_schema.json."""
        schema_file = os.path.join(
            os.path.dirname(__file__),
            '../../pii_variation_schema.json'
        )
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        location_schema = schema['pii_types']['LOCATION']
        self.location_formats = location_schema['variation_formats']
        self.phi_label = location_schema['phi_label']
    
    def load_components(self):
        """Load location components from JSON file."""
        component_file = os.path.join(os.path.dirname(__file__), 'geo_sub_divs_components.json')
        with open(component_file, 'r') as f:
            components = json.load(f)
        
        self.facility_names = components.get('facility_names', [])
        self.facility_types = components.get('facility_types', [])
        self.departments = components.get('departments', [])
        
        # Rich sentence templates for location/geo subdivision
        self.location_templates = [
            # Basic facility mentions
            "Patient treated at {LOCATION}.",
            "Admitted to {LOCATION}.",
            "Discharged from {LOCATION}.",
            "Medical records from {LOCATION}.",
            "Referred to {LOCATION}.",
            "Consultation at {LOCATION}.",
            
            # Procedure and treatment
            "Surgery performed at {LOCATION}.",
            "Procedure scheduled at {LOCATION}.",
            "Treatment provided at {LOCATION}.",
            "Therapy sessions at {LOCATION}.",
            "Diagnostic testing at {LOCATION}.",
            "Lab work completed at {LOCATION}.",
            
            # Staff and providers
            "{NAME} transferred to {LOCATION}.",
            "{NAME} works at {LOCATION}.",
            "Dr. {NAME} practices at {LOCATION}.",
            "Nurse {NAME} assigned to {LOCATION}.",
            "Staff at {LOCATION} contacted.",
            "Provider affiliation: {LOCATION}.",
            
            # Facility and location details
            "Facility: {LOCATION}.",
            "Emergency at {LOCATION}.",
            "Urgent care at {LOCATION}.",
            "ICU department at {LOCATION}.",
            "Outpatient services at {LOCATION}.",
            "Hospital location: {LOCATION}.",
            
            # Administrative
            "Patient database updated at {LOCATION}.",
            "Medical records maintained at {LOCATION}.",
            "Insurance verified with {LOCATION}.",
            "Authorization obtained from {LOCATION}.",
            "Billing submitted to {LOCATION}.",
            "Account established at {LOCATION}.",
            
            # Appointments and scheduling
            "Appointment at {LOCATION} on {DATE}.",
            "Follow-up visit at {LOCATION}.",
            "Initial consultation at {LOCATION}.",
            "Scheduled for {LOCATION}.",
            "Appointment confirmed with {LOCATION}.",
            "Transfer arranged to {LOCATION}.",
            
            # Clinical coordination
            "Care coordinated with {LOCATION}.",
            "Referral sent to {LOCATION}.",
            "Results received from {LOCATION}.",
            "Communication with {LOCATION} staff.",
            "Case review at {LOCATION}.",
            "Interdepartmental coordination at {LOCATION}.",
            
            # Emergency and urgent
            "Emergency admission to {LOCATION}.",
            "Trauma case at {LOCATION}.",
            "Critical condition at {LOCATION}.",
            "Emergency room {LOCATION}.",
            "Acute care provided at {LOCATION}.",
            "Life-threatening case at {LOCATION}.",
            
            # Records and documentation
            "Records requested from {LOCATION}.",
            "Documentation from {LOCATION} received.",
            "File updated from {LOCATION}.",
            "Note from {LOCATION} physician.",
            "Report filed at {LOCATION}.",
            "History obtained from {LOCATION}.",
            
            # Specialty services
            "Specialty care at {LOCATION}.",
            "Rehabilitation services at {LOCATION}.",
            "Mental health services at {LOCATION}.",
            "Dental services at {LOCATION}.",
            "Pediatric care at {LOCATION}.",
            "Geriatric services at {LOCATION}.",
            
            # Follow-up and continuity
            "Continued care at {LOCATION}.",
            "Long-term care facility {LOCATION}.",
            "Discharge to {LOCATION}.",
            "Post-operative follow-up at {LOCATION}.",
            "Recovery facility {LOCATION}.",
            "Rehabilitation completed at {LOCATION}."
        ]
    
    def generate_location_components(self) -> Dict[str, str]:
        """Generate random location components."""
        return {
            'name': random.choice(self.facility_names),
            'type': random.choice(self.facility_types),
            'department': random.choice(self.departments)
        }
    
    def apply_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to location components."""
        try:
            return format_pattern.format(**components)
        except KeyError:
            return format_pattern
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all location format variations."""
        total_formats = len(self.location_formats)
        
        all_data = {
            "metadata": {
                "entity_type": "LOCATION",
                "phi_label": self.phi_label,
                "total_formats": total_formats,
                "sentences_per_format": sentences_per_format,
                "total_sentences": total_formats * sentences_per_format,
                "sentence_templates": len(self.location_templates),
                "facility_names": len(self.facility_names),
                "facility_types": len(self.facility_types),
                "departments": len(self.departments)
            },
            "formats": {}
        }
        
        current_id = 1
        
        print(f"\nGenerating {total_formats} location format variations × {sentences_per_format:,} sentences each")
        print(f"Total sentences to generate: {total_formats * sentences_per_format:,}\n")
        
        for format_idx, location_format in enumerate(self.location_formats, 1):
            print(f"[{format_idx}/{total_formats}] Generating location format: {location_format}")
            
            format_sentences = []
            
            for sentence_num in range(sentences_per_format):
                # Pick a random template for variety
                template = random.choice(self.location_templates)
                
                # Generate location components
                components = self.generate_location_components()
                location_value = self.apply_format(location_format, components)
                
                # Create sentence
                sentence = template.replace("{LOCATION}", location_value)
                
                # Handle {NAME} placeholder if present
                if "{NAME}" in sentence:
                    names = ["John Smith", "Mary Johnson", "Robert Williams", "Patricia Davis", 
                            "Michael Brown", "Linda Miller", "David Wilson", "Barbara Moore"]
                    sentence = sentence.replace("{NAME}", random.choice(names))
                
                # Handle {DATE} placeholder if present
                if "{DATE}" in sentence:
                    month = random.randint(1, 12)
                    day = random.randint(1, 28)
                    year = random.randint(2023, 2024)
                    sentence = sentence.replace("{DATE}", f"{month:02d}/{day:02d}/{year}")
                
                # Calculate character offsets
                start_pos = sentence.find(location_value)
                end_pos = start_pos + len(location_value)
                
                sentence_obj = {
                    "sentence_id": f"location_{current_id:08d}",
                    "sentence": sentence,
                    "entity": {
                        "start": start_pos,
                        "end": end_pos,
                        "label": self.phi_label,
                        "value": location_value
                    },
                    "template_idx": self.location_templates.index(template) + 1,
                    "template_pattern": template,
                    "format": location_format
                }
                
                format_sentences.append(sentence_obj)
                current_id += 1
            
            format_key = f"format_{format_idx:02d}"
            all_data["formats"][format_key] = {
                "pattern": location_format,
                "num_sentences": len(format_sentences),
                "sentences": format_sentences
            }
            
            print(f"     ✓ Generated {len(format_sentences):,} sentences (IDs: location_{current_id - len(format_sentences):08d} to location_{current_id - 1:08d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any]):
        """Save sentences dataset with metadata."""
        output_file = os.path.join(self.output_dir if self.output_dir else os.path.dirname(__file__), 'geo_sub_divs_dataset.json')
        print(f"\nSaving to {os.path.basename(output_file)}...")
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
        
        return output_file
    
    def save_template_dataset(self, data: Dict[str, Any]):
        """Save template dataset with {LOCATION} placeholders."""
        template_data = {
            "metadata": data["metadata"],
            "formats": {}
        }
        
        for format_key, format_data in data["formats"].items():
            template_data["formats"][format_key] = {
                "pattern": format_data["pattern"],
                "num_sentences": format_data["num_sentences"],
                "sentences": []
            }
            
            for sentence_obj in format_data["sentences"]:
                # Replace actual location with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entity"]["value"],
                    "{LOCATION}"
                )
                
                template_data["formats"][format_key]["sentences"].append({
                    "sentence_id": sentence_obj["sentence_id"],
                    "sentence": template_sentence,
                    "template_idx": sentence_obj["template_idx"],
                    "template_pattern": sentence_obj["template_pattern"]
                })
        
        output_file = os.path.join(self.output_dir if self.output_dir else os.path.dirname(__file__), 'geo_sub_divs_templates.json')
        print("Creating template dataset with {LOCATION} placeholders...")
        print(f"Saving templates to {os.path.basename(output_file)}...")
        
        with open(output_file, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
        
        return output_file
    
    def run(self, sentences_per_format: int = 10000):
        """Run the location generator."""
        print("\n" + "=" * 70)
        print("Geographic Subdivision (Location) PII Generator - Enhanced")
        print("=" * 70)
        
        print(f"\nConfiguration:")
        print(f"- Location formats: {len(self.location_formats)}")
        print(f"- Sentences per format: {sentences_per_format:,}")
        print(f"- Sentence templates: {len(self.location_templates)}")
        print(f"- Facility names: {len(self.facility_names)}")
        print(f"- Facility types: {len(self.facility_types)}")
        print(f"- Departments: {len(self.departments)}")
        print(f"- Total output: {len(self.location_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save templates
        self.save_template_dataset(data)
        
        print("\n" + "=" * 70)
        print("✓ Location PII generation complete!")
        print(f"  Generated {len(self.location_formats) * sentences_per_format:,} total sentences")
        print(f"  Across {len(self.location_formats)} format variations × {sentences_per_format:,} sentences each")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    generator = LocationGenerator()
    generator.run(sentences_per_format=10000)
