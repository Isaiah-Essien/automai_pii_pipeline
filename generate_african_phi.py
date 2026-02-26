#!/usr/bin/env python3
"""
African PHI Data Generator
===========================

Generates short, focused medical text with African PHI entities.
Optimized for African healthcare data with country-specific information.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter

try:
    from faker import Faker
except ImportError:
    raise ImportError("Please install faker: pip install faker")


class AfricanPHIGenerator:
    """
    Generator for African-focused PHI data with short sentences.
    """

    def __init__(
        self,
        config_path: str = "phi_config.json",
        seed: Optional[int] = None
    ):
        """Initialize with configuration file."""
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        if seed:
            random.seed(seed)
            Faker.seed(seed)
        
        # Initialize Faker (use default locale, we have custom African data)
        self.faker = Faker('en_US')
        
        self.african_countries = self.config['african_countries']
        self.entity_config = self.config['entity_types']
        self.output_settings = self.config['output_settings']
        
        # Common African first and last names
        self.african_first_names = [
            "Amara", "Kwame", "Ayo", "Zuri", "Chinwe", "Kofi", "Aisha", "Jabari",
            "Nia", "Sekou", "Fatima", "Thabo", "Amina", "Kwesi", "Zara", "Tendai",
            "Oluwa", "Makena", "Tariq", "Imani", "Adebayo", "Kamau", "Aaliyah", "Nuru",
            "Chidi", "Wanjiru", "Habib", "Zalika", "Otieno", "Nadira", "Babatunde",
            "Akinyi", "Rashid", "Kadijah", "Musa", "Abena", "Jelani", "Nkechi"
        ]
        
        self.african_last_names = [
            "Okonkwo", "Mwangi", "Nkosi", "Mensah", "Okeke", "Kamara", "Diop", "Ngozi",
            "Adeyemi", "Wanjiku", "Banda", "Kwame", "Ibrahim", "Osei", "Mutombo",
            "Oluwaseun", "Kariuki", "Moyo", "Abebe", "Nnamdi", "Otieno", "Zulu",
            "Kagiso", "Amadi", "Kiprono", "Boateng", "Uwem", "Temitope"
        ]
        
        # Common African street names
        self.african_streets = [
            "Uhuru", "Independence", "Nelson Mandela", "Haile Selassie", "Kwame Nkrumah",
            "Julius Nyerere", "Moi", "Kenyatta", "Victoria", "Market", "Station",
            "Church", "Hospital", "University", "Airport", "Beach", "Garden"
        ]

    def get_random_country(self) -> Tuple[str, Dict]:
        """Get random African country with its data."""
        country_name = random.choice(list(self.african_countries.keys()))
        return country_name, self.african_countries[country_name]

    def generate_person(self) -> str:
        """Generate African person name."""
        first = random.choice(self.african_first_names)
        last = random.choice(self.african_last_names)
        return f"{first} {last}"

    def generate_address(self) -> str:
        """Generate African street address."""
        number = random.randint(1, 999)
        street = random.choice(self.african_streets)
        street_type = random.choice(["Road", "Street", "Avenue", "Way", "Drive"])
        return f"{number} {street} {street_type}"

    def generate_city(self) -> str:
        """Generate African city."""
        country_name, country_data = self.get_random_country()
        return random.choice(country_data['cities'])

    def generate_state(self) -> str:
        """Generate African state/province/region."""
        country_name, country_data = self.get_random_country()
        return random.choice(country_data['states'])

    def generate_country(self) -> str:
        """Generate African country."""
        return random.choice(list(self.african_countries.keys()))

    def generate_date_of_birth(self) -> str:
        """Generate date of birth (18-90 years ago)."""
        days_ago = random.randint(18*365, 90*365)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def generate_admission_date(self) -> str:
        """Generate admission date (recent past)."""
        days_ago = random.randint(1, 365)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def generate_discharge_date(self, admission_date_str: Optional[str] = None) -> str:
        """Generate discharge date (after admission)."""
        if admission_date_str:
            # Parse admission date and add 1-30 days
            try:
                admit_date = datetime.strptime(admission_date_str, "%d/%m/%Y")
                days_stay = random.randint(1, 30)
                discharge_date = admit_date + timedelta(days=days_stay)
            except:
                days_ago = random.randint(1, 335)
                discharge_date = datetime.now() - timedelta(days=days_ago)
        else:
            days_ago = random.randint(1, 335)
            discharge_date = datetime.now() - timedelta(days=days_ago)
        
        return self.format_date(discharge_date)

    def generate_date(self) -> str:
        """Generate general date."""
        days_ago = random.randint(1, 1825)  # Up to 5 years
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def format_date(self, date_obj: datetime) -> str:
        """Format date in common formats."""
        formats = [
            lambda d: d.strftime("%d/%m/%Y"),      # 15/03/2024
            lambda d: d.strftime("%d-%m-%Y"),      # 15-03-2024
            lambda d: d.strftime("%d %B %Y"),      # 15 March 2024
            lambda d: d.strftime("%d %b %Y"),      # 15 Mar 2024
        ]
        return random.choice(formats)(date_obj)

    def generate_phone(self) -> str:
        """Generate African phone number with country code."""
        country_name, country_data = self.get_random_country()
        phone_code = country_data['phone_code']
        
        # Generate local number (different formats)
        if random.random() < 0.5:
            # Format: +234 803 123 4567
            local = f"{random.randint(700, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        else:
            # Format: +234-803-123-4567
            local = f"{random.randint(700, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        if random.random() < 0.7:
            return f"{phone_code} {local}"
        else:
            return f"{phone_code}{local.replace(' ', '').replace('-', '')}"

    def generate_entities_for_record(self) -> Dict[str, List[str]]:
        """Generate entities based on configuration."""
        entities_dict = defaultdict(list)
        
        # Always include essential entities
        if self.entity_config["PERSON"]["enabled"]:
            entities_dict["PERSON"].append(self.generate_person())
        
        # Generate dates
        admission_date = None
        if self.entity_config["ADMISSION_DATE"]["enabled"] and random.random() < self.entity_config["ADMISSION_DATE"]["probability"]:
            admission_date = self.generate_admission_date()
            entities_dict["ADMISSION_DATE"].append(admission_date)
        
        if self.entity_config["DISCHARGE_DATE"]["enabled"] and random.random() < self.entity_config["DISCHARGE_DATE"]["probability"]:
            discharge_date = self.generate_discharge_date(admission_date)
            entities_dict["DISCHARGE_DATE"].append(discharge_date)
        
        if self.entity_config["DATE_OF_BIRTH"]["enabled"] and random.random() < self.entity_config["DATE_OF_BIRTH"]["probability"]:
            entities_dict["DATE_OF_BIRTH"].append(self.generate_date_of_birth())
        
        if self.entity_config["DATE"]["enabled"] and random.random() < self.entity_config["DATE"]["probability"]:
            entities_dict["DATE"].append(self.generate_date())
        
        # Generate location entities
        if self.entity_config["ADDRESS"]["enabled"] and random.random() < self.entity_config["ADDRESS"]["probability"]:
            entities_dict["ADDRESS"].append(self.generate_address())
        
        if self.entity_config["CITY"]["enabled"] and random.random() < self.entity_config["CITY"]["probability"]:
            entities_dict["CITY"].append(self.generate_city())
        
        if self.entity_config["STATE"]["enabled"] and random.random() < self.entity_config["STATE"]["probability"]:
            entities_dict["STATE"].append(self.generate_state())
        
        if self.entity_config["COUNTRY"]["enabled"] and random.random() < self.entity_config["COUNTRY"]["probability"]:
            entities_dict["COUNTRY"].append(self.generate_country())
        
        # Generate phone
        if self.entity_config["PHONE"]["enabled"] and random.random() < self.entity_config["PHONE"]["probability"]:
            entities_dict["PHONE"].append(self.generate_phone())
        
        return entities_dict

    def create_short_sentences(self, entities_dict: Dict[str, List[str]]) -> str:
        """Create short, focused sentences with PHI."""
        sentences = []
        
        # Person introduction
        if "PERSON" in entities_dict:
            person = entities_dict["PERSON"][0]
            sentences.append(f"Patient name is {person}.")
            
            # Add DOB if available
            if "DATE_OF_BIRTH" in entities_dict:
                dob = entities_dict["DATE_OF_BIRTH"][0]
                sentences.append(f"Born on {dob}.")
        
        # Address information
        if "ADDRESS" in entities_dict:
            address = entities_dict["ADDRESS"][0]
            city = entities_dict.get("CITY", [self.generate_city()])[0]
            sentences.append(f"Resides at {address}, {city}.")
        elif "CITY" in entities_dict:
            city = entities_dict["CITY"][0]
            sentences.append(f"Lives in {city}.")
        
        # State/Country
        if "STATE" in entities_dict and "COUNTRY" in entities_dict:
            state = entities_dict["STATE"][0]
            country = entities_dict["COUNTRY"][0]
            sentences.append(f"From {state}, {country}.")
        elif "COUNTRY" in entities_dict:
            country = entities_dict["COUNTRY"][0]
            sentences.append(f"Country of residence is {country}.")
        
        # Phone contact
        if "PHONE" in entities_dict:
            phone = entities_dict["PHONE"][0]
            sentences.append(f"Contact number: {phone}.")
        
        # Admission information
        if "ADMISSION_DATE" in entities_dict:
            admit = entities_dict["ADMISSION_DATE"][0]
            sentences.append(f"Admitted on {admit}.")
        
        # Discharge information
        if "DISCHARGE_DATE" in entities_dict:
            discharge = entities_dict["DISCHARGE_DATE"][0]
            sentences.append(f"Discharged on {discharge}.")
        
        # General date if present
        if "DATE" in entities_dict and "ADMISSION_DATE" not in entities_dict:
            date = entities_dict["DATE"][0]
            actions = ["Visited clinic", "Consulted", "Examined", "Treated"]
            sentences.append(f"{random.choice(actions)} on {date}.")
        
        # Shuffle for variety
        random.shuffle(sentences)
        
        return " ".join(sentences)

    def add_entity(
        self,
        text: str,
        substring: str,
        label: str,
        entities_list: List[Dict],
        start_offset: int = 0
    ) -> bool:
        """Find substring in text and add entity annotation."""
        idx = text.find(substring, start_offset)
        if idx == -1:
            return False
        
        start = idx
        end = idx + len(substring)
        
        # Check for overlap
        for existing in entities_list:
            if not (end <= existing["start"] or start >= existing["end"]):
                return False
        
        entities_list.append({
            "start": start,
            "end": end,
            "label": label
        })
        
        return True

    def build_record(self, record_id: str) -> Dict:
        """Build a complete annotated record with short sentences."""
        # Generate entities
        entities_dict = self.generate_entities_for_record()
        
        # Create short text
        text = self.create_short_sentences(entities_dict)
        
        # Annotate entities
        entities_list = []
        
        label_map = {
            "PERSON": "PERSON",
            "DATE_OF_BIRTH": "DATE_OF_BIRTH",
            "ADMISSION_DATE": "ADMISSION_DATE",
            "DISCHARGE_DATE": "DISCHARGE_DATE",
            "DATE": "DATE",
            "ADDRESS": "ADDRESS",
            "CITY": "CITY",
            "STATE": "STATE",
            "COUNTRY": "COUNTRY",
            "PHONE": "PHONE"
        }
        
        for entity_type, values in entities_dict.items():
            if entity_type in label_map:
                for value in values:
                    self.add_entity(text, value, label_map[entity_type], entities_list)
        
        # Sort entities by start position
        entities_list.sort(key=lambda x: x["start"])
        
        return {
            "id": record_id,
            "text": text,
            "entities": entities_list,
            "source": "synthetic",
            "region": "africa",
            "lang": "en"
        }

    def generate_dataset(self, n_records: int, verbose: bool = False) -> List[Dict]:
        """Generate complete dataset."""
        dataset = []
        
        for i in range(n_records):
            if verbose and (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{n_records} records...")
            
            record_id = f"african_phi_{uuid.uuid4().hex[:12]}"
            record = self.build_record(record_id)
            dataset.append(record)
        
        if verbose:
            print(f"✓ Generated {n_records} records")
        
        return dataset

    def write_jsonl(self, dataset: List[Dict], output_path: str) -> None:
        """Write dataset to JSONL file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for record in dataset:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"✓ Dataset written to {output_path}")

    def generate_frequency_report(self, dataset: List[Dict]) -> Dict:
        """Generate statistics report."""
        label_counts = Counter()
        total_entities = 0
        
        for record in dataset:
            for ent in record["entities"]:
                label_counts[ent["label"]] += 1
                total_entities += 1
        
        return {
            "total_records": len(dataset),
            "total_entities": total_entities,
            "avg_entities_per_record": total_entities / len(dataset) if dataset else 0,
            "label_distribution": dict(label_counts)
        }


