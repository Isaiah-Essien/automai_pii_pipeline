#!/usr/bin/env python3
"""
Synthetic HIPAA-aligned PHI Data Generator
==========================================

Generates realistic medical narrative text with annotated PHI entities
for training PHI detection models.

Follows HIPAA Safe Harbor guidelines and canonical semantic label schema.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
import re

try:
    from faker import Faker
except ImportError:
    raise ImportError(
        "Please install faker: pip install faker"
    )


# Canonical Semantic Label Schema (26 labels)
LABEL_SCHEMA = [
    "PERSON",
    "RELATIVE",
    "CAREGIVER",
    "PROVIDER",
    "LOCATION",
    "ADDRESS",
    "ZIP",
    "FACILITY",
    "ORGANIZATION",
    "DATE",
    "AGE",
    "PHONE",
    "FAX",
    "EMAIL",
    "URL",
    "IP",
    "ID_MEDICAL",
    "ID_INSURANCE",
    "ID_ACCOUNT",
    "ID_LICENSE",
    "ID_DEVICE",
    "ID_VEHICLE",
    "ID_OTHER",
    "BIOMETRIC",
    "IMAGE_REF",
    "OTHER_UNIQUE",
]


class SyntheticPHIGenerator:
    """
    Production-ready generator for synthetic HIPAA-aligned PHI data.
    
    Architecture follows Detect-Map-Act philosophy:
    - Detection: Entity generation with proper semantic labels
    - Mapping: Regulatory alignment with HIPAA Safe Harbor
    - Act: Audit-ready output with validation
    """

    def __init__(
        self,
        seed: Optional[int] = None,
        locale: str = "en_US",
        min_entities_per_record: int = 5,
        max_entities_per_record: int = 15,
        include_long_tail_identifiers: bool = True,
    ):
        """Initialize the generator with configuration."""
        if seed:
            random.seed(seed)
            Faker.seed(seed)
        
        self.faker = Faker(locale)
        self.min_entities = min_entities_per_record
        self.max_entities = max_entities_per_record
        self.include_long_tail = include_long_tail_identifiers
        
        # Entity probabilities (adjust for coverage)
        self.entity_probabilities = {
            "PERSON": 0.9,
            "RELATIVE": 0.3,
            "CAREGIVER": 0.2,
            "PROVIDER": 0.7,
            "LOCATION": 0.4,
            "ADDRESS": 0.5,
            "ZIP": 0.4,
            "FACILITY": 0.8,
            "ORGANIZATION": 0.3,
            "DATE": 0.9,
            "AGE": 0.6,
            "PHONE": 0.6,
            "FAX": 0.2,
            "EMAIL": 0.4,
            "URL": 0.2,
            "IP": 0.1,
            "ID_MEDICAL": 0.8,
            "ID_INSURANCE": 0.5,
            "ID_ACCOUNT": 0.3,
            "ID_LICENSE": 0.2,
            "ID_DEVICE": 0.25,
            "ID_VEHICLE": 0.15,
            "ID_OTHER": 0.3,
            "BIOMETRIC": 0.1,
            "IMAGE_REF": 0.15,
            "OTHER_UNIQUE": 0.2,
        }
        
        # Medical note templates
        self.note_templates = [
            self._template_admission_note,
            self._template_discharge_summary,
            self._template_clinical_observation,
            self._template_emergency_report,
            self._template_lab_report,
            self._template_referral_letter,
            self._template_progress_note,
            self._template_consultation_note,
        ]
        
        # Medical specialties and departments
        self.departments = [
            "Cardiology", "Emergency Department", "Internal Medicine",
            "Pediatrics", "Surgery", "Oncology", "Neurology",
            "Orthopedics", "Radiology", "Psychiatry"
        ]
        
        # Medical conditions
        self.conditions = [
            "hypertension", "diabetes mellitus", "coronary artery disease",
            "chronic kidney disease", "COPD", "atrial fibrillation",
            "heart failure", "pneumonia", "sepsis", "acute myocardial infarction"
        ]

    # =======================================================================
    # ENTITY GENERATORS (one per HIPAA category)
    # =======================================================================

    def generate_person(self) -> str:
        """Generate person name."""
        return self.faker.name()

    def generate_relative(self) -> Tuple[str, str]:
        """Generate relative name with relationship."""
        relationships = ["son", "daughter", "spouse", "mother", "father", "brother", "sister"]
        name = self.faker.name()
        rel = random.choice(relationships)
        return name, rel

    def generate_caregiver(self) -> str:
        """Generate caregiver name."""
        return self.faker.name()

    def generate_provider(self) -> str:
        """Generate healthcare provider name."""
        titles = ["Dr.", "Nurse", "PA", "NP"]
        return f"{random.choice(titles)} {self.faker.last_name()}"

    def generate_location(self) -> str:
        """Generate location (city/county)."""
        return self.faker.city()

    def generate_address(self) -> str:
        """Generate street address."""
        return self.faker.street_address()

    def generate_zip(self) -> str:
        """Generate ZIP code."""
        return self.faker.zipcode()

    def generate_facility(self) -> str:
        """Generate healthcare facility name."""
        types = ["Medical Center", "Hospital", "Clinic", "Health System", "Regional Hospital"]
        return f"{self.faker.city()} {random.choice(types)}"

    def generate_organization(self) -> str:
        """Generate organization name."""
        return self.faker.company()

    def generate_date(self) -> str:
        """Generate date (various formats)."""
        date_obj = self.faker.date_between(start_date="-5y", end_date="today")
        formats = [
            lambda d: d.strftime("%B %d, %Y"),
            lambda d: d.strftime("%m/%d/%Y"),
            lambda d: d.strftime("%Y-%m-%d"),
            lambda d: d.strftime("%b %d, %Y"),
        ]
        return random.choice(formats)(date_obj)

    def generate_age(self) -> str:
        """Generate age (occasionally >89 for HIPAA edge case)."""
        if random.random() < 0.05:  # 5% chance of >89
            age = random.randint(90, 105)
        else:
            age = random.randint(18, 89)
        return f"{age} years old" if random.random() < 0.5 else str(age)

    def generate_phone(self) -> str:
        """Generate phone number."""
        formats = [
            lambda: self.faker.phone_number(),
            lambda: f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}",
            lambda: f"{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}",
        ]
        return random.choice(formats)()

    def generate_fax(self) -> str:
        """Generate fax number."""
        return f"Fax: ({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"

    def generate_email(self) -> str:
        """Generate email address."""
        return self.faker.email()

    def generate_url(self) -> str:
        """Generate URL."""
        domains = ["patientportal.com", "healthsystem.org", "medicalcenter.net"]
        return f"https://{random.choice(domains)}/{self.faker.user_name()}"

    def generate_ip(self) -> str:
        """Generate IP address."""
        return self.faker.ipv4()

    def generate_medical_id(self) -> str:
        """Generate medical record number (MRN)."""
        return f"MRN {random.randint(1000000, 9999999)}"

    def generate_insurance_id(self) -> str:
        """Generate health insurance ID."""
        prefix = random.choice(["INS", "MBI", "POL"])
        return f"{prefix}{random.randint(100000000, 999999999)}"

    def generate_account_id(self) -> str:
        """Generate account number."""
        return f"Account #{random.randint(100000, 999999)}"

    def generate_license_id(self) -> str:
        """Generate license/certificate number."""
        state = random.choice(["CA", "NY", "TX", "FL", "IL"])
        return f"License {state}{random.randint(1000000, 9999999)}"

    def generate_device_id(self) -> str:
        """Generate medical device identifier."""
        types = ["pacemaker", "insulin pump", "ventilator", "monitor"]
        return f"{random.choice(types)} serial #{random.randint(100000, 999999)}"

    def generate_vehicle_id(self) -> str:
        """Generate vehicle identifier/plate."""
        state = random.choice(["CA", "NY", "TX", "FL", "IL"])
        plate = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7))
        return f"{state} plate {plate}"

    def generate_ssn_style_id(self) -> str:
        """Generate SSN-style identifier (ID_OTHER per HIPAA)."""
        return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"

    def generate_biometric(self) -> str:
        """Generate biometric identifier reference."""
        types = ["fingerprint", "retinal scan", "voice print", "facial recognition"]
        return f"{random.choice(types)} ID {random.randint(10000, 99999)}"

    def generate_image_ref(self) -> str:
        """Generate photographic image reference."""
        return f"image_{random.randint(1000, 9999)}.jpg"

    def generate_other_unique(self) -> str:
        """Generate other unique identifier."""
        types = ["badge", "employee ID", "case", "study"]
        return f"{random.choice(types)} #{random.randint(10000, 99999)}"

    # =======================================================================
    # MEDICAL NOTE TEMPLATES
    # =======================================================================

    def _template_admission_note(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate admission note template."""
        person = entities_dict.get("PERSON", ["John Doe"])[0]
        age = entities_dict.get("AGE", ["45"])[0]
        date = entities_dict.get("DATE", ["January 1, 2024"])[0]
        facility = entities_dict.get("FACILITY", ["General Hospital"])[0]
        mrn = entities_dict.get("ID_MEDICAL", ["MRN 1234567"])[0]
        provider = entities_dict.get("PROVIDER", ["Dr. Smith"])[0]
        condition = random.choice(self.conditions)
        
        template = f"""ADMISSION NOTE

Patient {person}, {age}, was admitted on {date} to {facility}. {mrn} was verified upon arrival. 

Chief Complaint: {condition.title()}

History of Present Illness:
The patient presented to the emergency department with symptoms consistent with {condition}. Initial evaluation performed by {provider}."""
        
        return template

    def _template_discharge_summary(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate discharge summary template."""
        person = entities_dict.get("PERSON", ["Jane Smith"])[0]
        admit_date = entities_dict.get("DATE", ["March 1, 2024"])[0]
        facility = entities_dict.get("FACILITY", ["City Hospital"])[0]
        provider = entities_dict.get("PROVIDER", ["Dr. Johnson"])[0]
        
        template = f"""DISCHARGE SUMMARY

Patient Name: {person}
Admitting Facility: {facility}
Admission Date: {admit_date}
Attending Physician: {provider}

The patient was admitted for evaluation and treatment. Hospital course was unremarkable. Patient discharged in stable condition with follow-up instructions."""
        
        return template

    def _template_clinical_observation(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate clinical observation note."""
        person = entities_dict.get("PERSON", ["Michael Jones"])[0]
        date = entities_dict.get("DATE", ["February 15, 2024"])[0]
        provider = entities_dict.get("PROVIDER", ["Nurse Williams"])[0]
        
        template = f"""CLINICAL OBSERVATION NOTE

Date: {date}
Patient: {person}
Observer: {provider}

Patient observed during routine rounds. Vital signs stable. No acute distress noted. Continue current treatment plan."""
        
        return template

    def _template_emergency_report(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate emergency department report."""
        person = entities_dict.get("PERSON", ["Sarah Brown"])[0]
        date = entities_dict.get("DATE", ["April 20, 2024"])[0]
        facility = entities_dict.get("FACILITY", ["Memorial Hospital"])[0]
        phone = entities_dict.get("PHONE", ["555-1234"])[0]
        
        template = f"""EMERGENCY DEPARTMENT REPORT

Patient {person} arrived at {facility} emergency department on {date}. 

Emergency contact: {phone}

Patient presented with acute symptoms requiring immediate evaluation. Stabilized and admitted for further observation."""
        
        return template

    def _template_lab_report(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate laboratory report."""
        person = entities_dict.get("PERSON", ["Robert Wilson"])[0]
        date = entities_dict.get("DATE", ["May 10, 2024"])[0]
        mrn = entities_dict.get("ID_MEDICAL", ["MRN 7654321"])[0]
        facility = entities_dict.get("FACILITY", ["Central Lab"])[0]
        
        template = f"""LABORATORY REPORT

Patient: {person}
{mrn}
Collection Date: {date}
Location: {facility}

Test results within normal limits. No immediate intervention required."""
        
        return template

    def _template_referral_letter(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate referral letter."""
        person = entities_dict.get("PERSON", ["Emily Davis"])[0]
        from_provider = entities_dict.get("PROVIDER", ["Dr. Anderson"])[0]
        date = entities_dict.get("DATE", ["June 5, 2024"])[0]
        address = entities_dict.get("ADDRESS", ["123 Main St"])[0]
        
        template = f"""REFERRAL LETTER

Date: {date}
From: {from_provider}

RE: Patient {person}
Address: {address}

I am referring this patient for specialized consultation. Please see attached medical records for additional information."""
        
        return template

    def _template_progress_note(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate progress note."""
        person = entities_dict.get("PERSON", ["David Martinez"])[0]
        date = entities_dict.get("DATE", ["July 12, 2024"])[0]
        provider = entities_dict.get("PROVIDER", ["Dr. Lee"])[0]
        
        template = f"""PROGRESS NOTE

Patient: {person}
Date: {date}
Provider: {provider}

Assessment: Patient showing improvement with current treatment regimen. Plan: Continue current medications and schedule follow-up."""
        
        return template

    def _template_consultation_note(self, entities_dict: Dict[str, List[str]]) -> str:
        """Generate consultation note."""
        person = entities_dict.get("PERSON", ["Lisa Taylor"])[0]
        date = entities_dict.get("DATE", ["August 8, 2024"])[0]
        provider = entities_dict.get("PROVIDER", ["Dr. Patel"])[0]
        dept = random.choice(self.departments)
        
        template = f"""CONSULTATION NOTE

Patient: {person}
Consultation Date: {date}
Consulting Service: {dept}
Consultant: {provider}

Thank you for this {dept} consultation. Patient evaluated and recommendations provided to primary team."""
        
        return template

    # =======================================================================
    # ENTITY INJECTION & ANNOTATION
    # =======================================================================

    def add_entity(
        self,
        text: str,
        substring: str,
        label: str,
        entities_list: List[Dict],
        start_offset: int = 0
    ) -> bool:
        """
        Find substring in text and add entity annotation.
        
        Args:
            text: Full text to search in
            substring: Entity text to find
            label: Semantic label
            entities_list: List to append entity dict to
            start_offset: Optional offset to start search from
            
        Returns:
            True if entity added, False if not found
        """
        # Find the substring
        idx = text.find(substring, start_offset)
        if idx == -1:
            return False
        
        start = idx
        end = idx + len(substring)
        
        # Validate
        if text[start:end] != substring:
            raise ValueError(f"Offset mismatch: text[{start}:{end}] != '{substring}'")
        
        # Check for overlap
        for existing in entities_list:
            if not (end <= existing["start"] or start >= existing["end"]):
                # Overlapping - skip this entity
                return False
        
        entities_list.append({
            "start": start,
            "end": end,
            "label": label
        })
        
        return True

    def generate_entities_for_record(self) -> Tuple[Dict[str, List[str]], List[str]]:
        """
        Generate random set of entities for one record.
        
        Returns:
            Tuple of (entities_dict, label_list)
        """
        entities_dict = defaultdict(list)
        labels_selected = []
        
        # Determine which entities to include
        num_entities = random.randint(self.min_entities, self.max_entities)
        
        # Always include some core entities
        core_labels = ["PERSON", "DATE", "FACILITY", "PROVIDER", "ID_MEDICAL"]
        for label in core_labels:
            if random.random() < self.entity_probabilities.get(label, 0.5):
                labels_selected.append(label)
        
        # Add random additional entities until we hit target
        available_labels = [l for l in LABEL_SCHEMA if l not in labels_selected]
        while len(labels_selected) < num_entities and available_labels:
            label = random.choice(available_labels)
            available_labels.remove(label)
            if random.random() < self.entity_probabilities.get(label, 0.3):
                labels_selected.append(label)
        
        # Generate entity values
        generator_map = {
            "PERSON": self.generate_person,
            "RELATIVE": lambda: self.generate_relative()[0],
            "CAREGIVER": self.generate_caregiver,
            "PROVIDER": self.generate_provider,
            "LOCATION": self.generate_location,
            "ADDRESS": self.generate_address,
            "ZIP": self.generate_zip,
            "FACILITY": self.generate_facility,
            "ORGANIZATION": self.generate_organization,
            "DATE": self.generate_date,
            "AGE": self.generate_age,
            "PHONE": self.generate_phone,
            "FAX": self.generate_fax,
            "EMAIL": self.generate_email,
            "URL": self.generate_url,
            "IP": self.generate_ip,
            "ID_MEDICAL": self.generate_medical_id,
            "ID_INSURANCE": self.generate_insurance_id,
            "ID_ACCOUNT": self.generate_account_id,
            "ID_LICENSE": self.generate_license_id,
            "ID_DEVICE": self.generate_device_id,
            "ID_VEHICLE": self.generate_vehicle_id,
            "ID_OTHER": self.generate_ssn_style_id,
            "BIOMETRIC": self.generate_biometric,
            "IMAGE_REF": self.generate_image_ref,
            "OTHER_UNIQUE": self.generate_other_unique,
        }
        
        for label in labels_selected:
            if label in generator_map:
                value = generator_map[label]()
                entities_dict[label].append(value)
        
        return entities_dict, labels_selected

    def build_record(self, record_id: str) -> Dict:
        """
        Build a complete annotated record.
        
        Returns:
            Dict with id, text, entities, source, domain, lang
        """
        # Generate entities
        entities_dict, labels_selected = self.generate_entities_for_record()
        
        # Select template
        template_func = random.choice(self.note_templates)
        
        # Generate text
        text = template_func(entities_dict)
        
        # Add additional entities not in template
        additional_entities = []
        
        # Inject extras into text naturally
        additions = []
        if "EMAIL" in entities_dict and "email" not in text.lower():
            email = entities_dict["EMAIL"][0]
            additions.append(f" Patient email: {email}.")
        
        if "PHONE" in entities_dict and len([e for e in entities_dict["PHONE"]]) > len(re.findall(r'\d{3}[-\)]\d{3}', text)):
            for phone in entities_dict["PHONE"]:
                if phone not in text:
                    additions.append(f" Contact: {phone}.")
        
        if "ADDRESS" in entities_dict and entities_dict["ADDRESS"][0] not in text:
            addr = entities_dict["ADDRESS"][0]
            additions.append(f" Address on file: {addr}.")
        
        if "ZIP" in entities_dict and entities_dict["ZIP"][0] not in text:
            zip_code = entities_dict["ZIP"][0]
            additions.append(f" ZIP: {zip_code}.")
        
        if "ID_INSURANCE" in entities_dict:
            ins_id = entities_dict["ID_INSURANCE"][0]
            additions.append(f" Insurance ID: {ins_id}.")
        
        if "URL" in entities_dict:
            url = entities_dict["URL"][0]
            additions.append(f" Patient portal: {url}.")
        
        if "IP" in entities_dict:
            ip = entities_dict["IP"][0]
            additions.append(f" System access from IP: {ip}.")
        
        if "ID_ACCOUNT" in entities_dict:
            acct = entities_dict["ID_ACCOUNT"][0]
            additions.append(f" Billing {acct}.")
        
        if "ID_LICENSE" in entities_dict:
            lic = entities_dict["ID_LICENSE"][0]
            additions.append(f" Provider {lic}.")
        
        if "ID_DEVICE" in entities_dict:
            dev = entities_dict["ID_DEVICE"][0]
            additions.append(f" Patient has implanted {dev}.")
        
        if "ID_VEHICLE" in entities_dict:
            veh = entities_dict["ID_VEHICLE"][0]
            additions.append(f" Vehicle registration: {veh}.")
        
        if "ID_OTHER" in entities_dict:
            ssn = entities_dict["ID_OTHER"][0]
            additions.append(f" SSN on file: {ssn}.")
        
        if "BIOMETRIC" in entities_dict:
            bio = entities_dict["BIOMETRIC"][0]
            additions.append(f" Biometric verification: {bio}.")
        
        if "IMAGE_REF" in entities_dict:
            img = entities_dict["IMAGE_REF"][0]
            additions.append(f" Photo ID on file: {img}.")
        
        if "OTHER_UNIQUE" in entities_dict:
            other = entities_dict["OTHER_UNIQUE"][0]
            additions.append(f" Reference {other}.")
        
        if "CAREGIVER" in entities_dict:
            caregiver = entities_dict["CAREGIVER"][0]
            additions.append(f" Primary caregiver: {caregiver}.")
        
        if "RELATIVE" in entities_dict:
            relative = entities_dict["RELATIVE"][0]
            additions.append(f" Next of kin: {relative}.")
        
        if "LOCATION" in entities_dict and entities_dict["LOCATION"][0] not in text:
            loc = entities_dict["LOCATION"][0]
            additions.append(f" Patient resides in {loc}.")
        
        if "ORGANIZATION" in entities_dict:
            org = entities_dict["ORGANIZATION"][0]
            additions.append(f" Referred by {org}.")
        
        # Add to text
        if additions:
            text = text.rstrip() + " " + " ".join(additions)
        
        # Now annotate all entities
        entities_list = []
        
        for label in labels_selected:
            if label in entities_dict:
                for value in entities_dict[label]:
                    self.add_entity(text, value, label, entities_list)
        
        # Sort entities by start position
        entities_list.sort(key=lambda x: x["start"])
        
        # Validate
        self.validate_entities(text, entities_list)
        
        return {
            "id": record_id,
            "text": text,
            "entities": entities_list,
            "source": "synthetic",
            "domain": "healthcare",
            "lang": "en"
        }

    def validate_entities(self, text: str, entities: List[Dict]) -> None:
        """
        Validate entity offsets and check for overlaps.
        
        Raises:
            ValueError: If validation fails
        """
        for ent in entities:
            start = ent["start"]
            end = ent["end"]
            label = ent["label"]
            
            # Validate offset
            extracted = text[start:end]
            if not extracted:
                raise ValueError(f"Empty entity at [{start}:{end}] for label {label}")
            
            # Check bounds
            if start < 0 or end > len(text) or start >= end:
                raise ValueError(f"Invalid offset [{start}:{end}] for text length {len(text)}")
        
        # Check overlaps
        for i, ent1 in enumerate(entities):
            for ent2 in entities[i+1:]:
                if not (ent1["end"] <= ent2["start"] or ent2["end"] <= ent1["start"]):
                    raise ValueError(
                        f"Overlapping entities: {ent1} and {ent2}"
                    )

    def generate_dataset(self, n_records: int, verbose: bool = False) -> List[Dict]:
        """
        Generate complete dataset.
        
        Args:
            n_records: Number of records to generate
            verbose: Print progress
            
        Returns:
            List of record dicts
        """
        dataset = []
        
        for i in range(n_records):
            if verbose and (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{n_records} records...")
            
            record_id = f"synthetic_{uuid.uuid4().hex[:12]}"
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

    # =======================================================================
    # BONUS FEATURES
    # =======================================================================

    def convert_to_bio_tagging(self, record: Dict) -> List[Tuple[str, str]]:
        """
        Convert entity annotations to BIO tagging format.
        
        Args:
            record: Record dict with text and entities
            
        Returns:
            List of (token, tag) tuples
        """
        text = record["text"]
        entities = record["entities"]
        
        # Simple whitespace tokenization (production would use proper tokenizer)
        tokens = []
        token_positions = []
        
        current_pos = 0
        for match in re.finditer(r'\S+', text):
            tokens.append(match.group())
            token_positions.append((match.start(), match.end()))
        
        # Initialize all tokens as 'O' (Outside)
        tags = ['O'] * len(tokens)
        
        # Assign BIO tags
        for ent in entities:
            ent_start = ent["start"]
            ent_end = ent["end"]
            label = ent["label"]
            
            first_token = True
            for i, (tok_start, tok_end) in enumerate(token_positions):
                # Check if token overlaps with entity
                if tok_start < ent_end and tok_end > ent_start:
                    if first_token:
                        tags[i] = f"B-{label}"
                        first_token = False
                    else:
                        tags[i] = f"I-{label}"
        
        return list(zip(tokens, tags))

    def generate_entity_frequency_report(self, dataset: List[Dict]) -> Dict:
        """
        Generate frequency report of entity labels.
        
        Args:
            dataset: List of records
            
        Returns:
            Dict with statistics
        """
        label_counts = Counter()
        total_entities = 0
        
        for record in dataset:
            for ent in record["entities"]:
                label_counts[ent["label"]] += 1
                total_entities += 1
        
        report = {
            "total_records": len(dataset),
            "total_entities": total_entities,
            "avg_entities_per_record": total_entities / len(dataset) if dataset else 0,
            "label_distribution": dict(label_counts),
            "label_coverage": len(label_counts),
            "missing_labels": [l for l in LABEL_SCHEMA if l not in label_counts]
        }
        
        return report

    def split_dataset(
        self,
        dataset: List[Dict],
        train_ratio: float = 0.8,
        dev_ratio: float = 0.1,
        test_ratio: float = 0.1,
        shuffle: bool = True
    ) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        Split dataset into train/dev/test.
        
        Args:
            dataset: Full dataset
            train_ratio: Proportion for training
            dev_ratio: Proportion for development
            test_ratio: Proportion for test
            shuffle: Whether to shuffle before splitting
            
        Returns:
            Tuple of (train, dev, test) datasets
        """
        if abs(train_ratio + dev_ratio + test_ratio - 1.0) > 0.001:
            raise ValueError("Ratios must sum to 1.0")
        
        data = dataset.copy()
        if shuffle:
            random.shuffle(data)
        
        n = len(data)
        train_end = int(n * train_ratio)
        dev_end = train_end + int(n * dev_ratio)
        
        train = data[:train_end]
        dev = data[train_end:dev_end]
        test = data[dev_end:]
        
        return train, dev, test


# =======================================================================
# UTILITY FUNCTIONS
# =======================================================================

def print_annotated_record(record: Dict, max_display_length: int = 500) -> None:
    """Pretty print a record with highlighted entities."""
    print(f"\n{'='*80}")
    print(f"ID: {record['id']}")
    print(f"{'='*80}")
    
    text = record['text']
    if len(text) > max_display_length:
        text_display = text[:max_display_length] + "..."
    else:
        text_display = text
    
    print(f"\nTEXT:\n{text_display}\n")
    
    print(f"ENTITIES ({len(record['entities'])}):")
    for ent in record['entities']:
        entity_text = record['text'][ent['start']:ent['end']]
        print(f"  [{ent['start']:4d}-{ent['end']:4d}] {ent['label']:20s} → \"{entity_text}\"")


def print_bio_tagging_sample(bio_tags: List[Tuple[str, str]], max_tokens: int = 50) -> None:
    """Pretty print BIO tagging."""
    print(f"\nBIO TAGGING (first {max_tokens} tokens):")
    print("-" * 80)
    for i, (token, tag) in enumerate(bio_tags[:max_tokens]):
        print(f"{token:20s} {tag}")
    if len(bio_tags) > max_tokens:
        print(f"... ({len(bio_tags) - max_tokens} more tokens)")


def print_frequency_report(report: Dict) -> None:
    """Pretty print entity frequency report."""
    print(f"\n{'='*80}")
    print("ENTITY FREQUENCY REPORT")
    print(f"{'='*80}")
    print(f"Total Records: {report['total_records']}")
    print(f"Total Entities: {report['total_entities']}")
    print(f"Avg Entities/Record: {report['avg_entities_per_record']:.2f}")
    print(f"Label Coverage: {report['label_coverage']}/{len(LABEL_SCHEMA)}")
    
    print(f"\nLabel Distribution:")
    for label, count in sorted(report['label_distribution'].items(), key=lambda x: -x[1]):
        pct = 100 * count / report['total_entities']
        print(f"  {label:20s}: {count:5d} ({pct:5.2f}%)")
    
    if report['missing_labels']:
        print(f"\nMissing Labels: {', '.join(report['missing_labels'])}")


# =======================================================================
# MAIN EXECUTION
# =======================================================================

def main():
    """Main execution entry point."""
    print("=" * 80)
    print("SYNTHETIC PHI DATA GENERATOR")
    print("HIPAA Safe Harbor Aligned")
    print("=" * 80)
    
    # Initialize generator
    generator = SyntheticPHIGenerator(
        seed=42,  # For reproducibility
        min_entities_per_record=5,
        max_entities_per_record=15,
        include_long_tail_identifiers=True
    )
    
    # Generate small sample dataset
    print("\n[1] Generating sample dataset (100 records)...")
    sample_dataset = generator.generate_dataset(n_records=100, verbose=True)
    
    # Write to JSONL
    sample_output_path = "synthetic_phi_sample.jsonl"
    generator.write_jsonl(sample_dataset, sample_output_path)
    
    # Display first 3 records
    print("\n[2] Sample records:")
    for i in range(min(3, len(sample_dataset))):
        print_annotated_record(sample_dataset[i])
    
    # Generate BIO tagging example
    print("\n[3] BIO Tagging Conversion Example:")
    bio_tags = generator.convert_to_bio_tagging(sample_dataset[0])
    print_bio_tagging_sample(bio_tags)
    
    # Generate frequency report
    print("\n[4] Entity Frequency Report:")
    report = generator.generate_entity_frequency_report(sample_dataset)
    print_frequency_report(report)
    
    # Split dataset
    print("\n[5] Dataset Split:")
    train, dev, test = generator.split_dataset(sample_dataset)
    print(f"  Train: {len(train)} records")
    print(f"  Dev:   {len(dev)} records")
    print(f"  Test:  {len(test)} records")
    
    # Write splits
    generator.write_jsonl(train, "synthetic_phi_train.jsonl")
    generator.write_jsonl(dev, "synthetic_phi_dev.jsonl")
    generator.write_jsonl(test, "synthetic_phi_test.jsonl")
    
    # Generate larger dataset
    print("\n[6] Generating full dataset (10,000 records)...")
    print("This may take a minute...")
    full_dataset = generator.generate_dataset(n_records=10000, verbose=True)
    
    full_output_path = "synthetic_phi_full.jsonl"
    generator.write_jsonl(full_dataset, full_output_path)
    
    # Final report
    print("\n[7] Full Dataset Report:")
    full_report = generator.generate_entity_frequency_report(full_dataset)
    print_frequency_report(full_report)
    
    print("\n" + "=" * 80)
    print("✓ GENERATION COMPLETE")
    print("=" * 80)
    print(f"\nGenerated files:")
    print(f"  • {sample_output_path} (100 records)")
    print(f"  • synthetic_phi_train.jsonl (80 records)")
    print(f"  • synthetic_phi_dev.jsonl (10 records)")
    print(f"  • synthetic_phi_test.jsonl (10 records)")
    print(f"  • {full_output_path} (10,000 records)")
    print("\nReady for PHI detection model training!")


if __name__ == "__main__":
    main()
