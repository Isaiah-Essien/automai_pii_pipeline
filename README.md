# PII Dataset Generation System

This system provides a unified interface to generate all 14+ HIPAA PII (Protected Health Information) datasets for healthcare machine learning and NER (Named Entity Recognition) training.

## Final Merged Datasets

The cleaned, merged PII datasets (2.2M+ records across 15 types) are hosted externally:

**Download:** [Final PII Datasets (Drive)](https://drive.google.com/placeholder-link) *(link to be added)*

These datasets consolidate contributor outputs into a unified schema with deduplication. See [Merge Pipeline](#merge-pipeline) below for how they are produced.

## Overview

The system includes generators for:

1. **Names** - 130,000 sentences (13 formats, African names)
2. **Dates** - 110,000 sentences (11 formats)
3. **Emails** - 60,000 sentences (6 formats, African domains)
4. **Medical Record Numbers (MRN)** - 50,000 sentences (5 formats)
5. **IP Addresses** - 10,000 sentences (1 format)
6. **Account Numbers** - 30,000 sentences (3 formats)
7. **Physical Addresses** - 70,000 sentences (7 formats, 229 African cities)
8. **URLs** - 30,000 sentences (3 formats)
9. **Vehicle IDs** - 30,000 sentences (3 formats, 9 African countries)
10. **Social Security Numbers (SSN)** - 50,000 sentences (5 formats)
11. **Device IDs** - 40,000 sentences (4 formats, 42 manufacturers)
12. **Certificates & Licenses** - 30,000 sentences (6 combined formats)
13. **FAX Numbers** - 40,000 sentences (8 formats)
14. **Locations (Geographic Subdivisions)** - 30,000 sentences (3 formats, 101 African facilities)
15. **Phone Numbers** - 40,000 sentences (8 formats)

**Total: 710,000+ sentences across all datasets**

## Output Structure

All generated datasets are saved to the `output/` directory with the following structure:

```
output/
  ├── account_number/
  │   ├── account_pii_dataset.json
  │   └── account_pii_templates.json
  ├── certificates_licenses/
  │   ├── certlic_pii_dataset.json
  │   └── certlic_pii_templates.json
  ├── dates/
  │   ├── date_pii_dataset.json
  │   └── date_pii_templates.json
  ├── ... (one folder per generator)
  ├── GENERATION_REPORT.json
  └── README_OUTPUT.md
```

Each PII type folder contains:
- **`{type}_pii_dataset.json`** - Full dataset with actual PII values and entity annotations
- **`{type}_pii_templates.json`** - Template version with {PLACEHOLDER} values for private learning datasets

## Usage

### Running All Generators

Generate all 15  PII datasets to the default `output/` directory:

```bash
python3 main.py
```

### Running with Custom Output Directory

```bash
python3 main.py --output /path/to/custom/output
```

### Listing Generated Files

```bash
python3 main.py --list-only
```

This will display all generated files organized by PII type with file sizes.

## Merge Pipeline

Contributor datasets can be merged into a single cleaned output.

### Merge Contributor Data

Place extracted contributor zip files in `data/` (e.g. `data/idara_extracted/`, `data/orpheus_extracted/`), then run:

```bash
python merge_pii_data.py
```

- Discovers all `data/*_extracted/PHI(*)/` folders automatically
- Deduplicates by (sentence, start, end, label)
- Skips regeneration when source files unchanged
- Use `--force` to regenerate even when unchanged

Output: `data/final_pii/*.json` (15 files, one per PII type). Each record has:

```json
{
  "id": 1,
  "sentence": "Patient John Smith was admitted.",
  "start": 8,
  "end": 19,
  "label": "PERSON",
  "value": "John Smith"
}
```

### Analyze Final Data

```bash
python analyze_final_pii.py
```

Reports record counts and file sizes per PII type.

## Output File Format

Each dataset file contains a structured JSON with metadata and data:

```json
{
  "metadata": {
    "total_formats": 8,
    "sentences_per_format": 5000,
    "total_sentences": 40000,
    "templates_count": 10
  },
  "data": [
    {
      "sentence_id": "fax_000001",
      "sentence": "Insurance fax line: +256 445 415 1638.",
      "entity": {
        "start": 20,
        "end": 37,
        "label": "FAX",
        "value": "+256 445 415 1638"
      },
      "format": 1,
      "format_pattern": "+{country_code} {area_code} {exchange} {number}"
    },
    ...
  ]
}
```

### Entity Annotation Fields

- **`sentence_id`** - Unique identifier (e.g., `fax_000001`)
- **`sentence`** - Complete sentence with PII entity
- **`entity.start`** - Character offset where entity begins
- **`entity.end`** - Character offset where entity ends
- **`entity.label`** - Type of PII (e.g., "FAX", "NAME", "EMAIL")
- **`entity.value`** - Actual entity value (or `{PLACEHOLDER}` in template files)
- **`format`** - Format variation number (1-N)
- **`format_pattern`** - Format pattern used (e.g., `+{country_code} {area_code} {exchange} {number}`)

## Generation Report

After generation, a `GENERATION_REPORT.json` file is created with:
- Total generators run
- Success/failure counts
- Output directory paths
- Any error messages

## Module Architecture

### Directory Structure

Each PII type is organized as a Python module:

```
src/pii/
  ├── names/
  │   ├── __init__.py
  │   ├── generate_name_pii.py
  │   ├── african_names.json
  │   └── (output files)
  ├── dates/
  ├── emails/
  ├── faxs/
  ├── geo_sub_divs/
  ├── ... (one per PII type)
```

### Generator Class Pattern

Each generator follows a consistent pattern:

```python
class NamePIIGenerator:
    def __init__(self):
        """Initialize generator with schema and components."""
        self.output_dir = None
        self.load_schema()
        self.load_components()
    
    def set_output_dir(self, output_dir: str):
        """Set custom output directory."""
        self.output_dir = output_dir
    
    def run(self, sentences_per_format: int = 10000):
        """Generate and save datasets."""
        data = self.generate_complete_dataset(sentences_per_format)
        self.save_dataset(data)
        self.save_template_dataset(data)
```

### Running Individual Generators

```python
from src.pii.names.generate_name_pii import NamePIIGenerator

# Direct generator usage
gen = NamePIIGenerator()
gen.set_output_dir('/path/to/output')
gen.run(sentences_per_format=1000)
```

## Features

### African-Focused Data Integration

- **103+ African facility names** (hospitals, clinics, medical centers)
- **229 African cities** across 5 regions (West, East, Southern, Central, North Africa)
- **303 African names** from 15+ countries
- **54 African healthcare domains**
- **9 African countries** with authentic vehicle plate formats
- Country codes for Angola, Botswana, DRC, Egypt, Ethiopia, Ghana, Kenya, Malawi, Mali, Morocco, Nigeria, Rwanda, South Africa, Sudan, Tanzania, Uganda, Zambia, Zimbabwe, and more

### Format Variations

Each PII type includes 1-13 format variations to provide realistic dataset diversity:
- Names: 13 formats (first name, first+middle, titles, suffixes, etc.)
- Dates: 11 formats (DD/MM/YYYY, ISO 8601, text formats, etc.)
- Emails: 6 formats (username@domain, first.last@domain, initials, etc.)
- FAX Numbers: 8 formats (international, parenthetical, dashes, dots, etc.)
- Phones: 8 formats (same as FAX)
- And more...

### Templates System

Two versions of every dataset:
1. **Full Dataset** - Contains actual PII values for reference/testing
2. **Template Dataset** - Contains `{PLACEHOLDER}` values for secure shared datasets

Example transformation:
```
Full:     "Patient SSN: 123-45-6789."
Template: "Patient SSN: {SSN}."
```

## Performance

Typical generation times (estimate):

- Single PII type: 5-30 seconds
- All 15 generators: 5-10 minutes
- Output size: ~350-400 MB total (varies with sentence_per_format setting)

Memory requirements: ~500 MB - 1 GB

## Data Quality

### Schema Compliance

All generators follow `src/pii_variation_schema.json` specifications exactly:
- Format variations match schema definitions
- Sentence templates from schema
- Entity labels consistent (phi_label from schema)

### Entity Annotation Accuracy

- Character offsets calculated precisely using `str.find()`
- Entity boundaries match actual values in sentences
- All entity types properly labeled

### Realistic Healthcare Context

Sentence templates include:
- Clinical terminology
- Medical workflows (admission, discharge, treatment)
- Healthcare administrative processes
- Insurance and billing language
- Emergency and urgent scenarios

## Error Handling

If a generator fails:
1. Error is caught and logged
2. System continues with next generator
3. Failed generators reported in GENERATION_REPORT.json
4. Exit code indicates success/failure

## Command-Line Options

```
usage: main.py [-h] [--output OUTPUT] [--list-only]

Generate all HIPAA PII datasets

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output directory for datasets
  --list-only, -l       Only list generated files
```

## Examples

### Example 1: Generate to custom location

```bash
python3 main.py --output /data/pii_datasets
```

### Example 2: Generate and immediately list files

```bash
python3 main.py --output ./datasets && python3 main.py --list-only
```

### Example 3: Use in Python

```python
from main import PIIDatasetOrchestrator

orch = PIIDatasetOrchestrator(output_dir='./my_output')
success = orch.run_all()
orch.list_output_files()
```

## Notes

- All generators are reproducible when using a fixed random seed
- Data is generated on-demand; no external APIs required
- All African geographic data is researched and verified
- Compatible with Python 3.7+
- Tested on macOS (can run on Linux/Windows)

## Support

For issues or questions about:
- Generator modifications: Check `src/pii/{type}/generate_*.py`
- Component data: Check `src/pii/{type}/` JSON files
- Schema definitions: Check `src/pii_variation_schema.json`
- Output formats: Check any `*.json` file in `output/`
- Merge pipeline: Check `merge_pii_data.py` and `data/final_pii/`

## Next Steps

1. Run `python3 main.py` to generate all datasets
2. Check `output/` folder for organized datasets
3. Review `GENERATION_REPORT.json` for generation statistics
4. (Optional) Merge contributor data: `python merge_pii_data.py`
5. (Optional) Analyze merged data: `python analyze_final_pii.py`
6. Download final merged datasets from [Drive](https://drive.google.com/placeholder-link) *(link to be added)*
7. Use generated datasets for ML training (full or template versions)
8. Customize individual generators as needed for your use case
