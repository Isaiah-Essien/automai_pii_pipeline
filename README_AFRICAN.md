# African PHI Data Generator

## Overview

Specialized generator for **African healthcare PHI data** with short, focused sentences optimized for training PHI detection models on African medical records.

**Key Features:**
- African names, addresses, and phone numbers from approximately 54 African countries
- Comprehensive coverage of nearly all African nations with real cities, states, and regions
- Phone numbers and fax numbers with African country codes (+234, +254, +27, etc.)
- Email addresses, national IDs, medical records, insurance IDs, and account numbers
- Short sentences (max 15 words) for focused learning
- Specific date types: DOB, admission, discharge
- JSON configuration for easy customization
- Comprehensive geographic and contact data for African healthcare systems

## Requirements

- Python 3.8+
- Faker library

## Quick Start

### Installation

```bash
# Install dependencies
pip install faker

# Or use requirements.txt
pip install -r requirements.txt
```

### Basic Usage

```bash
# Generate African PHI dataset
python generate_african_phi.py
```

This will generate:
- `african_phi_sample.jsonl` - 100 sample records
- `african_phi_train.jsonl` - 800 training records
- `african_phi_dev.jsonl` - 100 development records
- `african_phi_test.jsonl` - 100 test records
- `african_phi_full.jsonl` - 1,000 full dataset records

## PHI Entity Types

The generator covers **16 entity types** including contact information, identification, and healthcare identifiers:

**Personal & Demographic:**
| Entity Type | Description | Example |
|---|---|---|
| `PERSON` | African names | Amara Okonkwo, Kwame Mwangi |
| `DATE_OF_BIRTH` | Birth date | 15/03/1985 |
| `SSN` | Social Security Number / National ID | NG-1985031514567 |
| `ADDRESS` | Street address | 45 Hospital Road |
| `CITY` | African cities | Lagos, Nairobi, Cape Town |
| `STATE` | States/Provinces | Lagos State, Nairobi County |
| `COUNTRY` | African countries | Nigeria, Kenya, South Africa |

**Contact Information:**
| Entity Type | Description | Example |
|---|---|---|
| `PHONE` | Phone with country code | +234 803 123 4567 |
| `FAX` | Fax number with country code | +254 20 123 4567 |
| `EMAIL` | Email address | amara.okonkwo@hospital.ac.za |

**Healthcare & Financial Identifiers:**
| Entity Type | Description | Example |
|---|---|---|
| `ADMISSION_DATE` | Hospital admission date | 12 January 2024 |
| `DISCHARGE_DATE` | Hospital discharge date | 20-01-2024 |
| `DATE` | General dates | 05 Feb 2024 |
| `MEDICAL_RECORD_NUMBER` | Hospital/clinic record ID | MR-2026-338968 |
| `HEALTH_PLAN_BENEFICIARY_NUMBER` | Insurance beneficiary ID | HP-ZA-123-9876543210 |
| `ACCOUNT_NUMBER` | Bank/payment account number | ZA-984765321098 |

## Supported African Countries

The generator includes authentic data from approximately 54 African countries with:
- Over 100 authentic African first names
- Over 100 authentic African family names
- Over 100 authentic African street names and landmarks
- Real cities, states, and regions for each country
- Correct phone codes and country codes

**Regions Covered:**
- **West Africa**: Nigeria, Ghana, Senegal, Côte d'Ivoire, Cameroon, Liberia, Sierra Leone, Guinea, Mali, Burkina Faso, Niger, Chad, Guinea-Bissau, Gabon, Gambia, Cape Verde, São Tomé & Príncipe
- **East Africa**: Kenya, Tanzania, Uganda, Ethiopia, Rwanda, Burundi, Somalia, South Sudan, Eritrea, Djibouti, Mozambique, Mauritius, Seychelles, Comoros
- **South Africa**: South Africa, Namibia, Botswana, Lesotho, Eswatini, Madagascar, Malawi, Zambia, Zimbabwe
- **North Africa**: Egypt, Libya, Tunisia, Algeria, Morocco, Mauritania, Sudan
- **Central Africa**: Democratic Republic of Congo, Republic of Congo, Equatorial Guinea, Central African Republic

## Output Format

Each record contains short, focused sentences with comprehensive PHI coverage:

```json
{
  "id": "african_phi_abc123",
  "text": "Patient name is Amara Okonkwo. Born on 15/03/1985. National ID: NG-1985031514567. Resides at 45 Hospital Road, Lagos. Contact number: +234 803 123 4567. Fax: +234 803 123 4568. Email: amara.okonkwo@hospital.ac.za. Medical record: MR-2026-338968. Beneficiary ID: HP-NG-123-1234567890. Account: NG-123456789012. Admitted on 12 January 2024.",
  "entities": [
    {"start": 16, "end": 29, "label": "PERSON"},
    {"start": 39, "end": 49, "label": "DATE_OF_BIRTH"},
    {"start": 62, "end": 78, "label": "SSN"},
    {"start": 91, "end": 109, "label": "ADDRESS"},
    {"start": 111, "end": 116, "label": "CITY"},
    {"start": 134, "end": 151, "label": "PHONE"},
    {"start": 157, "end": 174, "label": "FAX"},
    {"start": 182, "end": 211, "label": "EMAIL"},
    {"start": 229, "end": 243, "label": "MEDICAL_RECORD_NUMBER"},
    {"start": 260, "end": 280, "label": "HEALTH_PLAN_BENEFICIARY_NUMBER"},
    {"start": 290, "end": 304, "label": "ACCOUNT_NUMBER"},
    {"start": 317, "end": 333, "label": "ADMISSION_DATE"}
  ],
  "source": "synthetic",
  "region": "africa",
  "lang": "en"
}
```

**Key Features:**
- Short sentences (1-3 entities per sentence)
- Clear PHI boundaries with precise character offsets
- Authentic African data across 54 countries
- No overlapping entities
- **Complete healthcare data**: identification, contact, medical records, insurance, banking

## Configuration

### Customize via `phi_config.json`

```json
{
  "entity_types": {
    "PERSON": {
      "enabled": true,
      "probability": 1.0
    },
    "PHONE": {
      "enabled": true,
      "probability": 0.9
    }
  },
  "african_countries": {
    "Nigeria": {
      "code": "NG",
      "phone_code": "+234",
      "cities": ["Lagos", "Abuja", "Kano"],
      "states": ["Lagos State", "Kano State"]
    }
  }
}
```

### Programmatic Usage

```python
from generate_african_phi import AfricanPHIGenerator

# Initialize
generator = AfricanPHIGenerator(
    config_path="phi_config.json",
    seed=42
)

# Generate dataset
dataset = generator.generate_dataset(n_records=1000, verbose=True)

# Write to file
generator.write_jsonl(dataset, "my_african_phi.jsonl")

# Get statistics
report = generator.generate_frequency_report(dataset)
print(report)
```

## Example Outputs

### Example 1: Full Patient Contact Record
```
Patient name is Chinwe Okeke. Born on 23/06/1978. National ID: NG-1978062301234.
Contact number: +234 803 456 7890. Fax: +234 803 456 7891. Email: chinwe.okeke@clinic.com.
Lives in Kano. Medical record: MR-2026-456789. Beneficiary ID: HP-NG-456-9876543210.
```

Entities:
- PERSON: "Chinwe Okeke"
- DATE_OF_BIRTH: "23/06/1978"
- SSN: "NG-1978062301234"
- PHONE: "+234 803 456 7890"
- FAX: "+234 803 456 7891"
- EMAIL: "chinwe.okeke@clinic.com"
- CITY: "Kano"
- MEDICAL_RECORD_NUMBER: "MR-2026-456789"
- HEALTH_PLAN_BENEFICIARY_NUMBER: "HP-NG-456-9876543210"

### Example 2: Hospital Admission & Financial Record
```
Patient name is Kwame Mwangi. National ID: KE-1990051256789. Resides at 123 Uhuru Road, Nairobi.
From Nairobi County, Kenya. Phone: +254 722 123 4567. Medical record: MR-2026-789012.
Beneficiary ID: HP-KE-789-5432109876. Account: KE-345678901234.
Admitted on 15 January 2024. Discharged on 22 January 2024.
```

Entities:
- PERSON: "Kwame Mwangi"
- SSN: "KE-1990051256789"
- ADDRESS: "123 Uhuru Road"
- CITY: "Nairobi"
- STATE: "Nairobi County"
- COUNTRY: "Kenya"
- PHONE: "+254 722 123 4567"
- MEDICAL_RECORD_NUMBER: "MR-2026-789012"
- HEALTH_PLAN_BENEFICIARY_NUMBER: "HP-KE-789-5432109876"
- ACCOUNT_NUMBER: "KE-345678901234"
- ADMISSION_DATE: "15 January 2024"
- DISCHARGE_DATE: "22 January 2024"

### Example 3: Multi-country Healthcare & Banking Integration
```
Patient name is Zuri Banda. Born on 12-04-1990. National ID: ZM-1990040112345.
Contact number: +260 977 123 4567. Fax: +260 977 123 4568. Email: zuri.banda@healthcare.zm.
Country of residence is Zambia. Medical record: MR-2026-234567.
Beneficiary ID: HP-ZM-234-1111111111. Account: ZM-987654321098.
Visited clinic on 05 Feb 2024.
```

