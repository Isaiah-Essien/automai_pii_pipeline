import json
import random
import os
from typing import List, Dict, Any

class AccountNumberGenerator:
    """Generate account number PII with realistic medical context sentences."""
    
    def __init__(self):
        self.variation_formats = [
            "{prefix}{number}",
            "{prefix}-{number}",
            "{prefix} {number}"
        ]
        
        self.account_prefixes = [
            "ACC", "ACCT", "ACN", "BIL", "PAT", "CUS", "CLT", "MEM", "SUB", "REF"
        ]
        
        self.sentence_templates = [
            "Account number: {ACCOUNT_NUMBER}.",
            "Bill to account {ACCOUNT_NUMBER}.",
            "Patient account {ACCOUNT_NUMBER} has outstanding balance.",
            "{NAME}'s account is {ACCOUNT_NUMBER}.",
            "Payment applied to {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} authorized for procedure.",
            "Invoice sent to account {ACCOUNT_NUMBER}.",
            "Financial account: {ACCOUNT_NUMBER}.",
            "{NAME} (Account: {ACCOUNT_NUMBER}) paid in full.",
            "Reference account {ACCOUNT_NUMBER} for billing."
        ]
    
    def generate_account_components(self) -> Dict[str, str]:
        """Generate random account number components."""
        return {
            "prefix": random.choice(self.account_prefixes),
            "number": str(random.randint(100000, 9999999))
        }
    
    def apply_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to account components."""
        return format_pattern.format(**components)
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{ACCOUNT_NUMBER}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "ID_ACCOUNT",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, num_sentences: int = 10000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate account number
            components = self.generate_account_components()
            account_number = self.apply_format(format_pattern, components)
            
            # Select random template
            template = random.choice(self.sentence_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(account_number, template)
            sentence_data["sentence_id"] = f"account_no_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "ACCOUNT_NUMBER",
                "phi_label": "ID_ACCOUNT",
                "total_formats": len(self.variation_formats),
                "sentences_per_format": sentences_per_format,
                "total_sentences": len(self.variation_formats) * sentences_per_format,
                "sentence_templates": len(self.sentence_templates),
                "account_prefixes": len(self.account_prefixes)
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
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: account_no_{current_id - len(dataset):06d} to account_no_{current_id - 1:06d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "account_number_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual account numbers with {ACCOUNT_NUMBER}."""
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
                # Replace actual account number with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{ACCOUNT_NUMBER}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "account_number_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{ACCOUNT_NUMBER}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("Account Number PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- Account formats: {len(self.variation_formats)}")
        print(f"- Sentence templates: {len(self.sentence_templates)}")
        print(f"- Account prefixes: {len(self.account_prefixes)}")
        print(f"- Total output: {len(self.variation_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*60)
        print("✓ Account Number PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = AccountNumberGenerator()
    generator.run(sentences_per_format=10000)