def print_sample_record(record: Dict) -> None:
    """Pretty print a sample record."""
    print(f"\n{'='*80}")
    print(f"ID: {record['id']}")
    print(f"{'='*80}")
    print(f"\nTEXT:\n{record['text']}\n")
    print(f"ENTITIES ({len(record['entities'])}):")
    for ent in record['entities']:
        entity_text = record['text'][ent['start']:ent['end']]
        print(f"  [{ent['start']:4d}-{ent['end']:4d}] {ent['label']:20s} → \"{entity_text}\"")


def main():
    """Main execution."""
    print("=" * 80)
    print("AFRICAN PHI DATA GENERATOR")
    print("Short Sentences | African Data")
    print("=" * 80)
    
    # Initialize generator
    generator = AfricanPHIGenerator(
        config_path="phi_config.json",
        seed=42
    )
    
    # Generate sample dataset
    print("\n[1] Generating sample dataset (100 records)...")
    sample_dataset = generator.generate_dataset(n_records=100, verbose=True)
    
    # Write sample
    generator.write_jsonl(sample_dataset, "african_phi_sample.jsonl")
    
    # Show examples
    print("\n[2] Sample records:")
    for i in range(min(3, len(sample_dataset))):
        print_sample_record(sample_dataset[i])
    
    # Statistics
    print("\n[3] Dataset Statistics:")
    report = generator.generate_frequency_report(sample_dataset)
    print(f"  Total Records: {report['total_records']}")
    print(f"  Total Entities: {report['total_entities']}")
    print(f"  Avg Entities/Record: {report['avg_entities_per_record']:.2f}")
    print(f"\n  Label Distribution:")
    for label, count in sorted(report['label_distribution'].items(), key=lambda x: -x[1]):
        pct = 100 * count / report['total_entities']
        print(f"    {label:20s}: {count:4d} ({pct:5.2f}%)")
    
    # Generate larger dataset
    print("\n[4] Generating full dataset (1,000 records)...")
    full_dataset = generator.generate_dataset(n_records=1000, verbose=True)
    generator.write_jsonl(full_dataset, "african_phi_full.jsonl")
    
    # Split dataset
    print("\n[5] Creating train/dev/test splits...")
    random.shuffle(full_dataset)
    
    train_size = int(0.8 * len(full_dataset))
    dev_size = int(0.1 * len(full_dataset))
    
    train = full_dataset[:train_size]
    dev = full_dataset[train_size:train_size+dev_size]
    test = full_dataset[train_size+dev_size:]
    
    generator.write_jsonl(train, "african_phi_train.jsonl")
    generator.write_jsonl(dev, "african_phi_dev.jsonl")
    generator.write_jsonl(test, "african_phi_test.jsonl")
    
    print(f"  Train: {len(train)} records")
    print(f"  Dev:   {len(dev)} records")
    print(f"  Test:  {len(test)} records")
    
    print("\n" + "=" * 80)
    print("✓ GENERATION COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  • african_phi_sample.jsonl (100 records)")
    print("  • african_phi_train.jsonl (800 records)")
    print("  • african_phi_dev.jsonl (100 records)")
    print("  • african_phi_test.jsonl (100 records)")
    print("  • african_phi_full.jsonl (1,000 records)")
    print("\nReady for African PHI detection model training!")


if __name__ == "__main__":
    main()
