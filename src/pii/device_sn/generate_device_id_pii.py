import json
import random
import os
import string
from typing import List, Dict, Any

class DeviceIDGenerator:
    """Generate device ID PII with realistic medical context sentences."""
    
    def __init__(self):
        self.variation_formats = [
            "{manufacturer} {model} S/N: {serial}",
            "Serial: {serial}",
            "{model}-{serial}",
            "Device ID: {serial}"
        ]
        
        self.sentence_templates = [
            "Implant serial number: {DEVICE_ID}.",
            "Device {DEVICE_ID} implanted in {NAME}.",
            "Pacemaker SN: {DEVICE_ID}.",
            "Medical device {DEVICE_ID} recalled.",
            "{NAME} has device {DEVICE_ID} implanted.",
            "Equipment serial: {DEVICE_ID}.",
            "Monitor {DEVICE_ID} assigned to patient.",
            "Device ID {DEVICE_ID} tracked.",
            "Prosthetic {DEVICE_ID} fitted on {DATE}.",
            "Implant {DEVICE_ID} requires follow-up.",
            "Device {DEVICE_ID} malfunction reported.",
            "Cardiovascular implant {DEVICE_ID}.",
            "Replacement device {DEVICE_ID} ordered.",
            "Device {DEVICE_ID} battery replacement scheduled.",
            "Orthopedic implant {DEVICE_ID} successful.",
            "Spinal fusion device {DEVICE_ID}.",
            "Hip replacement {DEVICE_ID} installed.",
            "Knee implant {DEVICE_ID} verified.",
            "Dental implant {DEVICE_ID} placed.",
            "Eye lens implant {DEVICE_ID}.",
            "Cochlear implant {DEVICE_ID} activated.",
            "Neurostimulator {DEVICE_ID} programmed.",
            "Infusion pump {DEVICE_ID} calibrated.",
            "Ventilator {DEVICE_ID} in use.",
            "Dialysis machine {DEVICE_ID} operational.",
            "CPAP device {DEVICE_ID} dispensed.",
            "Oxygen concentrator {DEVICE_ID} assigned.",
            "Insulin pump {DEVICE_ID} initialized.",
            "Glucose monitor {DEVICE_ID} connected.",
            "Blood pressure monitor {DEVICE_ID}.",
            "Pulse oximeter {DEVICE_ID} deployed.",
            "ECG monitor {DEVICE_ID} active.",
            "Cardiac defibrillator {DEVICE_ID}.",
            "Pacemaker lead {DEVICE_ID} positioned.",
            "Heart valve prosthetic {DEVICE_ID}.",
            "Stent placement {DEVICE_ID}.",
            "Catheter device {DEVICE_ID}.",
            "Endoscopy equipment {DEVICE_ID}.",
            "Ultrasound machine {DEVICE_ID}.",
            "CT scanner {DEVICE_ID}}.",
            "MRI system {DEVICE_ID}.",
            "X-ray equipment {DEVICE_ID}.",
            "Surgical robot {DEVICE_ID} ready.",
            "Anesthesia machine {DEVICE_ID}}.",
            "Patient monitor {DEVICE_ID} attached.",
            "IV pump {DEVICE_ID} connected.",
            "Suction apparatus {DEVICE_ID}}.",
            "Temperature regulation {DEVICE_ID}}.",
            "Light source {DEVICE_ID}}.",
            "Surgical laser {DEVICE_ID}}.",
            "Electrocautery unit {DEVICE_ID}}.",
            "Bone drill {DEVICE_ID}}.",
            "Microscope {DEVICE_ID}}.",
            "Defibrillation pad {DEVICE_ID}}.",
            "Compression device {DEVICE_ID}}.",
            "Vascular access device {DEVICE_ID}}.",
            "Feeding tube equipment {DEVICE_ID}}.",
            "Wound closure device {DEVICE_ID}}.",
            "Dressing material {DEVICE_ID}}.",
            "Support stockings {DEVICE_ID}}.",
            "Pressure relief mattress {DEVICE_ID}}.",
            "Hospital bed {DEVICE_ID}}.",
            "Patient lift {DEVICE_ID}}.",
            "Wheelchair {DEVICE_ID}}.",
            "Crutches set {DEVICE_ID}}.",
            "Prosthetic limb {DEVICE_ID}}.",
            "Orthotic brace {DEVICE_ID}}.",
            "Hearing aid {DEVICE_ID}}.",
            "Vision aid {DEVICE_ID}}.",
            "Mobility scooter {DEVICE_ID}}.",
            "Alarm system {DEVICE_ID}}.",
            "Communication device {DEVICE_ID}}.",
            "Telemedicine monitor {DEVICE_ID}}.",
            "Home monitoring kit {DEVICE_ID}}.",
            "Medication dispenser {DEVICE_ID}}.",
            "Robotic aid {DEVICE_ID}}.",
            "Assistive technology {DEVICE_ID}}.",
            "Preventive equipment {DEVICE_ID}}.",
            "Maintenance schedule {DEVICE_ID}}.",
            "Calibration record {DEVICE_ID}}.",
            "Quality assurance {DEVICE_ID}}.",
            "Inspection confirmed {DEVICE_ID}}.",
            "Sterilization log {DEVICE_ID}}.",
            "Warranty period {DEVICE_ID}}.",
            "Service contract {DEVICE_ID}}.",
            "Training completed {DEVICE_ID}}.",
            "Certification obtained {DEVICE_ID}}.",
            "FDA approved {DEVICE_ID}}.",
            "Insurance covered {DEVICE_ID}}.",
            "Inventory tracked {DEVICE_ID}}.",
            "Asset management {DEVICE_ID}}.",
            "Depreciation schedule {DEVICE_ID}}.",
            "Disposal protocol {DEVICE_ID}}."
        ]
        
        # Load device components
        self.load_device_components()
    
    def load_device_components(self):
        """Load device components from JSON file."""
        try:
            with open('device_components.json', 'r') as f:
                data = json.load(f)
                self.manufacturers = data['manufacturers']
                self.medical_device_models = data['medical_device_models']
                self.serial_prefixes = data['serial_prefixes']
                self.serial_number_length = data['serial_number_length']
                self.character_sets = data['character_sets']
        except FileNotFoundError:
            print("Error: device_components.json not found!")
            raise
    
    def generate_serial(self) -> str:
        """Generate a realistic serial number."""
        length = random.choice(self.serial_number_length)
        # Mix of alphanumeric characters
        serial = ''.join(random.choices(self.character_sets['alphanumeric'], k=length))
        return serial
    
    def generate_device_components(self) -> Dict[str, str]:
        """Generate random device components."""
        manufacturer = random.choice(self.manufacturers)
        
        # Select random device category and model
        category = random.choice(list(self.medical_device_models.keys()))
        model = random.choice(self.medical_device_models[category])
        
        serial = self.generate_serial()
        
        return {
            "manufacturer": manufacturer,
            "model": model,
            "serial": serial
        }
    
    def apply_format(self, format_pattern: str, components: Dict[str, str]) -> str:
        """Apply format pattern to device components."""
        return format_pattern.format(**components)
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{DEVICE_ID}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "ID_DEVICE",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, num_sentences: int = 10000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate device
            components = self.generate_device_components()
            device_id = self.apply_format(format_pattern, components)
            
            # Select random template
            template = random.choice(self.sentence_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(device_id, template)
            sentence_data["sentence_id"] = f"device_id_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "DEVICE_ID",
                "phi_label": "ID_DEVICE",
                "total_formats": len(self.variation_formats),
                "sentences_per_format": sentences_per_format,
                "total_sentences": len(self.variation_formats) * sentences_per_format,
                "sentence_templates": len(self.sentence_templates),
                "manufacturers": len(self.manufacturers),
                "device_categories": len(self.medical_device_models)
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
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: device_id_{current_id - len(dataset):06d} to device_id_{current_id - 1:06d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "device_id_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual device IDs with {DEVICE_ID}."""
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
                # Replace actual device ID with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{DEVICE_ID}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "device_id_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{DEVICE_ID}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("Device ID PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- Device ID formats: {len(self.variation_formats)}")
        print(f"- Sentence templates: {len(self.sentence_templates)}")
        print(f"- Medical device manufacturers: {len(self.manufacturers)}")
        print(f"- Device categories: {len(self.medical_device_models)}")
        print(f"- Total output: {len(self.variation_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*60)
        print("✓ Device ID PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = DeviceIDGenerator()
    # Generate 25,000 sentences per format (4 formats × 25,000 = 100,000 total)
    generator.run(sentences_per_format=25000)
