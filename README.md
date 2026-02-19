# Synthetic PHI Data Generator

## 🎯 Overview

Production-ready Python script for generating synthetic HIPAA-aligned Protected Health Information (PHI) data for training PHI detection models.

**Key Features:**
- ✅ Generates realistic medical narrative text (admission notes, discharge summaries, etc.)
- ✅ Injects all 18 HIPAA Safe Harbor identifiers
- ✅ Annotates entities with absolute character offsets
- ✅ Outputs in JSON Lines (JSONL) format
- ✅ Follows canonical 26-label semantic schema
- ✅ Includes BIO tagging conversion
- ✅ Automatic validation and quality checks
- ✅ Train/dev/test splitting
- ✅ Entity frequency analysis

## 📋 Requirements

- Python 3.8+
- Faker library

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install Faker directly
pip install faker
```

### Basic Usage

```bash
# Generate synthetic PHI dataset
python generate_synthetic_phi.py
```

This will generate:
- `synthetic_phi_sample.jsonl` - 100 sample records
- `synthetic_phi_train.jsonl` - 80 training records
- `synthetic_phi_dev.jsonl` - 10 development records
- `synthetic_phi_test.jsonl` - 10 test records
- `synthetic_phi_full.jsonl` - 10,000 full dataset records

### Programmatic Usage

```python
from generate_synthetic_phi import SyntheticPHIGenerator

# Initialize generator
generator = SyntheticPHIGenerator(
    seed=42,
    min_entities_per_record=5,
    max_entities_per_record=15,
    include_long_tail_identifiers=True
)

# Generate dataset
dataset = generator.generate_dataset(n_records=1000, verbose=True)

# Write to file
generator.write_jsonl(dataset, "output.jsonl")

# Generate frequency report
report = generator.generate_entity_frequency_report(dataset)
print(report)

# Convert to BIO tagging
bio_tags = generator.convert_to_bio_tagging(dataset[0])
print(bio_tags)

# Split dataset
train, dev, test = generator.split_dataset(dataset)
```

## 📊 Output Format

Each record follows this strict JSONL schema:

```json
{
  "id": "synthetic_abc123def456",
  "text": "Patient John Smith was admitted on March 4, 2023 to Kigali Medical Center. His MRN 4582931 was verified upon arrival...",
  "entities": [
    {"start": 8, "end": 18, "label": "PERSON"},
    {"start": 35, "end": 49, "label": "DATE"},
    {"start": 53, "end": 75, "label": "FACILITY"},
    {"start": 81, "end": 91, "label": "ID_MEDICAL"}
  ],
  "source": "synthetic",
  "domain": "healthcare",
  "lang": "en"
}
```

### Entity Validation

- `text[start:end]` exactly equals the entity substring
- Offsets are absolute character positions (0-indexed)
- No overlapping spans
- Automatic validation on generation

## 🏷️ Canonical Label Schema (26 Labels)

The generator uses these semantic labels aligned with HIPAA Safe Harbor:

| Label | Description | HIPAA Category |
|-------|-------------|----------------|
| `PERSON` | Individual's name | Names |
| `RELATIVE` | Family member name | Names |
| `CAREGIVER` | Caregiver name | Names |
| `PROVIDER` | Healthcare provider name | Names |
| `LOCATION` | City/county | Geographic subdivision |
| `ADDRESS` | Street address | Geographic subdivision |
| `ZIP` | ZIP code | Geographic subdivision |
| `FACILITY` | Healthcare facility | Names |
| `ORGANIZATION` | Organization name | Names |
| `DATE` | Any date | Dates |
| `AGE` | Age (especially >89) | Ages |
| `PHONE` | Phone number | Telephone |
| `FAX` | Fax number | Fax |
| `EMAIL` | Email address | Email |
| `URL` | Web URL | URLs |
| `IP` | IP address | IP address |
| `ID_MEDICAL` | Medical record number | Medical record number |
| `ID_INSURANCE` | Health plan ID | Health plan number |
| `ID_ACCOUNT` | Account number | Account number |
| `ID_LICENSE` | License/certificate | Certificate/license |
| `ID_DEVICE` | Device identifier | Device identifier |
| `ID_VEHICLE` | Vehicle ID/plate | Vehicle identifier |
| `ID_OTHER` | SSN-style ID | Social Security number |
| `BIOMETRIC` | Biometric identifier | Biometric identifier |
| `IMAGE_REF` | Photo reference | Full-face photo |
| `OTHER_UNIQUE` | Other unique ID | Other unique identifier |

## 🏥 Medical Note Types

The generator creates realistic medical narratives:

1. **Admission Notes** - Patient admission documentation
2. **Discharge Summaries** - Post-treatment summaries
3. **Clinical Observations** - Routine clinical notes
4. **Emergency Reports** - ED documentation
5. **Lab Reports** - Laboratory results
6. **Referral Letters** - Physician referrals
7. **Progress Notes** - Treatment progress
8. **Consultation Notes** - Specialist consultations

## ⚙️ Configuration Options

### Generator Parameters

```python
SyntheticPHIGenerator(
    seed=42,                              # Random seed for reproducibility
    locale="en_US",                       # Faker locale
    min_entities_per_record=5,           # Minimum PHI entities per note
    max_entities_per_record=15,          # Maximum PHI entities per note
    include_long_tail_identifiers=True   # Include rare HIPAA identifiers
)
```

### Entity Probabilities

Customize entity inclusion probabilities:

```python
generator.entity_probabilities = {
    "PERSON": 0.9,      # 90% of records
    "DATE": 0.9,
    "FACILITY": 0.8,
    "PROVIDER": 0.7,
    "ID_MEDICAL": 0.8,
    "PHONE": 0.6,
    # ... etc
}
```

## 🧪 BIO Tagging Conversion

Convert entity annotations to BIO format for token classification:

```python
bio_tags = generator.convert_to_bio_tagging(record)
# Returns: [('Patient', 'O'), ('John', 'B-PERSON'), ('Smith', 'I-PERSON'), ...]
```

**BIO Schema:**
- `B-LABEL` - Beginning of entity
- `I-LABEL` - Inside entity
- `O` - Outside any entity

## 📈 Analysis & Reporting

### Entity Frequency Report

```python
report = generator.generate_entity_frequency_report(dataset)
# Returns:
# {
#   "total_records": 1000,
#   "total_entities": 8532,
#   "avg_entities_per_record": 8.53,
#   "label_distribution": {"PERSON": 892, "DATE": 876, ...},
#   "label_coverage": 26,
#   "missing_labels": []
# }
```

### Dataset Splitting

```python
train, dev, test = generator.split_dataset(
    dataset,
    train_ratio=0.8,
    dev_ratio=0.1,
    test_ratio=0.1,
    shuffle=True
)
```

## 🔍 Validation Features

The generator automatically validates:

1. **Offset Accuracy** - `text[start:end]` matches entity
2. **Span Overlap** - Detects overlapping entities
3. **Bounds Checking** - Valid start/end positions
4. **Coverage Analysis** - Ensures HIPAA category coverage

## 🏗️ Architecture

Follows **Detect-Map-Act** philosophy:

- **Detect**: Semantic entity generation with proper labels
- **Map**: Regulatory alignment with HIPAA Safe Harbor
- **Act**: Audit-ready output with validation

### Class Structure

```
SyntheticPHIGenerator
├── Entity Generators (one per HIPAA category)
│   ├── generate_person()
│   ├── generate_date()
│   ├── generate_medical_id()
│   └── ... (26 generators)
├── Medical Note Templates (8 templates)
│   ├── _template_admission_note()
│   ├── _template_discharge_summary()
│   └── ...
├── Annotation & Validation
│   ├── add_entity()
│   ├── validate_entities()
│   └── build_record()
└── Bonus Features
    ├── convert_to_bio_tagging()
    ├── generate_entity_frequency_report()
    └── split_dataset()