Entities:
- PERSON: "Zuri Banda"
- DATE_OF_BIRTH: "12-04-1990"
- SSN: "ZM-1990040112345"
- PHONE: "+260 977 123 4567"
- FAX: "+260 977 123 4568"
- EMAIL: "zuri.banda@healthcare.zm"
- COUNTRY: "Zambia"
- MEDICAL_RECORD_NUMBER: "MR-2026-234567"
- HEALTH_PLAN_BENEFICIARY_NUMBER: "HP-ZM-234-1111111111"
- ACCOUNT_NUMBER: "ZM-987654321098"
- DATE: "05 Feb 2024"

## Customization

### Add More African Countries

Edit `phi_config.json`:

```json
{
  "african_countries": {
    "Egypt": {
      "code": "EG",
      "phone_code": "+20",
      "cities": ["Cairo", "Alexandria", "Giza"],
      "states": ["Cairo Governorate", "Alexandria Governorate"]
    }
  }
}
```

### Adjust Entity Probabilities

```json
{
  "entity_types": {
    "PHONE": {
      "enabled": true,
      "probability": 1.0  // Always include phone
    },
    "ADDRESS": {
      "enabled": true,
      "probability": 0.5  // Include 50% of the time
    }
  }
}
```

### Control Dataset Size

```python
# Small dataset
small = generator.generate_dataset(n_records=100)

# Large dataset
large = generator.generate_dataset(n_records=10000)
```

## Use Cases

### 1. Training African NER Models
Train models to recognize PHI in African medical records:

```python
generator = AfricanPHIGenerator(seed=42)
training_data = generator.generate_dataset(n_records=5000)
```

### 2. Testing De-identification Systems
Test if your system handles African data:

```python
test_data = generator.generate_dataset(n_records=100)
for record in test_data:
    redacted = your_deidentifier(record['text'])
    # Validate against record['entities']
```

### 3. Data Augmentation
Augment real African datasets:

```python
synthetic = generator.generate_dataset(n_records=1000)
# Mix with real data for better model performance
```

## Dataset Statistics

Full dataset (1,000 records, 11,662 entities):
```
PERSON (8.57%) | MEDICAL_RECORD_NUMBER (7.79%) | PHONE (7.75%)
ADMISSION_DATE (7.83%) | ADDRESS (7.73%) | EMAIL (7.30%)
DATE_OF_BIRTH (7.71%) | SSN (6.88%) | HEALTH_PLAN_BENEFICIARY_NUMBER (6.43%)
FAX (5.20%) | ACCOUNT_NUMBER (4.15%) | And more...
```

## Validation and Visualization

Use the included validator:

```bash
python validate_dataset.py african_phi_full.jsonl
```

View records with entity highlighting:

```bash
python pretty_print.py african_phi_sample.jsonl      # Show first 3 records
python pretty_print.py african_phi_sample.jsonl 5    # Show specific record #5
```

## Why This Dataset Design?

**Short Sentences:** Help models:
- Learn clear PHI boundaries
- Focus on entity patterns, not context
- Achieve higher precision in detection
- Work better with limited training data
- Generalize to different writing styles

**Rich Entity Coverage:** Trains comprehensive PHI detection for:
- Identity documents (SSN/National IDs)
- Healthcare systems (medical records, insurance)
- Financial systems (bank accounts, beneficiary IDs)
- Communication channels (phone, fax, email)
- Geographic information (addresses, locations)
- Temporal data (dates of birth, admission, discharge)

## Quality Assurance

Each generated record:
- Uses authentic African names from 54 countries
- Includes real African cities, states, and street names
- Has correct country codes for phones and fax
- Generates realistic email addresses and institutional IDs
- Creates valid-format national IDs, medical records, and account numbers
- Contains non-overlapping entities with precise character offsets
- Uses short, focused sentences (max 15 words per sentence)
- Validates all entity boundaries automatically
- Supports comprehensive healthcare and financial data scenarios

## File Structure

```
automai_pii_pipeline/
├── generate_african_phi.py      # African PHI generator
├── phi_config.json               # Configuration file
├── validate_dataset.py           # Validation tool
├── pretty_print.py               # Visualization tool
├── requirements.txt              # Dependencies
└── README_AFRICAN.md            # This file
```

## Troubleshooting

### Issue: Import Error
```bash
# Solution
pip install faker
```

### Issue: Wrong Python Version
```bash
# Check version (needs 3.8+)
python --version

# Use correct Python
python3 generate_african_phi.py
```

### Issue: Config File Not Found
```bash
# Make sure phi_config.json is in same directory
ls phi_config.json
```

## Contact and Support

For issues or questions:
1. Check `phi_config.json` settings
2. Review generated samples
3. Validate output with `validate_dataset.py`

## Best Practices

1. **Start Small**: Generate 100 records first
2. **Review Samples**: Check if data looks realistic
3. **Adjust Config**: Tune probabilities for your needs
4. **Validate**: Always run validation before training
5. **Test**: Try different countries and settings

## License

See LICENSE file for details.

---

**Ready to generate African PHI data!**

```bash
python generate_african_phi.py
```
