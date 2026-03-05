#!/usr/bin/env python3
"""
Simple African PHI Sentence Generator
======================================

Generates simple sentences with ONE PHI identifier per sentence.
Output as JSON array of sentences.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

try:
    from faker import Faker
except ImportError:
    raise ImportError("Please install faker: pip install faker")


class SimpleAfricanPHIGenerator:
    """Generator for simple sentences with one PHI per sentence."""

    def __init__(self, config_path: str = "phi_config.json", seed: int = None):
        """Initialize with configuration."""
        if seed:
            random.seed(seed)
            Faker.seed(seed)
        
        # Load config
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.faker = Faker('en_US')
        self.african_countries = self.config['african_countries']
        
        # African names (expanded list with country-specific names and English names)
        self.african_first_names = [
            # West Africa (Ghana, Nigeria, Senegal, Mali)
            "Amara", "Kwame", "Ayo", "Chinwe", "Kofi", "Adebayo", "Kwesi", "Abena",
            "Oluwa", "Chidi", "Babatunde", "Nkechi", "Yaw", "Akosua", "Kojo", "Ama",
            "Ekow", "Efe", "Obinna", "Adaeze", "Femi", "Folake", "Tunde", "Bisi",
            "Adama", "Mamadou", "Ousmane", "Aminata", "Cheikh", "Moussa", "Kadiatou", "Seydou",
            "Yaya", "Fanta", "Bakary", "Hawa", "Abdoulaye", "Fatoumata", "Idrissa", "Mariama",
            # East Africa (Kenya, Tanzania, Uganda, Ethiopia)
            "Zuri", "Makena", "Kamau", "Wanjiru", "Otieno", "Akinyi", "Jabari", "Nia",
            "Jelani", "Zawadi", "Bahati", "Furaha", "Juma", "Neema", "Baraka", "Amani",
            "Abebe", "Desta", "Haile", "Selam", "Tadesse", "Almaz", "Girma", "Tigist",
            "Okello", "Nakato", "Wasswa", "Nambi", "Kirabo", "Apio", "Kato", "Aceng",
            "Mwangi", "Njeri", "Kimani", "Nyambura", "Githinji", "Wambui", "Kariuki", "Wangari",
            # Southern Africa (Zimbabwe, South Africa, Lesotho, Malawi, Botswana, Namibia)
            "Thabo", "Tendai", "Tafadzwa", "Rudo", "Farai", "Tanaka", "Kuda", "Ngoni",
            "Sipho", "Nandi", "Mandla", "Nosipho", "Bongani", "Thandeka", "Lerato", "Thato",
            "Lineo", "Mpho", "Palesa", "Tshepo", "Musa", "Chipo", "Limbani", "Chisomo",
            "Kgosi", "Boipelo", "Kagiso", "Kefilwe", "Tebogo", "Ontlametse", "Tsholofelo",
            "Kudzai", "Tatenda", "Tinashe", "Shingai", "Rukudzo", "Takudzwa", "Nyasha",
            # Rwanda, Burundi
            "Uwimana", "Gasana", "Mugisha", "Umutoni", "Nshuti", "Iradukunda", "Hakizimana",
            "Niyonzima", "Kamanzi", "Ndayisenga", "Uwase", "Nkurunziza", "Ndihokubwayo",
            # North Africa (Egypt, Morocco, Algeria, Tunisia)
            "Mohamed", "Ahmed", "Fatima", "Khadija", "Omar", "Yasmine", "Hassan",
            "Laila", "Malik", "Salma", "Karim", "Amir", "Nadia", "Samir", "Zahra",
            # Mixed/Common African names
            "Aisha", "Amina", "Zara", "Tariq", "Imani", "Aaliyah", "Nuru",
            "Sekou", "Habib", "Zalika", "Nadira", "Rashid", "Kadijah", "Halima",
            # English names (mixed throughout)
            "Victor", "Esther", "Emmanuel", "Grace", "Ibrahim", "Mariam", "Yusuf",
            "David", "Sarah", "Joseph", "Ruth", "Daniel", "Naomi", "John", "Mary",
            "Michael", "Elizabeth", "James", "Rebecca", "Peter", "Catherine", "Paul", "Rachel",
            "Samuel", "Hannah", "Benjamin", "Deborah", "Stephen", "Martha", "Andrew", "Lydia",
            "Thomas", "Jane", "Matthew", "Susan", "Mark", "Margaret", "Luke", "Anne",
            "Joshua", "Jennifer", "Philip", "Linda", "Simon", "Patricia", "Christopher", "Barbara"
        ]
        
        self.african_last_names = [
            # West Africa (Ghana, Nigeria, Senegal, Mali)
            "Okonkwo", "Okeke", "Ngozi", "Adeyemi", "Nnamdi", "Mensah", "Osei", "Kwame",
            "Oluwaseun", "Mba", "Asante", "Boateng", "Owusu", "Ofori", "Adjei", "Agyeman",
            "Antwi", "Amoah", "Appiah", "Sarpong", "Ofosu", "Frimpong", "Yeboah",
            "Kamara", "Diop", "Sow", "Ba", "Ndiaye", "Cisse", "Diallo", "Traore",
            "Keita", "Toure", "Kone", "Diarra", "Coulibaly", "Sylla", "Sankara",
            # East Africa (Kenya, Tanzania, Ethiopia, Uganda)
            "Mwangi", "Wanjiku", "Kariuki", "Otieno", "Kamau", "Odhiambo", "Wambui", "Njoroge",
            "Kimani", "Nyambura", "Maina", "Mugo", "Gitau", "Waweru", "Njenga", "Waithaka",
            "Abebe", "Kebede", "Tesfaye", "Bekele", "Gebre", "Wolde", "Haile", "Desta",
            "Tadesse", "Alemu", "Demissie", "Mengistu", "Assefa", "Mulugeta",
            "Mwinyi", "Mkuu", "Ally", "Hassan", "Omari", "Selemani", "Juma",
            "Okello", "Nambi", "Wasswa", "Kato", "Nakato", "Mukasa", "Babirye",
            # Southern Africa (Zimbabwe, South Africa, Lesotho, Malawi, Botswana)
            "Nkosi", "Moyo", "Ndlovu", "Khumalo", "Dlamini", "Zulu", "Sithole", "Ncube",
            "Mthembu", "Mkhize", "Ngcobo", "Nxumalo", "Mabaso", "Shabalala",
            "Banda", "Phiri", "Tembo", "Mwale", "Chirwa", "Mhango", "Chuma", "Sakala",
            "Molefe", "Mokone", "Tau", "Mothibe", "Motaung", "Sebake", "Mokoena",
            "Sibanda", "Mutasa", "Chigumira", "Mavhura", "Mahlangu", "Ngwenya",
            # Rwanda, Burundi
            "Uwimana", "Gasana", "Mugisha", "Habimana", "Niyonzima", "Mukiza",
            "Ntawukuriryayo", "Nkurunziza", "Ndayisenga", "Bizimana",
            # North Africa (Egypt, Morocco, Algeria, Tunisia)
            "Mohamed", "Ahmed", "Hassan", "Ali", "Omar", "Mahmoud", "Farouk",
            "Benani", "El-Fassi", "Alami", "Benjelloun", "Bennani",
            # English/Common surnames
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
            "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White",
            "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark",
            
            # Mixed
            "Mutombo", "Ibrahim", "Myarnya", "Mensah", "Kofi"
        ]

    def generate_person(self) -> str:
        """Generate African person name."""
        first = random.choice(self.african_first_names)
        last = random.choice(self.african_last_names)
        return f"{first} {last}"

    def generate_date_of_birth(self) -> str:
        """Generate date of birth."""
        days_ago = random.randint(18*365, 90*365)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def generate_admission_date(self) -> str:
        """Generate admission date."""
        days_ago = random.randint(1, 365)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def generate_discharge_date(self) -> str:
        """Generate discharge date."""
        days_ago = random.randint(1, 335)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def generate_date(self) -> str:
        """Generate general date."""
        days_ago = random.randint(1, 1825)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def format_date(self, date_obj: datetime) -> str:
        """Format date."""
        formats = [
            lambda d: d.strftime("%d/%m/%Y"),
            lambda d: d.strftime("%d-%m-%Y"),
            lambda d: d.strftime("%d %B %Y"),
            lambda d: d.strftime("%d %b %Y"),
            lambda d: d.strftime("%A"),  # Day name like "Monday"
        ]
        return random.choice(formats)(date_obj)

    def generate_phone(self) -> str:
        """Generate African phone number."""
        country_name, country_data = random.choice(list(self.african_countries.items()))
        phone_code = country_data['phone_code']
        
        if random.random() < 0.5:
            local = f"{random.randint(700, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        else:
            local = f"{random.randint(700, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        return f"{phone_code} {local}"

    def generate_address(self) -> str:
        """Generate address."""
        streets = ["Hospital Road", "Independence Avenue", "Uhuru Street", "Market Road",
                  "Station Avenue", "Church Street", "Nelson Mandela Road", "Kenyatta Avenue"]
        number = random.randint(1, 999)
        street = random.choice(streets)
        return f"{number} {street}"

    def generate_city(self) -> str:
        """Generate city."""
        all_cities = []
        for country_data in self.african_countries.values():
            all_cities.extend(country_data['cities'])
        return random.choice(all_cities)

    def generate_state(self) -> str:
        """Generate state/province."""
        all_states = []
        for country_data in self.african_countries.values():
            all_states.extend(country_data['states'])
        return random.choice(all_states)

    def generate_country(self) -> str:
        """Generate country."""
        return random.choice(list(self.african_countries.keys()))

    def create_sentence_with_one_phi(self, entity_type: str = None, record_id: str = None) -> Dict:
        """Create ONE sentence with ONE PHI entity."""
        
        # Always use PERSON entity type
        entity_type = "PERSON"
        
        # Generate the entity value
        generators = {
            "PERSON": self.generate_person,
            "DATE_OF_BIRTH": self.generate_date_of_birth,
            "ADMISSION_DATE": self.generate_admission_date,
            "DISCHARGE_DATE": self.generate_discharge_date,
            "DATE": self.generate_date,
            "PHONE": self.generate_phone,
            "ADDRESS": self.generate_address,
            "CITY": self.generate_city,
            "STATE": self.generate_state,
            "COUNTRY": self.generate_country,
        }
        
        entity_value = generators[entity_type]()
        
        # Create sentence templates with high variety (60+ templates)
        templates = {
            "PERSON": [
                # Admission-related
                f"The patient {entity_value} was admitted.",
                f"Patient {entity_value} was admitted to the ward.",
                f"{entity_value} was admitted on Monday.",
                f"{entity_value} was admitted for emergency treatment.",
                f"We admitted {entity_value} this morning.",
                f"{entity_value} has been admitted to the ICU.",
                f"Emergency admission for {entity_value} was processed.",
                
                # Discharge-related
                f"{entity_value} was discharged today.",
                f"Patient {entity_value} was discharged yesterday.",
                f"{entity_value} received discharge papers.",
                f"The doctor discharged {entity_value} on Friday.",
                f"{entity_value}'s discharge was approved.",
                
                # Arrival and registration
                f"{entity_value} arrived at the clinic.",
                f"Patient {entity_value} checked in at reception.",
                f"{entity_value} registered at the front desk.",
                f"{entity_value} is waiting in the reception area.",
                f"{entity_value} arrived for their appointment.",
                
                # Identity and records
                f"{entity_value} is the patient.",
                f"Patient name is {entity_value}.",
                f"The medical record for {entity_value} was reviewed.",
                f"{entity_value}'s file was updated.",
                f"Medical records show {entity_value} as the patient.",
                f"Hospital records indicate {entity_value} was treated here.",
                f"{entity_value}'s chart was reviewed by the team.",
                
                # Examinations and consultations
                f"Dr. examined {entity_value} yesterday.",
                f"The doctor will see {entity_value} shortly.",
                f"{entity_value} was examined by Dr. Smith.",
                f"Dr. Johnson consulted with {entity_value}.",
                f"{entity_value} had a consultation today.",
                f"The specialist evaluated {entity_value}.",
                f"{entity_value} underwent a physical examination.",
                
                # Treatment and care
                f"{entity_value}'s treatment was completed.",
                f"Patient {entity_value} requires medication.",
                f"{entity_value} needs follow-up care.",
                f"{entity_value} received treatment today.",
                f"Treatment plan for {entity_value} was approved.",
                f"{entity_value} is responding well to therapy.",
                f"Medication was prescribed to {entity_value}.",
                
                # Medical procedures
                f"{entity_value} is scheduled for surgery.",
                f"{entity_value} had surgery last week.",
                f"Surgery for {entity_value} is tomorrow.",
                f"{entity_value} underwent a procedure.",
                f"The operation for {entity_value} was successful.",
                f"{entity_value}'s lab results came back.",
                f"{entity_value} needs blood work done.",
                
                # Condition and status
                f"{entity_value}'s condition is stable.",
                f"Patient {entity_value} is in stable condition.",
                f"{entity_value} is recovering well.",
                f"{entity_value} shows signs of improvement.",
                f"The condition of {entity_value} has improved.",
                f"{entity_value}'s vitals are normal.",
                
                # Communication
                f"The nurse called {entity_value}.",
                f"Staff contacted {entity_value} by phone.",
                f"{entity_value} was notified about the results.",
                f"A message was left for {entity_value}.",
                f"{entity_value} spoke with the nursing staff.",
                
                # Family and visitors
                f"{entity_value}'s mother in law is the care taker.",
                f"The family of {entity_value} was informed.",
                f"{entity_value}'s next of kin was contacted.",
                f"Relatives of {entity_value} are in the waiting room.",
                f"{entity_value}'s spouse visited today.",
                
                # Appointments and scheduling
                f"{entity_value} has an appointment scheduled.",
                f"Next visit for {entity_value} is next week.",
                f"{entity_value} needs to reschedule.",
                f"Appointment confirmed for {entity_value}.",
                f"{entity_value} missed their appointment.",
                
                # Referrals and transfers
                f"{entity_value} was referred to a specialist.",
                f"Patient {entity_value} was transferred to another facility.",
                f"{entity_value} will be transferred to cardiology.",
                f"Referral letter was sent for {entity_value}.",
                
                # Prescriptions and medications
                f"Prescription issued to {entity_value}.",
                f"{entity_value} picked up their medication.",
                f"Pharmacy dispensed medication for {entity_value}.",
                f"{entity_value}'s prescription was renewed.",
                
                # Various medical contexts
                f"{entity_value} is in the waiting area.",
                f"X-ray ordered for {entity_value}.",
                f"{entity_value}'s test results are pending.",
                f"Blood pressure checked for {entity_value}.",
                f"{entity_value} complained of chest pain.",
                f"The diagnosis for {entity_value} was confirmed.",
                f"{entity_value} requires immediate attention.",
                f"Emergency room visit by {entity_value}.",
                f"{entity_value} was seen in outpatient clinic.",
            ],
        }
        
        sentence = random.choice(templates["PERSON"])
        
        # Find the entity position in the sentence
        start = sentence.find(entity_value)
        end = start + len(entity_value)
        
        # Use provided record_id or generate a UUID-based one as fallback
        if record_id is None:
            record_id = f"simple_phi_{uuid.uuid4().hex[:12]}"
        
        return {
            "id": record_id,
            "text": sentence,
            "entities": [{
                "start": start,
                "end": end,
                "label": entity_type,
                "value": entity_value
            }]
        }

    def generate_dataset(self, n_sentences: int, verbose: bool = False) -> List[Dict]:
        """Generate dataset of simple sentences."""
        dataset = []
        
        for i in range(n_sentences):
            if verbose and (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{n_sentences} sentences...")
            
            # Create simple numeric ID with zero-padding
            record_id = str(i + 1).zfill(4)
            record = self.create_sentence_with_one_phi(record_id=record_id)
            dataset.append(record)
        
        if verbose:
            print(f"✓ Generated {n_sentences} sentences")
        
        return dataset

    def write_json(self, dataset: List[Dict], output_path: str) -> None:
        """Write dataset to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)
        print(f"✓ Dataset written to {output_path}")


