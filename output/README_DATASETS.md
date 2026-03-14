# PII Datasets - Consolidated Output

## Summary

All 15 PII datasets have been consolidated into the `output/` folder.

**Total Size:** 337 MB
**Datasets:** 15 types × 2 versions (full + template) = 30 files
**Total Sentences:** 710,000+

## Files Location

All files are now in: `/Users/cococe/Desktop/automai_pii_pipeline/output/`

## Dataset Files (15 total)

### Full Datasets (*_dataset.json files) - 250 MB

| File | Size | Sentences | PII Type |
|------|------|-----------|----------|
| name_pii_dataset.json | 39 MB | 130,000 | Names (African) |
| date_pii_dataset.json | 31 MB | 110,000 | Dates |
| phone_pii_dataset.json | 24 MB | 40,000 | Phone Numbers |
| address_pii_dataset.json | 22 MB | 70,000 | Physical Addresses (African) |
| email_pii_dataset.json | 18 MB | 60,000 | Emails (African) |
| ssn_pii_dataset.json | 14 MB | 50,000 | Social Security Numbers |
| mrn_pii_dataset.json | 14 MB | 50,000 | Medical Record Numbers |
| device_id_pii_dataset.json | 13 MB | 40,000 | Device IDs |
| fax_pii_dataset.json | 12 MB | 40,000 | FAX Numbers |
| location_pii_dataset.json | 11 MB | 30,000 | Locations (African facilities) |
| url_pii_dataset.json | 9.6 MB | 30,000 | URLs |
| vehicle_id_pii_dataset.json | 9.4 MB | 30,000 | Vehicle IDs (African) |
| certlic_pii_dataset.json | 9.3 MB | 30,000 | Certificates & Licenses |
| account_number_pii_dataset.json | 9.1 MB | 30,000 | Account Numbers |
| ip_pii_dataset.json | 3.0 MB | 10,000 | IP Addresses |
| **TOTAL DATASETS** | **250 MB** | **640,000** | - |

### Template Datasets (*_templates.json files) - 87 MB

Same files as above with `{PLACEHOLDER}` values instead of actual PII:

| File | Size | Use Case |
|------|------|----------|
| name_pii_templates.json | 14 MB | Secure sharing (names replaced with {NAME}) |
| date_pii_templates.json | 11 MB | Secure sharing (dates replaced with {DATE}) |
| phone_pii_templates.json | 9.0 MB | Secure sharing (phones replaced with {PHONE}) |
| ... (15 total files) | ... | ... |
| **TOTAL TEMPLATES** | **87 MB** | **640,000** | - |

## Quick Statistics

- **Total PII Types:** 15
- **Total Sentences:** 640,000 (datasets) + 640,000 (templates) = 1,280,000 records
- **Format Variations:** 93 combined
- **Output Files:** 30 JSON files
- **Total Size:** 337 MB

## File Naming Convention

```
{pii_type}_pii_dataset.json    - Full dataset with actual values
{pii_type}_pii_templates.json  - Template with {PLACEHOLDER} values
```

### PII Type Abbreviations

- `name_pii_*` - Person names
- `date_pii_*` - Dates
- `email_pii_*` - Email addresses
- `mrn_pii_*` - Medical Record Numbers
- `ip_pii_*` - IP addresses
- `account_number_pii_*` - Financial accounts
- `address_pii_*` - Physical addresses
- `url_pii_*` - URLs/websites
- `vehicle_id_pii_*` - Vehicle IDs
- `ssn_pii_*` - Social Security Numbers
- `device_id_pii_*` - Device identifiers
- `certlic_pii_*` - Certificates and licenses
- `fax_pii_*` - FAX numbers
- `location_pii_*` - Healthcare locations
- `phone_pii_*` - Phone numbers

## Usage Examples

### Load a Dataset in Python

```python
import json

# Load full dataset
with open('output/name_pii_dataset.json', 'r') as f:
    data = json.load(f)

# Access metadata
print(f"Total sentences: {data['metadata']['total_sentences']}")
print(f"Formats: {data['metadata']['total_formats']}")

# Access first record
first_record = data['data'][0]
print(f"Sentence: {first_record['sentence']}")
print(f"Entity: {first_record['entity']}")
```

### Load Template Dataset

```python
# Load template (safer for sharing)
with open('output/name_pii_templates.json', 'r') as f:
    templates = json.load(f)

# All entity values are replaced with placeholders
sentence = templates['data'][0]['sentence']
print(sentence)  # "Patient {NAME} was admitted on {DATE}."
```

## Data Format Example

Each record contains:

```json
{
  "sentence_id": "name_000001",
  "sentence": "Patient Kwame Osei was admitted on 15/03/2026.",
  "entity": {
    "start": 8,
    "end": 20,
    "label": "PERSON",
    "value": "Kwame Osei"
  },
  "format": 1,
  "format_pattern": "{first_name} {last_name}"
}
```

Character offsets allow precise entity extraction:
- `start`: 8 (position where "Kwame Osei" begins)
- `end`: 20 (position where "Kwame Osei" ends)

## Dataset Features

✅ **High Quality**
- Realistic healthcare/medical context
- African cultural authenticity
- Proper entity annotation with character offsets

✅ **Diverse Formats**
- 1-13 format variations per PII type
- 93 total format variations
- Realistic distribution

✅ **Complete Coverage**
- 15 HIPAA PII types
- 710,000+ sentences
- Healthcare-specific templates

✅ **Reusable**
- Machine learning training
- Named Entity Recognition (NER)
- Data validation testing
- Privacy-aware development

## Next Steps

1. **Review Datasets**
   ```bash
   cd output
   ls -lh
   ```

2. **Use for ML Training**
   - Load datasets into your NER model
   - Use template versions for secure sharing
   - Use full versions for development

3. **Integrate with Pipeline**
   - Use main.py for regeneration
   - Customize sentence counts
   - Add additional PII types

4. **Version Control**
   ```bash
   git add output/
   git commit -m "Add consolidated PII datasets"
   git push
   ```

## File Organization

```
/Users/cococe/Desktop/automai_pii_pipeline/
├── output/
│   ├── name_pii_dataset.json
│   ├── name_pii_templates.json
│   ├── date_pii_dataset.json
│   ├── date_pii_templates.json
│   ├── ... (26 more files)
│   ├── GENERATION_REPORT.json
│   └── README_OUTPUT.md (this file)
└── src/pii/
    ├── names/
    ├── dates/
    └── ... (original source files)
```

## Backup & Recovery

All original files remain in `src/pii/{type}/` folders:
- Original datasets preserved
- Templates preserved
- Components preserved
- Can regenerate if needed

## Support

- **Questions about data:** Check README_MAIN.md
- **Generator details:** Check src/pii_{type}/generate_*_pii.py
- **Schema info:** Check src/pii_variation_schema.json
- **Regenerate:** Run `python3 main.py`
