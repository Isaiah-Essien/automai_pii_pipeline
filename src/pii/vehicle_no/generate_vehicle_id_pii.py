import json
import random
import os
from typing import List, Dict, Any

class VehicleIDGenerator:
    """Generate vehicle ID PII with realistic medical context sentences."""
    
    def __init__(self):
        self.variation_formats = [
            "{plate}",
            "{state} {plate}",
            "VIN: {vin}"
        ]
        
        self.sentence_templates = [
            "Vehicle plate: {VEHICLE_ID}.",
            "Patient arrived in vehicle {VEHICLE_ID}.",
            "Parking validated for {VEHICLE_ID}.",
            "{NAME} drives {VEHICLE_ID}.",
            "Vehicle identification: {VEHICLE_ID}.",
            "Plate {VEHICLE_ID} registered to {NAME}.",
            "Accident involved vehicle {VEHICLE_ID}.",
            "VIN {VEHICLE_ID} matched to patient.",
            "Emergency vehicle {VEHICLE_ID} transported patient.",
            "Registration {VEHICLE_ID} verified.",
            "Patient transport: {VEHICLE_ID}.",
            "Ambulance {VEHICLE_ID} dispatched.",
            "Medical transport vehicle {VEHICLE_ID} en route.",
            "{NAME} arrived by vehicle {VEHICLE_ID}.",
            "Vehicle {VEHICLE_ID} documented in incident report.",
            "Emergency services vehicle {VEHICLE_ID}.",
            "Hospital transport vehicle {VEHICLE_ID}.",
            "Plate {VEHICLE_ID} flagged in system.",
            "Patient transfer via {VEHICLE_ID}.",
            "Vehicle {VEHICLE_ID} assigned to case.",
            "Insurance claim vehicle {VEHICLE_ID}.",
            "Witness vehicle {VEHICLE_ID} identified.",
            "Transport log: {VEHICLE_ID}.",
            "Patient custody of vehicle {VEHICLE_ID}.",
            "Parking permit for {VEHICLE_ID} issued.",
            "Vehicle {VEHICLE_ID} checked by security.",
            "Disabled parking: {VEHICLE_ID}.",
            "Handicap accessible vehicle {VEHICLE_ID}.",
            "Wheelchair transport {VEHICLE_ID}.",
            "Medical personnel vehicle {VEHICLE_ID}.",
            "Staff parking assigned: {VEHICLE_ID}.",
            "Delivery vehicle {VEHICLE_ID} recorded.",
            "Pharmacy delivery by {VEHICLE_ID}.",
            "Medical supplies transport {VEHICLE_ID}.",
            "Lab specimen transport {VEHICLE_ID}.",
            "Organ transport vehicle {VEHICLE_ID}.",
            "Blood bank vehicle {VEHICLE_ID}.",
            "Specimen courier {VEHICLE_ID}.",
            "Home care visit by {VEHICLE_ID}.",
            "Visiting nurse vehicle {VEHICLE_ID}.",
            "Mobile clinic {VEHICLE_ID}.",
            "Telemedicine vehicle {VEHICLE_ID}.",
            "Mobile health unit {VEHICLE_ID}.",
            "Vaccination drive vehicle {VEHICLE_ID}.",
            "Outreach program vehicle {VEHICLE_ID}.",
            "Clinical trial transport {VEHICLE_ID}.",
            "Patient volunteer vehicle {VEHICLE_ID}.",
            "Caregiver arrival: {VEHICLE_ID}.",
            "Family visit vehicle {VEHICLE_ID}.",
            "Visitor vehicle {VEHICLE_ID} authorized.",
            "Companion transport {VEHICLE_ID}.",
            "Medical escort vehicle {VEHICLE_ID}.",
            "Personnel vehicle {VEHICLE_ID} badge valid.",
            "Security patrol vehicle {VEHICLE_ID}.",
            "Maintenance vehicle {VEHICLE_ID} on site."
        ]
        
        # Load vehicle components
        self.load_vehicle_components()
    
    def load_vehicle_components(self):
        """Load vehicle components from JSON file."""
        try:
            with open('vehicle_components.json', 'r') as f:
                data = json.load(f)
                self.countries_and_plates = data['countries_and_plates']
                self.plate_formats = data['plate_number_formats']
                self.vin_manufacturers = data['vin_manufacturers']
                self.vin_years = data['vin_years']
                self.vin_plants = data['vin_plants']
        except FileNotFoundError:
            print("Error: vehicle_components.json not found!")
            raise
    
    def generate_plate(self) -> tuple:
        """Generate a realistic vehicle plate and state."""
        country_data = random.choice(list(self.countries_and_plates.values()))
        state = random.choice(country_data['states'])
        
        # Choose format
        plate_format = random.choice(country_data['plate_formats'])
        
        # Generate components
        digits1 = random.choice(self.plate_formats['digits1'])
        digits2 = random.choice(self.plate_formats['digits2'])
        digits = random.choice(self.plate_formats['digits'])
        letters = random.choice(self.plate_formats['letters'])
        
        plate = plate_format.format(
            state=state,
            digits1=digits1,
            digits2=digits2,
            digits=digits,
            letters=letters
        )
        
        return plate, state
    
    def generate_vin(self) -> str:
        """Generate a realistic 17-character VIN."""
        # Position 1-3: Manufacturer (WMI)
        manufacturer = random.choice(self.vin_manufacturers)
        
        # Position 4-9: Descriptor (model, body, engine, transmission, etc.)
        descriptor = ''.join([random.choice('ABCDEFGHJKLMNPRSTUVWXYZ0123456789') for _ in range(6)])
        
        # Position 10: Check digit
        check_digit = str(random.randint(0, 9))
        
        # Position 11: Year
        year = random.choice(self.vin_years)
        
        # Position 12: Plant
        plant = random.choice(self.vin_plants)
        
        # Position 13-17: Serial number
        serial = ''.join([str(random.randint(0, 9)) for _ in range(5)])
        
        vin = manufacturer + descriptor + check_digit + year + plant + serial
        return vin
    
    def apply_format(self, format_pattern: str, plate: str, state: str, vin: str) -> str:
        """Apply format pattern to vehicle components."""
        return format_pattern.format(
            plate=plate,
            state=state,
            vin=vin
        )
    
    def create_sentence(self, entity_value: str, template: str) -> Dict[str, Any]:
        """Create sentence with entity annotation and character offsets."""
        sentence = template.replace("{VEHICLE_ID}", entity_value)
        
        # Calculate character offsets
        start_pos = sentence.find(entity_value)
        end_pos = start_pos + len(entity_value)
        
        return {
            "sentence": sentence,
            "entities": [
                {
                    "start": start_pos,
                    "end": end_pos,
                    "label": "ID_VEHICLE",
                    "value": entity_value
                }
            ]
        }
    
    def generate_dataset_for_format(self, format_pattern: str, num_sentences: int = 10000, start_id: int = 1) -> List[Dict[str, Any]]:
        """Generate dataset for a specific format."""
        dataset = []
        
        for i in range(num_sentences):
            # Generate vehicle components
            plate, state = self.generate_plate()
            vin = self.generate_vin()
            
            # Apply format
            vehicle_id = self.apply_format(format_pattern, plate, state, vin)
            
            # Select random template
            template = random.choice(self.sentence_templates)
            
            # Create sentence with annotations
            sentence_data = self.create_sentence(vehicle_id, template)
            sentence_data["sentence_id"] = f"vehicle_id_{start_id + i:06d}"
            
            dataset.append(sentence_data)
        
        return dataset
    
    def generate_complete_dataset(self, sentences_per_format: int = 10000) -> Dict[str, Any]:
        """Generate complete dataset across all format variations."""
        all_data = {
            "metadata": {
                "entity_type": "VEHICLE_ID",
                "phi_label": "ID_VEHICLE",
                "total_formats": len(self.variation_formats),
                "sentences_per_format": sentences_per_format,
                "total_sentences": len(self.variation_formats) * sentences_per_format,
                "sentence_templates": len(self.sentence_templates),
                "countries_covered": len(self.countries_and_plates),
                "plate_formats_per_country": len(self.countries_and_plates)
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
            print(f"     ✓ Generated {len(dataset)} sentences (IDs: vehicle_id_{current_id - len(dataset):06d} to vehicle_id_{current_id - 1:06d})")
        
        return all_data
    
    def save_dataset(self, data: Dict[str, Any], filename: str = "vehicle_id_pii_dataset.json"):
        """Save complete dataset to JSON file."""
        print(f"\nSaving to {filename}...")
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Saved successfully! File size: {file_size_mb:.2f} MB")
    
    def create_template_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create template dataset by replacing actual vehicle IDs with {VEHICLE_ID}."""
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
                # Replace actual vehicle ID with placeholder
                template_sentence = sentence_obj["sentence"].replace(
                    sentence_obj["entities"][0]["value"],
                    "{VEHICLE_ID}"
                )
                template_data["formats"][format_key]["sentences"].append({
                    "sentence": template_sentence,
                    "sentence_id": sentence_obj["sentence_id"]
                })
        
        return template_data
    
    def save_template_dataset(self, data: Dict[str, Any], filename: str = "vehicle_id_pii_templates.json"):
        """Save template dataset to JSON file."""
        print(f"Creating template dataset with {{VEHICLE_ID}} placeholders...")
        template_data = self.create_template_dataset(data)
        
        print(f"Saving templates to {filename}...")
        with open(filename, 'w') as f:
            json.dump(template_data, f, indent=2)
        
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        print(f"✓ Template file saved successfully! File size: {file_size_mb:.2f} MB")
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save both dataset and template files."""
        print("\n" + "="*60)
        print("Vehicle ID PII Generator")
        print("="*60)
        
        print(f"\nConfiguration:")
        print(f"- Vehicle ID formats: {len(self.variation_formats)}")
        print(f"- Sentence templates: {len(self.sentence_templates)}")
        print(f"- African countries covered: {len(self.countries_and_plates)}")
        print(f"- Total output: {len(self.variation_formats) * sentences_per_format:,} sentences")
        print()
        
        # Generate complete dataset
        data = self.generate_complete_dataset(sentences_per_format)
        
        # Save dataset
        self.save_dataset(data)
        
        # Save template dataset
        self.save_template_dataset(data)
        
        print("\n" + "="*60)
        print("✓ Vehicle ID PII generation complete!")
        print("="*60 + "\n")


if __name__ == "__main__":
    generator = VehicleIDGenerator()
    generator.run(sentences_per_format=10000)
