import json
import random
import os
from typing import List, Dict, Any

class URLGenerator:
    """Generate URL PII with realistic medical context sentences."""
    
    def __init__(self):
        self.variation_formats = [
            "{protocol}{subdomain}.{domain}{tld}",
            "{protocol}{domain}{tld}/{path}",
            "{subdomain}.{domain}{tld}"
        ]
        
        self.sentence_templates = [
            "Patient portal: {URL}.",
            "Visit {URL} for results.",
            "Website: {URL}.",
            "Access records at {URL}.",
            "Login to {URL} for appointments.",
            "Telehealth link: {URL}.",
            "Medical records available at {URL}.",
            "Register at {URL}.",
            "{NAME} accessed {URL}.",
            "For information, visit {URL}."
        ]
        
        # Load URL components
        self.load_url_components()
    
    def load_url_components(self):
        """Load URL components from JSON file."""
        try:
            with open('url_components.json', 'r') as f:
                data = json.load(f)
                self.protocols = data['protocols']
                self.subdomains = data['subdomains']
                self.domains = data['domains']
                self.tlds = data['tlds']
                self.paths = data['paths']
        except FileNotFoundError:
            print("Error: url_components.json not found!")
            raise
    
    def generate_url_components(self) -> Dict[str, str]:
        """Generate random URL components."""
        return {
            "protocol": random.choice(self.protocols),
            "subdomain": random.choice(self.subdomains),
            "domain": random.choice(self.domains),
            "tld": random.choice(self.tlds),
            "path": random.choice(self.paths)
        }
    
    def apply_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to URL components."""
        # Clean up protocol if needed
        protocol = components["protocol"].strip()
        return format_pattern.format(**components).replace("//", "/").replace("https://http", "https").replace("http://https", "https")
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{URL}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "URL",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, num_sentences: int = 10000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate URL
            components = self.generate_url_components()
            url = self.apply_format(format_pattern, components)
            
            # Clean up double protocols
            url = url.replace("https://https://", "https://").replace("http://http://", "http://")
            
            # Select random template
            template = random.choice(self.sentence_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(url, template)
            sentence_data["sentence_id"] = f"url_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "URL",
                "phi_label": "URL",
                "total_formats": len(self.variation_formats),
                "sentences_per_format": sentences_per_format,
                "total_sentences": len(self.variation_formats) * sentences_per_format,
                "sentence_templates": len(self.sentence_templates),
                "subdomains": len(self.subdomains),
                "domains": len(self.domains),
                "tlds": len(self.tlds),
                "paths": len(self.paths)
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
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: url_{current_id - len(dataset):06d} to url_{current_id - 1:06d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "url_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual URLs with {URL}."""
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
                # Replace actual URL with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{URL}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "url_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{URL}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("URL PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- URL formats: {len(self.variation_formats)}")
        print(f"- Sentence templates: {len(self.sentence_templates)}")
        print(f"- Subdomains: {len(self.subdomains)}")
        print(f"- Domains: {len(self.domains)}")
        print(f"- TLDs: {len(self.tlds)}")
        print(f"- Paths: {len(self.paths)}")
        print(f"- Total output: {len(self.variation_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*60)
        print("✓ URL PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = URLGenerator()
    generator.run(sentences_per_format=10000)