```

## 📝 Example Output

### JSONL Record

```json
{"id": "synthetic_a1b2c3d4e5f6", "text": "ADMISSION NOTE\n\nPatient Michael Johnson, 67 years old, was admitted on February 15, 2024 to Springfield Medical Center. MRN 3847291 was verified upon arrival. \n\nChief Complaint: Hypertension\n\nHistory of Present Illness:\nThe patient presented to the emergency department with symptoms consistent with hypertension. Initial evaluation performed by Dr. Williams.", "entities": [{"start": 28, "end": 44, "label": "PERSON"}, {"start": 46, "end": 58, "label": "AGE"}, {"start": 75, "end": 93, "label": "DATE"}, {"start": 97, "end": 124, "label": "FACILITY"}, {"start": 126, "end": 137, "label": "ID_MEDICAL"}, {"start": 348, "end": 360, "label": "PROVIDER"}], "source": "synthetic", "domain": "healthcare", "lang": "en"}
```

### BIO Tagging

```
Patient          O
Michael          B-PERSON
Johnson          I-PERSON
,                O
67               B-AGE
years            I-AGE
old              I-AGE
,                O
was              O
admitted         O
on               O
February         B-DATE
15               I-DATE
,                I-DATE
2024             I-DATE
...
```

## 🎓 Use Cases

Perfect for training:
- Named Entity Recognition (NER) models
- Token classification models (DeBERTa, BERT, RoBERTa)
- PHI detection systems
- Clinical NLP pipelines
- HIPAA compliance tools

## 🔒 Privacy & Ethics

**Important Notes:**
- This generates **synthetic** data only
- No real patient information is used
- Safe for development and testing
- Not intended for compliance auditing with real data
- Always validate with domain experts before production use

## 🐛 Troubleshooting

### Import Error

```bash
ImportError: Please install faker: pip install faker
```

**Solution:** `pip install faker`

### Validation Error

```
ValueError: Offset mismatch: text[X:Y] != 'substring'
```

**Cause:** Entity substring not found at expected position  
**Solution:** Usually auto-handled; check custom modifications

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

This is a production-ready reference implementation. Contributions welcome for:
- Additional medical note templates
- Enhanced entity variety
- Performance optimizations
- Additional output formats

## 📚 References

- [HIPAA Safe Harbor Method](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)
- [PHI Identifiers (45 CFR §164.514)](https://www.govinfo.gov/content/pkg/CFR-2021-title45-vol1/xml/CFR-2021-title45-vol1-sec164-514.xml)

---

**Ready to generate synthetic PHI data for your detection model!** 🚀