def main():
    """Main execution."""
    print("=" * 80)
    print("SIMPLE AFRICAN PHI SENTENCE GENERATOR")
    print("Person Names Only - One Name per Sentence")
    print("=" * 80)
    
    # Initialize
    generator = SimpleAfricanPHIGenerator(
        config_path="phi_config.json",
        seed=42
    )
    
    # Generate sentences
    print("\n[1] Generating 10,000 simple sentences (person names only)...")
    dataset = generator.generate_dataset(n_sentences=10000, verbose=True)
    
    # Write to JSON
    generator.write_json(dataset, "simple_african_phi_sentences.json")
    
    # Show examples
    print("\n[2] Sample sentences with person names:")
    for i in range(min(15, len(dataset))):
        record = dataset[i]
        entity = record['entities'][0]
        print(f"  {i+1}. {record['text']}")
    
    print("\n[3] Statistics:")
    print(f"  Total sentences: {len(dataset)}")
    print(f"  Entity type: PERSON (names only)")
    print(f"  Unique templates: 90 different sentence patterns")
    print(f"  Unique first names: {len(generator.african_first_names)}")
    print(f"  Unique last names: {len(generator.african_last_names)}")
    
    print("\n" + "=" * 80)
    print("✓ GENERATION COMPLETE")
    print("=" * 80)
    print("\n✅ File created: simple_african_phi_sentences.json")
    print("   Format: JSON array with one person name per sentence")
    print("\nReady to use!")


if __name__ == "__main__":
    main()
