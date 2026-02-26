# African PHI Data Generator

## 🌍 Overview

Specialized generator for **African healthcare PHI data** with short, focused sentences optimized for training PHI detection models on African medical records.

**Key Features:**
- ✅ African names, addresses, and phone numbers
- ✅ 10 African countries with real cities/states/regions
- ✅ Phone numbers with African country codes (+234, +254, +27, etc.)
- ✅ Short sentences (max 15 words) for focused learning
- ✅ Specific date types: DOB, admission, discharge
- ✅ JSON configuration for easy customization
- ✅ Geographic data from Nigeria, Kenya, South Africa, Ghana, Tanzania, Uganda, Ethiopia, Rwanda, Senegal, Zambia

## 📋 Requirements

- Python 3.8+
- Faker library

## 🚀 Quick Start

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

## 📊 PHI Entity Types

The generator focuses on these African PHI categories:

| Entity Type | Description | Example |
|-------------|-------------|---------|
| `PERSON` | African names | Amara Okonkwo, Kwame Mwangi |
| `DATE_OF_BIRTH` | Birth date | 15/03/1985 |
| `ADMISSION_DATE` | Hospital admission | 12 January 2024 |
| `DISCHARGE_DATE` | Hospital discharge | 20-01-2024 |
| `DATE` | General dates | 05 Feb 2024 |
| `ADDRESS` | Street address | 45 Hospital Road |
| `CITY` | African cities | Lagos, Nairobi, Cape Town |
| `STATE` | States/Provinces | Lagos State, Nairobi County |
| `COUNTRY` | African countries | Nigeria, Kenya, South Africa |
| `PHONE` | Phone with country code | +234 803 123 4567 |

## 🌍 Supported African Countries

The generator includes authentic data from:

1. **Nigeria** - Lagos, Abuja, Kano (+234)
2. **Kenya** - Nairobi, Mombasa, Kisumu (+254)
3. **South Africa** - Johannesburg, Cape Town, Durban (+27)
4. **Ghana** - Accra, Kumasi, Tamale (+233)
5. **Tanzania** - Dar es Salaam, Dodoma, Mwanza (+255)
6. **Uganda** - Kampala, Gulu, Mbarara (+256)
7. **Ethiopia** - Addis Ababa, Dire Dawa, Mekelle (+251)
8. **Rwanda** - Kigali, Butare, Gisenyi (+250)
9. **Senegal** - Dakar, Touba, Thiès (+221)
10. **Zambia** - Lusaka, Kitwe, Ndola (+260)

## 📝 Output Format

Each record contains short, focused sentences:

```json
{
  "id": "african_phi_abc123",
  "text": "Patient name is Amara Okonkwo. Born on 15/03/1985. Resides at 45 Hospital Road, Lagos. Contact number: +234 803 123 4567. Admitted on 12 January 2024.",
  "entities": [
    {"start": 16, "end": 29, "label": "PERSON"},
    {"start": 39, "end": 49, "label": "DATE_OF_BIRTH"},
    {"start": 62, "end": 80, "label": "ADDRESS"},
    {"start": 82, "end": 87, "label": "CITY"},
    {"start": 105, "end": 123, "label": "PHONE"},
    {"start": 136, "end": 152, "label": "ADMISSION_DATE"}
  ],
  "source": "synthetic",
  "region": "africa",
  "lang": "en"
}
```

**Key Features:**
- Short sentences (1-3 entities per sentence)
- Clear PHI boundaries
- Authentic African data
- No overlapping entities

## ⚙️ Configuration

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

## 📈 Example Outputs

### Example 1: Basic Patient Info
```
Patient name is Chinwe Okeke. Born on 23/06/1978. Lives in Kano. 
Contact number: +234 803 456 7890.
```

Entities:
- PERSON: "Chinwe Okeke"
- DATE_OF_BIRTH: "23/06/1978"
- CITY: "Kano"
- PHONE: "+234 803 456 7890"

### Example 2: Admission Record
```
Patient name is Kwame Mwangi. Resides at 123 Uhuru Road, Nairobi. 
From Nairobi County, Kenya. Admitted on 15 January 2024. 
Discharged on 22 January 2024.
```

Entities:
- PERSON: "Kwame Mwangi"
- ADDRESS: "123 Uhuru Road"
- CITY: "Nairobi"
- STATE: "Nairobi County"
- COUNTRY: "Kenya"
- ADMISSION_DATE: "15 January 2024"
- DISCHARGE_DATE: "22 January 2024"

### Example 3: Contact Information
```
Patient name is Zuri Banda. Born on 12-04-1990. 
Contact number: +260 977 123 4567. Country of residence is Zambia. 
Visited clinic on 05 Feb 2024.
```

Entities:
- PERSON: "Zuri Banda"
- DATE_OF_BIRTH: "12-04-1990"
- PHONE: "+260 977 123 4567"
- COUNTRY: "Zambia"
- DATE: "05 Feb 2024"

## 🔧 Customization

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

## 🎯 Use Cases

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

## 📊 Validation

Use the included validator:

```bash
python validate_dataset.py african_phi_full.jsonl
```

View records:

```bash
python pretty_print.py african_phi_sample.jsonl
```

## 🌟 Why Short Sentences?

Short sentences help models:
- ✅ Learn clear PHI boundaries
- ✅ Focus on entity patterns, not context
- ✅ Achieve higher precision
- ✅ Work better with limited training data
- ✅ Generalize to different writing styles

## 🔍 Quality Assurance

Each generated record:
- ✓ Uses authentic African names
- ✓ Includes real African cities/states
- ✓ Has correct country codes for phones
- ✓ Contains non-overlapping entities
- ✓ Uses short, focused sentences (max 15 words)
- ✓ Validates entity offsets automatically

## 📁 File Structure

```
automai_pii_pipeline/
├── generate_african_phi.py      # African PHI generator
├── phi_config.json               # Configuration file
├── validate_dataset.py           # Validation tool
├── pretty_print.py               # Visualization tool
├── requirements.txt              # Dependencies
└── README_AFRICAN.md            # This file
```

## 🐛 Troubleshooting

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

## 📞 Contact & Support

For issues or questions:
1. Check `phi_config.json` settings
2. Review generated samples
3. Validate output with `validate_dataset.py`

## 🎓 Best Practices

1. **Start Small**: Generate 100 records first
2. **Review Samples**: Check if data looks realistic
3. **Adjust Config**: Tune probabilities for your needs
4. **Validate**: Always run validation before training
5. **Test**: Try different countries and settings

## 📝 License

See LICENSE file for details.

---

**Ready to generate African PHI data!** 🌍

```bash
python generate_african_phi.py
```
