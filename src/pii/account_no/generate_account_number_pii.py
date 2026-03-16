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
            # Basic account information
            "Account number: {ACCOUNT_NUMBER}.",
            "Patient account {ACCOUNT_NUMBER}.",
            "Medical account {ACCOUNT_NUMBER}.",
            "Healthcare account {ACCOUNT_NUMBER}.",
            "Account ID {ACCOUNT_NUMBER}.",
            
            # Billing and payment
            "Bill to account {ACCOUNT_NUMBER}.",
            "Patient account {ACCOUNT_NUMBER} has outstanding balance.",
            "Payment applied to {ACCOUNT_NUMBER}.",
            "Invoice sent to account {ACCOUNT_NUMBER}.",
            "Invoice number {ACCOUNT_NUMBER} issued.",
            "Charge to account {ACCOUNT_NUMBER}.",
            "Payment method on file for account {ACCOUNT_NUMBER}.",
            "Billing address for account {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} balance: $0.",
            "Please remit payment to account {ACCOUNT_NUMBER}.",
            
            # Authorization and procedures
            "Account {ACCOUNT_NUMBER} authorized for procedure.",
            "{NAME}'s account is {ACCOUNT_NUMBER}.",
            "{NAME} under account {ACCOUNT_NUMBER}.",
            "{NAME} (Account: {ACCOUNT_NUMBER}) paid in full.",
            "Patient {NAME} account {ACCOUNT_NUMBER}.",
            "Primary account holder {NAME} with account {ACCOUNT_NUMBER}.",
            
            # Reference and documentation
            "Reference account {ACCOUNT_NUMBER} for billing.",
            "Reference account {ACCOUNT_NUMBER}.",
            "See account {ACCOUNT_NUMBER} for details.",
            "Refer to account {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} on file.",
            "Account {ACCOUNT_NUMBER} linked to patient records.",
            
            # Financial account
            "Financial account: {ACCOUNT_NUMBER}.",
            "Insurance account {ACCOUNT_NUMBER}.",
            "Verification account {ACCOUNT_NUMBER}.",
            "Patient financial responsibility account {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} for co-payment.",
            "Deductible applied to account {ACCOUNT_NUMBER}.",
            
            # Administrative
            "Account {ACCOUNT_NUMBER} created.",
            "Account {ACCOUNT_NUMBER} updated.",
            "Account {ACCOUNT_NUMBER} verified.",
            "Account {ACCOUNT_NUMBER} confirmed.",
            "Account {ACCOUNT_NUMBER} activated.",
            "Account {ACCOUNT_NUMBER} status: Active.",
            
            # Correspondence
            "Statement for account {ACCOUNT_NUMBER} mailed.",
            "Correspondence sent to account {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} notice.",
            "Update regarding account {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} inquiry received.",
            "Contact regarding account {ACCOUNT_NUMBER}.",
            
            # Insurance and claims
            "Insurance claim filed under account {ACCOUNT_NUMBER}.",
            "Claim number {ACCOUNT_NUMBER} processed.",
            "Insurance account {ACCOUNT_NUMBER} updated.",
            "Coverage for account {ACCOUNT_NUMBER} active.",
            "Benefits applied to account {ACCOUNT_NUMBER}.",
            "Prior authorization for account {ACCOUNT_NUMBER}.",
            
            # Treatment and services
            "Services rendered to account {ACCOUNT_NUMBER}.",
            "Treatment for account {ACCOUNT_NUMBER} scheduled.",
            "Consultation billed to account {ACCOUNT_NUMBER}.",
            "Procedure billed to account {ACCOUNT_NUMBER}.",
            "Follow-up appointment for account {ACCOUNT_NUMBER}.",
            "Medications dispensed for account {ACCOUNT_NUMBER}.",
            
            # Records and documentation
            "Medical record account {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} contains patient history.",
            "Document routing to account {ACCOUNT_NUMBER}.",
            "Records associated with account {ACCOUNT_NUMBER}.",
            "Account {ACCOUNT_NUMBER} archived.",
            "Account {ACCOUNT_NUMBER} purged.",
            
            # Emergency and priority
            "Priority account {ACCOUNT_NUMBER}.",
            "Emergency account {ACCOUNT_NUMBER}.",
            "Urgent: Review account {ACCOUNT_NUMBER}.",
            "Critical flag on account {ACCOUNT_NUMBER}.",
            "Alert for account {ACCOUNT_NUMBER}.",
            "Follow up required for account {ACCOUNT_NUMBER}.",
            
            # Additional variations
            "Patient registered under account {ACCOUNT_NUMBER}.",
            "Enrollment processed for account {ACCOUNT_NUMBER}.",
            "New account {ACCOUNT_NUMBER} opened.",
            "Account {ACCOUNT_NUMBER} merged.",
            "Account {ACCOUNT_NUMBER} transferred.",
            "Account {ACCOUNT_NUMBER} reassigned.",
            "Duplicate account {ACCOUNT_NUMBER} flagged.",
            "Account {ACCOUNT_NUMBER} reconciliation pending.",
            "Due date for account {ACCOUNT_NUMBER} is {DATE}.",
            "Account {ACCOUNT_NUMBER} eligible for discount."
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
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        total_formats = len(self.variation_formats)
        
        all_data = {
            "metadata": {
                "entity_type": "ACCOUNT_NUMBER",
                "phi_label": "ID_ACCOUNT",
                "total_formats": total_formats,
                "sentences_per_format": sentences_per_format,
                "total_sentences": total_formats * sentences_per_format,
                "sentence_templates": len(self.sentence_templates),
                "account_prefixes": len(self.account_prefixes)
            },
            "formats": {}
        }
        
        current_id = 1
        
        print(f"\nGenerating {total_formats} format variations × {sentences_per_format} sentences each")
        print(f"Total sentences to generate: {total_formats * sentences_per_format:,}\n")
        
        for format_idx, format_pattern in enumerate(self.variation_formats, 1):
            print(f"[{format_idx}/{total_formats}] Generating format: {format_pattern}")
            
            format_sentences = []
            
            for sentence_num in range(sentences_per_format):
                # Pick a random template for variety
                template = random.choice(self.sentence_templates)
                
                # Generate account number using this format
                components = self.generate_account_components()
                account_number = self.apply_format(format_pattern, components)
                
                # Create sentence with annotations
                sentence = template.replace("{ACCOUNT_NUMBER}", account_number)
                
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
                start_pos = sentence.find(account_number)
                end_pos = start_pos + len(account_number)
                
                sentence_obj = {
                    "sentence_id": f"account_no_{current_id:08d}",
                    "sentence": sentence,
                    "entity": {
                        "start": start_pos,
                        "end": end_pos,
                        "label": "ID_ACCOUNT",
                        "value": account_number
                    },
                    "template_idx": self.sentence_templates.index(template) + 1,
                    "template_pattern": template,
                    "format": format_pattern
                }
                
                format_sentences.append(sentence_obj)
                current_id += 1
            
            format_key = f"format_{format_idx:02d}"
            all_data["formats"][format_key] = {
                "pattern": format_pattern,
                "num_sentences": len(format_sentences),
                "sentences": format_sentences
            }
            
            print(f"     ✓ Generated {len(format_sentences):,} sentences (IDs: account_no_{current_id - len(format_sentences):08d} to account_no_{current_id - 1:08d})")
        
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
                    sentence_obj["entity"]["value"],
                    "{ACCOUNT_NUMBER}"
                )
                
                template_data["formats"][format_key]["sentences"].append({
                    "sentence_id": sentence_obj["sentence_id"],
                    "sentence": template_sentence,
                    "template_idx": sentence_obj["template_idx"],
                    "template_pattern": sentence_obj["template_pattern"]
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
        print("\n" + "="*70)
        print("Account Number PII Generator - Enhanced")
        print("="*70)
        
        print(f"\nConfiguration:")
        print(f"- Account formats: {len(self.variation_formats)}")
        print(f"- Sentences per format: {sentences_per_format:,}")
        print(f"- Sentence templates available: {len(self.sentence_templates)}")
        print(f"- Account prefixes: {len(self.account_prefixes)}")
        print(f"- Total output: {len(self.variation_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*70)
        print("✓ Account Number PII generation complete!")
        print(f"  Generated {len(self.variation_formats) * sentences_per_format:,} total sentences")
        print(f"  Across {len(self.variation_formats)} format variations × {sentences_per_format:,} sentences each")
        print("="*70 + "\n")


if __name__ == "__main__":
    generator = AccountNumberGenerator()
    # Generate 16667 sentences per format (3 formats × 16667 ≈ 50,000 total)
    generator.run(sentences_per_format=16667)
