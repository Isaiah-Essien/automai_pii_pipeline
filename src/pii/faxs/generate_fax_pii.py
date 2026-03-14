#!/usr/bin/env python3
"""
FAX Number PII Generator
Generates FAX numbers in multiple format variations for healthcare contexts.
Following schema specifications with formats similar to PHONE but fax-specific.
"""

import json
import random
import os
from typing import List, Dict, Any

class FAXGenerator:
    def __init__(self):
        """Initialize FAX number generator with components and schema."""

        self.output_dir = None  # Will be set via set_output_dir()
        self.load_schema()
        self.load_components()
        
    def set_output_dir(self, output_dir: str):
        """Set custom output directory for generated files."""
        self.output_dir = output_dir

    def load_schema(self):
        """Load FAX schema from pii_variation_schema.json."""
        schema_file = os.path.join(
            os.path.dirname(__file__),
            '../../pii_variation_schema.json'
        )
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        fax_schema = schema['pii_types']['FAX']
        self.fax_formats = fax_schema['variation_formats']
        self.fax_templates = fax_schema['sentence_templates']
        self.phi_label = fax_schema['phi_label']
    
    def load_components(self):
        """Load FAX components from JSON file."""
        component_file = os.path.join(os.path.dirname(__file__), 'fax_components.json')
        with open(component_file, 'r') as f:
            components = json.load(f)
        
        self.fax_prefixes = components.get('fax_prefixes', [])
        self.area_codes = components.get('area_codes', [])
        self.country_codes = components.get('country_codes', [])
        self.exchange_codes = components.get('exchange_codes', [])
    
    def generate_fax_components(self) -> Dict[str, str]:
        """Generate random FAX number components."""
        return {
            "country_code": random.choice(self.country_codes),
            "area_code": random.choice(self.area_codes),
            "exchange": random.choice(self.exchange_codes),
            "number": str(random.randint(1000, 9999)).zfill(4),
            "prefix": random.choice(self.fax_prefixes)
        }
    
    def apply_format(self, pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to components."""
        return pattern.format(**components)
    
    def create_sentence(self, fax_value: str, template: str) -> Dict[str, Any]:
        """Create a sentence with FAX entity annotation."""
        sentence = template.replace("{FAX}", fax_value)
        start = sentence.find(fax_value)
        end = start + len(fax_value)
        
        return {
            "start": start,
            "end": end,
            "label": "FAX",
            "value": fax_value
        }
    
    def generate_dataset_for_format(self, format_index: int, format_pattern: str, 
                                    sentences_per_format: int = 5000, 
                                    start_id: int = 1) -> tuple:
        """Generate dataset for a specific FAX format."""
        data = []
        current_id = start_id
        
        for i in range(sentences_per_format):
            components = self.generate_fax_components()
            fax_value = self.apply_format(format_pattern, components)
            template = random.choice(self.fax_templates)
            sentence = template.replace("{FAX}", fax_value)
            
            entity = self.create_sentence(fax_value, template)
            
            record = {
                "sentence_id": f"fax_{current_id:06d}",
                "sentence": sentence,
                "entity": entity,
                "format": format_index + 1,
                "format_pattern": format_pattern
            }
            data.append(record)
            current_id += 1
        
        return data, current_id
    
    def generate_complete_dataset(self, sentences_per_format: int = 5000) -> List[Dict[str, Any]]:
        """Generate complete dataset across all FAX formats."""
        all_data = []
        current_id = 1
        
        print(f"\nGenerating FAX formats:")
        for format_index, format_pattern in enumerate(self.fax_formats, 1):
            print(f"[{format_index}/{len(self.fax_formats)}] Generating FAX format: {format_pattern}")
            format_data, current_id = self.generate_dataset_for_format(
                format_index - 1, format_pattern, sentences_per_format, current_id
            )
            print(f"       ✓ Generated {len(format_data)} sentences (IDs: fax_{current_id - len(format_data):06d} to fax_{current_id - 1:06d})")
            all_data.extend(format_data)
        
        return all_data
    
    def save_dataset(self, data: List[Dict[str, Any]]):
        """Save dataset to JSON file with metadata."""
        output_file = os.path.join(self.output_dir if self.output_dir else os.path.dirname(__file__), 'fax_pii_dataset.json')
        print(f"\nSaving to {os.path.basename(output_file)}...")
        
        metadata = {
            "metadata": {
                "total_formats": len(self.fax_formats),
                "sentences_per_format": len(data) // len(self.fax_formats),
                "total_sentences": len(data),
                "templates_count": len(self.fax_templates)
            },
            "data": data
        }
        
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def save_template_dataset(self, data: List[Dict[str, Any]]):
        """Save template dataset with {FAX} placeholders and metadata."""
        template_data = []
        
        for record in data:
            sentence = record["sentence"]
            fax_value = record["entity"]["value"]
            sentence_with_placeholder = sentence.replace(fax_value, "{FAX}")
            
            template_record = {
                "sentence_id": record["sentence_id"],
                "sentence": sentence_with_placeholder,
                "entity": {
                    "start": record["entity"]["start"],
                    "end": record["entity"]["end"],
                    "label": record["entity"]["label"],
                    "value": "{FAX}"
                },
                "format": record["format"],
                "format_pattern": record["format_pattern"]
            }
            template_data.append(template_record)
        
        output_file = os.path.join(self.output_dir if self.output_dir else os.path.dirname(__file__), 'fax_pii_templates.json')
        print("Creating template dataset with {FAX} placeholders...")
        print(f"Saving templates to {os.path.basename(output_file)}...")
        
        metadata = {
            "metadata": {
                "total_formats": len(self.fax_formats),
                "sentences_per_format": len(template_data) // len(self.fax_formats),
                "total_sentences": len(template_data),
                "templates_count": len(self.fax_templates)
            },
            "data": template_data
        }
        
        with open(output_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 5000):
        """Generate and save both dataset and template files."""
        print("=" * 60)
        print("FAX Number PII Generator")
        print("=" * 60)
        print("\nConfiguration:")
        print(f"- FAX formats: {len(self.fax_formats)}")
        print(f"- Templates: {len(self.fax_templates)}")
        print(f"- Total output: {len(self.fax_formats) * sentences_per_format:,} sentences")
        
        data = self.generate_complete_dataset(sentences_per_format)
        self.save_dataset(data)
        self.save_template_dataset(data)
        
        print("\n" + "=" * 60)
        print("✓ FAX Number PII generation complete!")
        print("=" * 60)


if __name__ == "__main__":
    generator = FAXGenerator()
    generator.run(sentences_per_format=5000)
