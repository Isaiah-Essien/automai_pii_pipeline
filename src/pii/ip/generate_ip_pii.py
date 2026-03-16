import json
import random
import os
from typing import List, Dict, Any

class IPAddressGenerator:
    """Generate IP address PII with realistic medical context sentences."""
    
    def __init__(self):
        self.variation_formats = [
            "{octet1}.{octet2}.{octet3}.{octet4}"
        ]
        
        self.sentence_templates = [
            "Device IP: {IP_ADDRESS}.",
            "Patient accessed portal from {IP_ADDRESS}.",
            "Connection from {IP_ADDRESS}.",
            "System IP: {IP_ADDRESS}.",
            "Medical device at {IP_ADDRESS}.",
            "Login detected from {IP_ADDRESS}.",
            "Server IP: {IP_ADDRESS}.",
            "Network address {IP_ADDRESS} flagged.",
            "Equipment IP {IP_ADDRESS} online.",
            "Remote access via {IP_ADDRESS}."
        ]
    
    def generate_ip_components(self) -> Dict[str, int]:
        """Generate random IP address octets (0-255)."""
        return {
            "octet1": random.randint(1, 255),
            "octet2": random.randint(0, 255),
            "octet3": random.randint(0, 255),
            "octet4": random.randint(1, 255)
        }
    
    def apply_format(self, format_pattern: str, components: Dict[str, int]) -> str:
        """Apply format pattern to IP components."""
        return format_pattern.format(**components)
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{IP_ADDRESS}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "IP_ADDRESS",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, num_sentences: int = 10000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate IP address
            components = self.generate_ip_components()
            ip_address = self.apply_format(format_pattern, components)
            
            # Select random template
            template = random.choice(self.sentence_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(ip_address, template)
            sentence_data["sentence_id"] = f"ip_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "IP_ADDRESS",
                "phi_label": "IP_ADDRESS",
                "total_formats": len(self.variation_formats),
                "sentences_per_format": sentences_per_format,
                "total_sentences": len(self.variation_formats) * sentences_per_format,
                "sentence_templates": len(self.sentence_templates)
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
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: ip_{current_id - len(dataset):06d} to ip_{current_id - 1:06d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "ip_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual IP addresses with {IP_ADDRESS}."""
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
                # Replace actual IP address with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{IP_ADDRESS}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "ip_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{IP_ADDRESS}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("IP Address PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- IP formats: {len(self.variation_formats)}")
        print(f"- Sentence templates: {len(self.sentence_templates)}")
        print(f"- Total output: {len(self.variation_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*60)
        print("✓ IP Address PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = IPAddressGenerator()
    # Generate 50,000 sentences for single IP format (1 format × 50,000 = 50,000 total)
    generator.run(sentences_per_format=50000)
