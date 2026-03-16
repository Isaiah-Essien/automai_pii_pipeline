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
        self.location_templates = location_schema['sentence_templates']
        self.phi_label = location_schema['phi_label']
    
    def load_components(self):
        """Load location components from JSON file."""
        component_file = os.path.join(os.path.dirname(__file__), 'geo_sub_divs_components.json')
        with open(component_file, 'r') as f:
            components = json.load(f)
        
        self.facility_names = components.get('facility_names', [])
        self.facility_types = components.get('facility_types', [])
        self.departments = components.get('departments', [])
    
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
    
    def generate_sentences(self, num_sentences: int = 30000) -> List[Dict[str, Any]]:
        """Generate location sentences with entity annotations."""
        sentences = []
        sentences_per_format = num_sentences // len(self.location_formats)
        
        sentence_id = 0
        for format_idx, location_format in enumerate(self.location_formats, 1):
            for _ in range(sentences_per_format):
                sentence_id += 1
                
                # Generate location value
                components = self.generate_location_components()
                location_value = self.apply_format(location_format, components)
                
                # Choose random template
                template = random.choice(self.location_templates)
                
                # Generate sentence with location
                sentence = template.replace('{LOCATION}', location_value)
                
                # Calculate entity position
                start_pos = sentence.find(location_value)
                end_pos = start_pos + len(location_value) if start_pos != -1 else -1
                
                # Create entity annotation
                entity_data = {
                    "sentence_id": f"location_{sentence_id:06d}",
                    "sentence": sentence,
                    "entity": {
                        "start": start_pos,
                        "end": end_pos,
                        "label": self.phi_label,
                        "value": location_value
                    },
                    "format": format_idx,
                    "format_pattern": location_format
                }
                
                sentences.append(entity_data)
        
        return sentences
    
    def save_dataset(self, sentences: List[Dict[str, Any]]):
        """Save sentences dataset with metadata."""
        output_file = 'geo_sub_divs_dataset.json'
        if self.output_dir:
            output_file = os.path.join(self.output_dir, output_file)
        
        metadata = {
            "metadata": {
                "total_formats": len(self.location_formats),
                "sentences_per_format": len(sentences) // len(self.location_formats),
                "total_sentences": len(sentences),
                "pii_type": "LOCATION",
                "phi_label": self.phi_label
            },
            "data": sentences
        }
        
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return output_file
    
    def save_template_dataset(self):
        """Load and save the existing template dataset."""
        # Read existing templates
        template_file = os.path.join(os.path.dirname(__file__), 'geo_sub_divs_templates.json')
        
        output_file = 'geo_sub_divs_templates.json'
        if self.output_dir:
            output_file = os.path.join(self.output_dir, output_file)
        
        # Copy template file to output location
        if os.path.exists(template_file) and self.output_dir:
            with open(template_file, 'r') as f:
                templates = json.load(f)
            with open(output_file, 'w') as f:
                json.dump(templates, f, indent=2)
        
        return output_file
    
    def run(self, num_sentences: int = 30000):
        """Run the location generator."""
        print(f"Generating {num_sentences} location sentences...")
        
        # Generate sentences
        sentences = self.generate_sentences(num_sentences)
        
        # Save dataset
        dataset_file = self.save_dataset(sentences)
        print(f"✓ Saved dataset: {dataset_file}")
        
        # Save templates
        template_file = self.save_template_dataset()
        print(f"✓ Saved templates: {template_file}")
        
        return {
            'dataset_file': dataset_file,
            'template_file': template_file,
            'total_sentences': len(sentences)
        }


if __name__ == "__main__":
    generator = LocationGenerator()
    result = generator.run(num_sentences=30000)
    print(f"\nGeneration complete!")
    print(f"  Total sentences: {result['total_sentences']}")
