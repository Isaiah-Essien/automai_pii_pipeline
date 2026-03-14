#!/usr/bin/env python3
"""
Utility script to add output_dir support to all PII generators.
"""

import os
import re
from pathlib import Path

def add_output_dir_support(file_path):
    """Add output_dir support to a generator file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract class name
    class_match = re.search(r'class (\w+)\:', content)
    if not class_match:
        print(f"  ✗ Could not find class in {file_path}")
        return False
    
    class_name = class_match.group(1)
    
    # Check if already updated
    if 'self.output_dir' in content and 'set_output_dir' in content:
        print(f"  ✓ Already has output_dir support")
        return True
    
    # Find __init__ method
    init_pattern = rf'(class {class_name}:\s+def __init__\(self\):.*?\n        """[^"]*""")\n'
    init_match = re.search(init_pattern, content, re.DOTALL)
    
    if not init_match:
        print(f"  ✗ Could not find __init__ in {class_name}")
        return False
    
    # Add output_dir initialization and set_output_dir method
    init_end = init_match.end()
    
    # Check what comes after __init__ docstring
    after_init = content[init_end:init_end+50]
    
    # Add the initialization after docstring
    output_dir_init = "\n        self.output_dir = None  # Will be set via set_output_dir()\n"
    
    # Insert after docstring
    content_updated = content[:init_end] + output_dir_init + content[init_end:]
    
    # Add set_output_dir method after __init__
    set_output_dir_method = f"""    
    def set_output_dir(self, output_dir: str):
        \"\"\"Set custom output directory for generated files.\"\"\"
        self.output_dir = output_dir
"""
    
    # Find where to insert (after __init__, before next method)
    next_method = re.search(r'\n    def ', content_updated[init_end+len(output_dir_init):])
    if next_method:
        insert_pos = init_end + len(output_dir_init) + next_method.start()
        content_updated = content_updated[:insert_pos] + set_output_dir_method + content_updated[insert_pos:]
    
    with open(file_path, 'w') as f:
        f.write(content_updated)
    
    return True

def update_save_methods(file_path, placeholder_name):
    """Update save_dataset and save_template_dataset methods to use output_dir."""
    with open(file_path, 'r')as f:
        content = f.read()
    
    file_patterns = {
        'generate_name_pii.py': ('name_pii_dataset.json', 'name_pii_templates.json'),
        'generate_date_pii.py': ('date_pii_dataset.json', 'date_pii_templates.json'),
        'generate_email_pii.py': ('email_pii_dataset.json', 'email_pii_templates.json'),
        'generate_mrn_pii.py': ('mrn_pii_dataset.json', 'mrn_pii_templates.json'),
        'generate_ip_pii.py': ('ip_pii_dataset.json', 'ip_pii_templates.json'),
        'generate_account_number_pii.py': ('account_pii_dataset.json', 'account_pii_templates.json'),
        'generate_address_pii.py': ('address_pii_dataset.json', 'address_pii_templates.json'),
        'generate_url_pii.py': ('url_pii_dataset.json', 'url_pii_templates.json'),
        'generate_vehicle_id_pii.py': ('vehicle_id_pii_dataset.json', 'vehicle_id_pii_templates.json'),
        'generate_ssn_pii.py': ('ssn_pii_dataset.json', 'ssn_pii_templates.json'),
        'generate_device_id_pii.py': ('device_id_pii_dataset.json', 'device_id_pii_templates.json'),
        'generate_certlic_pii.py': ('certlic_pii_dataset.json', 'certlic_pii_templates.json'),
        'generate_fax_pii.py': ('fax_pii_dataset.json', 'fax_pii_templates.json'),
        'generate_phone_pii.py': ('phone_pii_dataset.json', 'phone_pii_templates.json'),
    }
    
    basename = os.path.basename(file_path)
    if basename not in file_patterns:
        return True
    
    dataset_file, template_file = file_patterns[basename]
    
    # Update save_dataset
    dataset_pattern = rf'os\.path\.join\(os\.path\.dirname\(__file__\), [\'\"]{dataset_file}[\'\"]'
    if re.search(dataset_pattern, content):
        replacement = f'os.path.join(self.output_dir if self.output_dir else os.path.dirname(__file__), \'{dataset_file}\''
        content = re.sub(dataset_pattern, replacement, content)
    
    # Update save_template_dataset
    template_pattern = rf'os\.path\.join\(os\.path\.dirname\(__file__\), [\'\"]{template_file}[\'\"]'
    if re.search(template_pattern, content):
        replacement = f'os.path.join(self.output_dir if self.output_dir else os.path.dirname(__file__), \'{template_file}\''
        content = re.sub(template_pattern, replacement, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

# Main process
pii_dir = Path('/Users/cococe/Desktop/automai_pii_pipeline/src/pii')
generator_files = list(pii_dir.glob('*/generate_*_pii.py'))

print("Updating PII generators for output_dir support...")
print("=" * 60)

for gen_file in sorted(generator_files):
    print(f"\n{gen_file.parent.name}/")
    
    # Add output_dir initialization
    if add_output_dir_support(str(gen_file)):
        # Update save methods
        if update_save_methods(str(gen_file), gen_file.parent.name):
            print(f"  ✓ Updated successfully")
        else:
            print(f"  ⚠ Partially updated")
    else:
        print(f"  ✗ Failed to update")

print("\n" + "=" * 60)
print("✓ Generator update process complete!")
