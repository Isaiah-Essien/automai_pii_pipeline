import json
import random
import os
from typing import List, Dict, Any

class SSNGenerator:
    """Generate social security number PII with realistic medical context sentences."""
    
    def __init__(self):
        self.variation_formats = [
            "{part1}-{part2}-{part3}",
            "{part1} {part2} {part3}",
            "{part1}{part2}{part3}",
            "***-**-{part3}",
            "XXX-XX-{part3}"
        ]
        
        self.sentence_templates = [
            "Patient SSN: {SSN}.",
            "{NAME}'s social security number is {SSN}.",
            "National ID {SSN} verified.",
            "SSN on file: {SSN}.",
            "ID verification: {SSN}.",
            "Tax ID: {SSN}.",
            "{NAME} (SSN: {SSN}) enrolled in program.",
            "Billing SSN: {SSN}.",
            "Insurance requires SSN {SSN}.",
            "Identity confirmed with {SSN}.",
            "SSN {SSN} matched in system.",
            "Background check SSN {SSN}.",
            "Employment verification SSN {SSN}.",
            "Patient identifier: SSN {SSN}.",
            "Primary ID number {SSN}.",
            "Government ID {SSN} on record.",
            "Federation reference {SSN}.",
            "Social identifier {SSN} verified.",
            "Healthcare ID {SSN} active.",
            "Insurance member {SSN}.",
            "Provider NPI linked to {SSN}.",
            "Beneficiary SSN {SSN}.",
            "Dependent SSN {SSN}.",
            "Sponsor SSN {SSN} authorized.",
            "Emergency contact SSN {SSN}.",
            "Power of attorney SSN {SSN}.",
            "Healthcare proxy SSN {SSN}.",
            "Authorized representative {SSN}.",
            "Legal guardian SSN {SSN}.",
            "Next of kin SSN {SSN}.",
            "Birth record SSN {SSN}.",
            "Vital statistics {SSN}.",
            "Registration number {SSN}.",
            "License verification {SSN}.",
            "Professional credential {SSN}.",
            "Practitioner ID {SSN}.",
            "Staff SSN {SSN} active.",
            "Employee ID {SSN}.",
            "Credentialing SSN {SSN}.",
            "Privileging approval {SSN}.",
            "Medical director SSN {SSN}.",
            "Clinical lead identifier {SSN}.",
            "Department head {SSN}.",
            "Compliance record {SSN}.",
            "Audit trail SSN {SSN}.",
            "Verification timestamp SSN {SSN}.",
            "Consent form signed {SSN}.",
            "Authorization code {SSN}.",
            "Release of information {SSN}.",
            "HIPAA authorization {SSN}.",
            "Privacy agreement {SSN}.",
            "Billing statement {SSN}.",
            "Invoice reference {SSN}.",
            "Payment record {SSN}.",
            "Financial account {SSN}.",
            "Banking information {SSN}.",
            "Mortgage SSN {SSN}.",
            "Credit check {SSN}.",
            "Collections reference {SSN}.",
            "Debt verification {SSN}.",
            "Court order case {SSN}.",
            "Legal proceeding {SSN}.",
            "Prosecution case number {SSN}.",
            "Evidence tracking {SSN}.",
            "Case file reference {SSN}.",
            "Incident number {SSN}.",
            "Report number {SSN}.",
            "Arrest record {SSN}.",
            "Conviction registry {SSN}.",
            "Parole officer SSN {SSN}.",
            "Probation tracker {SSN}.",
            "Criminal history {SSN}.",
            "Sex offender registry {SSN}.",
            "Watchlist entry {SSN}.",
            "Threat assessment {SSN}.",
            "Risk evaluation {SSN}.",
            "Safety protocol {SSN}.",
            "Restraining order {SSN}.",
            "No-contact order {SSN}.",
            "Protective custody {SSN}.",
            "Witness protection {SSN}.",
            "Relocation services {SSN}.",
            "Safe house registration {SSN}.",
            "Crisis intervention {SSN}.",
            "Mental health eval {SSN}.",
            "Psychiatric hold {SSN}.",
            "Substance abuse treatment {SSN}.",
            "Rehabilitation program {SSN}.",
            "Recovery tracking {SSN}.",
            "Medication monitoring {SSN}.",
            "Drug screening {SSN}.",
            "Toxicology report {SSN}."
        ]
    
    def generate_ssn_components(self) -> Dict[str, str]:
        """Generate random SSN components."""
        part1 = str(random.randint(1, 899)).zfill(3)
        part2 = str(random.randint(1, 99)).zfill(2)
        part3 = str(random.randint(1, 9999)).zfill(4)
        
        return {
            "part1": part1,
            "part2": part2,
            "part3": part3
        }
    
    def apply_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to SSN components."""
        return format_pattern.format(**components)
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{SSN}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "ID_SSN",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, num_sentences: int = 10000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate SSN
            components = self.generate_ssn_components()
            ssn = self.apply_format(format_pattern, components)
            
            # Select random template
            template = random.choice(self.sentence_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(ssn, template)
            sentence_data["sentence_id"] = f"ssn_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "SSN",
                "phi_label": "ID_SSN",
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
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: ssn_{current_id - len(dataset):06d} to ssn_{current_id - 1:06d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "ssn_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual SSNs with {SSN}."""
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
                # Replace actual SSN with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{SSN}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "ssn_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{SSN}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("Social Security Number (SSN) PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- SSN formats: {len(self.variation_formats)}")
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
        print("✓ SSN PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = SSNGenerator()
    generator.run(sentences_per_format=10000)
