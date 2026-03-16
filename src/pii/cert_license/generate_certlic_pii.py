import json
import random
import os
from typing import List, Dict, Any

class CertificateLicenseGenerator:
    """Generate certificate and license PII with realistic medical context sentences."""
    
    def __init__(self):
        # Certificate formats
        self.certificate_formats = [
            "{type} Certificate: {number}",
            "{type} Cert #{number}",
            "{number}/{year}"
        ]
        
        # License formats
        self.license_formats = [
            "{prefix}{number}",
            "{prefix}-{number}",
            "{prefix} {number}"
        ]
        
        # All formats combined
        self.all_formats = [
            ("CERTIFICATE", self.certificate_formats),
            ("LICENSE", self.license_formats)
        ]
        
        self.certificate_templates = [
            "Birth certificate: {CERTLIC}.",
            "Death certificate {CERTLIC} issued.",
            "{NAME}'s birth certificate: {CERTLIC}.",
            "Certificate number {CERTLIC} on file.",
            "Marriage certificate: {CERTLIC}.",
            "Official certificate {CERTLIC} verified.",
            "Certificate {CERTLIC} dated {DATE}.",
            "Legal document {CERTLIC} submitted.",
            "Certificate ID {CERTLIC} authenticated.",
            "{NAME} provided certificate {CERTLIC}.",
            "Adoption certificate {CERTLIC} filed.",
            "Naturalization certificate {CERTLIC}.",
            "Vaccination record {CERTLIC}.",
            "Medical certification {CERTLIC} obtained.",
            "Professional credential {CERTLIC}.",
            "Educational certificate {CERTLIC}.",
            "Training completion {CERTLIC}.",
            "Competency assessment {CERTLIC}.",
            "Board certification {CERTLIC} active.",
            "Specialty certification {CERTLIC}.",
            "Travel document {CERTLIC}.",
            "Immigration certificate {CERTLIC}.",
            "Work authorization {CERTLIC}.",
            "Security clearance {CERTLIC}.",
            "Diplomatic credential {CERTLIC}.",
            "Divorce certificate {CERTLIC}.",
            "Certificate renewal {CERTLIC} pending.",
            "Certificate expiration {CERTLIC} scheduled.",
            "Certificate archived {CERTLIC}.",
            "Digital certificate {CERTLIC}.",
            "Verified certificate {CERTLIC}.",
            "Notarized certificate {CERTLIC}.",
            "Original certificate {CERTLIC} retained.",
            "Copy of certificate {CERTLIC}.",
            "Certificate template {CERTLIC}}.",
            "Blockchain certificate {CERTLIC}.",
            "Certificate registry {CERTLIC}}.",
            "Certificate repository {CERTLIC}}.",
            "Certificate database {CERTLIC}}.",
            "Certificate tracking {CERTLIC}}."
        ]
        
        self.license_templates = [
            "Driver's license: {CERTLIC}.",
            "{NAME}'s license number is {CERTLIC}.",
            "Professional license {CERTLIC} verified.",
            "MD license: {CERTLIC}.",
            "Nurse {NAME} (License: {CERTLIC}) on duty.",
            "RN license {CERTLIC} expires {DATE}.",
            "Pharmacist license: {CERTLIC}.",
            "DL {CERTLIC} on file.",
            "License verification: {CERTLIC}.",
            "Provider license {CERTLIC} active.",
            "Dental license {CERTLIC}.",
            "Legal bar license {CERTLIC}.",
            "Psychology license {CERTLIC}}.",
            "Social work license {CERTLIC}}.",
            "Architecture license {CERTLIC}}.",
            "Engineering license {CERTLIC}}.",
            "CPA license {CERTLIC}}.",
            "Real estate license {CERTLIC}}.",
            "Insurance license {CERTLIC}}.",
            "Aviation license {CERTLIC}}.",
            "Marine license {CERTLIC}}.",
            "Veterinary license {CERTLIC}}.",
            "License renewal {CERTLIC}}.",
            "License expiration {CERTLIC}}.",
            "License suspension {CERTLIC}}.",
            "License revocation {CERTLIC}}.",
            "License reinstatement {CERTLIC}}.",
            "License application {CERTLIC}}.",
            "License background check {CERTLIC}}.",
            "License continuing education {CERTLIC}}.",
            "License board examination {CERTLIC}}.",
            "License approved {CERTLIC}}.",
            "License provisional {CERTLIC}}.",
            "License restricted {CERTLIC}}.",
            "License conditional {CERTLIC}}.",
            "License reciprocal {CERTLIC}}.",
            "License interstate {CERTLIC}}.",
            "License digital {CERTLIC}}.",
            "License credential {CERTLIC}}.",
            "License verification system {CERTLIC}}."
        ]
        
        # Load components
        self.load_components()
    
    def load_components(self):
        """Load certificate and license components from JSON file."""
        try:
            with open('cert_license_components.json', 'r') as f:
                data = json.load(f)
                self.certificate_types = data['certificate_types']
                self.license_prefixes = data['license_prefixes']
                self.years = data['years']
        except FileNotFoundError:
            print("Error: cert_license_components.json not found!")
            raise
    
    def generate_certificate(self) -> Dict[str, str]:
        """Generate certificate components."""
        return {
            "type": random.choice(self.certificate_types),
            "number": str(random.randint(100000, 9999999)),
            "year": str(random.choice(self.years))
        }
    
    def generate_license(self) -> Dict[str, str]:
        """Generate license components."""
        category = random.choice(list(self.license_prefixes.keys()))
        prefix = random.choice(self.license_prefixes[category])
        number = str(random.randint(10000, 9999999))
        
        return {
            "prefix": prefix,
            "number": number
        }
    
    def apply_certificate_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to certificate components."""
        return format_pattern.format(**components)
    
    def apply_license_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to license components."""
        return format_pattern.format(**components)
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{CERTLIC}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "ID_CERTLIC",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_certificate_format(self, format_pattern: str, num_sentences: int = 5000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific certificate format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate certificate
            components = self.generate_certificate()
            cert = self.apply_certificate_format(format_pattern, components)
            
            # Select random template
            template = random.choice(self.certificate_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(cert, template)
            sentence_data["sentence_id"] = f"certlic_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_dataset_for_license_format(self, format_pattern: str, num_sentences: int = 5000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific license format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate license
            components = self.generate_license()
            license_id = self.apply_license_format(format_pattern, components)
            
            # Select random template
            template = random.choice(self.license_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(license_id, template)
            sentence_data["sentence_id"] = f"certlic_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "CERTIFICATE_LICENSE",
                "phi_label": "ID_CERTLIC",
                "total_certificate_formats": len(self.certificate_formats),
                "total_license_formats": len(self.license_formats),
                "sentences_per_format": sentences_per_format,
                "total_sentences": (len(self.certificate_formats) + len(self.license_formats)) * sentences_per_format,
                "certificate_templates": len(self.certificate_templates),
                "license_templates": len(self.license_templates),
                "certificate_types": len(self.certificate_types)
            },
            "formats": {}
        }
        
        current_id = 1
        format_idx = 1
        
        # Generate certificate formats
        print("\nGenerating Certificate Formats:")
        for cert_format in self.certificate_formats:
            print(f"[{format_idx}/{len(self.certificate_formats) + len(self.license_formats)}] Generating certificate format: {cert_format}")
            
            dataset = self.generate_dataset_for_certificate_format(
                cert_format,
                sentences_per_format,
                start_id=current_id
            )
            
            format_key = f"format_{format_idx:02d}"
            all_data['formats'][format_key] = {
                'type': 'CERTIFICATE',
                'pattern': cert_format,
                'num_sentences': len(dataset),
                'sentences': dataset
            }
            
            current_id += len(dataset)
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: certlic_{current_id - len(dataset):06d} to certlic_{current_id - 1:06d})")
            format_idx += 1
        
        # Generate license formats
        print("\nGenerating License Formats:")
        for lic_format in self.license_formats:
            print(f"[{format_idx}/{len(self.certificate_formats) + len(self.license_formats)}] Generating license format: {lic_format}")
            
            dataset = self.generate_dataset_for_license_format(
                lic_format,
                sentences_per_format,
                start_id=current_id
            )
            
            format_key = f"format_{format_idx:02d}"
            all_data['formats'][format_key] = {
                'type': 'LICENSE',
                'pattern': lic_format,
                'num_sentences': len(dataset),
                'sentences': dataset
            }
            
            current_id += len(dataset)
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: certlic_{current_id - len(dataset):06d} to certlic_{current_id - 1:06d})")
            format_idx += 1
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "certlic_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual IDs with {CERTLIC}."""
        template_data = {
            "metadata": data["metadata"],
            "formats": {}
        }
        
        for format_key, format_data in data["formats"].items():
            template_data["formats"][format_key] = {
                "type": format_data["type"],
                "pattern": format_data["pattern"],
                "num_sentences": format_data["num_sentences"],
                "sentences": []
            }
            
            for sentence_obj in format_data["sentences"]:
                # Replace actual ID with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{CERTLIC}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "certlic_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{CERTLIC}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("Certificate & License PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- Certificate formats: {len(self.certificate_formats)}")
        print(f"- License formats: {len(self.license_formats)}")
        print(f"- Sentences per format: {sentences_per_format:,}")
        print(f"- Certificate templates: {len(self.certificate_templates)}")
        print(f"- License templates: {len(self.license_templates)}")
        print(f"- Certificate types: {len(self.certificate_types)}")
        print(f"- License categories: {len(self.license_prefixes)}")
        print(f"- Total output: {(len(self.certificate_formats) + len(self.license_formats)) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*60)
        print("✓ Certificate & License PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = CertificateLicenseGenerator()
    generator.run(sentences_per_format=10000)
