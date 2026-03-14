import json
import random
import os
from typing import List, Dict, Any

class AddressGenerator:
    """Generate physical address PII with realistic medical context sentences."""
    
    def __init__(self):
        self.variation_formats = [
            "{street_number} {street_name} {street_type}",
            "{street_number} {street_name} {street_type}, {unit_type} {unit_number}",
            "{street_number} {street_name} {street_type}, {city}",
            "{unit_type} {unit_number}, {street_number} {street_name} {street_type}",
            "{street_name} {street_type} {street_number}",
            "{street_number} {street_name}",
            "No. {street_number} {street_name} {street_type}"
        ]
        
        self.sentence_templates = [
            "Patient resides at {ADDRESS}.",
            "{NAME} lives at {ADDRESS}.",
            "Home address: {ADDRESS}.",
            "The patient was transported from {ADDRESS}.",
            "Incident occurred at {ADDRESS}.",
            "Mail prescription to {ADDRESS}.",
            "{NAME} moved to {ADDRESS} in {DATE}.",
            "Previous address: {ADDRESS}.",
            "Contact {NAME} at {ADDRESS} or {PHONE}.",
            "Emergency services responded to {ADDRESS}."
        ]
        
        # Load address data
        self.load_address_data()
    
    def load_address_data(self):
        """Load address components from JSON file."""
        try:
            with open('african_addresses.json', 'r') as f:
                data = json.load(f)
                self.street_names = data['street_names']
                self.street_types = data['street_types']
                self.unit_types = data['unit_types']
                
                # Combine all African cities
                all_cities = (
                    data['cities_west_africa'] +
                    data['cities_east_africa'] +
                    data['cities_southern_africa'] +
                    data['cities_central_africa']
                )
                self.cities = all_cities
        except FileNotFoundError:
            print("Error: african_addresses.json not found!")
            raise
    
    def generate_address_components(self) -> Dict[str, str]:
        """Generate random address components."""
        return {
            "street_number": str(random.randint(1, 9999)),
            "street_name": random.choice(self.street_names),
            "street_type": random.choice(self.street_types),
            "unit_type": random.choice(self.unit_types),
            "unit_number": str(random.randint(1, 500)),
            "city": random.choice(self.cities)
        }
    
    def apply_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to address components."""
        return format_pattern.format(**components)
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{ADDRESS}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "ADDRESS",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, num_sentences: int = 10000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate address
            components = self.generate_address_components()
            address = self.apply_format(format_pattern, components)
            
            # Select random template
            template = random.choice(self.sentence_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(address, template)
            sentence_data["sentence_id"] = f"address_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "ADDRESS",
                "phi_label": "ADDRESS",
                "total_formats": len(self.variation_formats),
                "sentences_per_format": sentences_per_format,
                "total_sentences": len(self.variation_formats) * sentences_per_format,
                "sentence_templates": len(self.sentence_templates),
                "street_names": len(self.street_names),
                "street_types": len(self.street_types),
                "unit_types": len(self.unit_types),
                "cities": len(self.cities)
            },
            "formats": {}
        }
        
        current_id = 1
        
        for idx, format_pattern in enumerate(self.variation_formats, 1):
            print(f"[{idx}/{len(self.variation_formats)}] Generating format: {format_pattern}")
            
            dataset = self.generate_dataset_for_format(
                format_pattern,
                sentences_per_format,
                start_id=current_id
            )
            
            format_key = f"format_{idx:02d}"
            all_data['formats'][format_key] = {
                'pattern': format_pattern,
                'num_sentences': len(dataset),
                'sentences': dataset
            }
            
            current_id += len(dataset)
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: address_{current_id - len(dataset):06d} to address_{current_id - 1:06d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "address_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual addresses with {ADDRESS}."""
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
                # Replace actual address with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{ADDRESS}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "address_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{ADDRESS}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("Physical Address PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- Address formats: {len(self.variation_formats)}")
        print(f"- Sentence templates: {len(self.sentence_templates)}")
        print(f"- Street names: {len(self.street_names)}")
        print(f"- Street types: {len(self.street_types)}")
        print(f"- Unit types: {len(self.unit_types)}")
        print(f"- African cities: {len(self.cities)}")
        print(f"- Total output: {len(self.variation_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*60)
        print("✓ Physical Address PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = AddressGenerator()
    generator.run(sentences_per_format=10000)
