#!/usr/bin/env python3
"""
PII Dataset Generator - Main Orchestrator
Generates all 14+ HIPAA PII datasets and consolidates them in an output folder.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class PIIDatasetOrchestrator:
    """Orchestrates generation of all PII datasets."""
    
    def __init__(self, output_dir: str = None):
        """Initialize the orchestrator."""
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'output')
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Define all generators with their relative paths, module names, and configs
        self.generators_config = [
            {
                'name': 'names',
                'module_path': 'pii.names.generate_name_pii',
                'class_name': 'NamePIIGenerator',
                'sentences_per_format': 10000,
                'num_formats': 13,
                'output_prefix': 'name_pii',
            },
            {
                'name': 'dates',
                'module_path': 'pii.dates.generate_date_pii',
                'class_name': 'DatePIIGenerator',
                'sentences_per_format': 10000,
                'num_formats': 11,
                'output_prefix': 'date_pii',
            },
            {
                'name': 'emails',
                'module_path': 'pii.emails.generate_email_pii',
                'class_name': 'EmailPIIGenerator',
                'sentences_per_format': 10000,
                'num_formats': 6,
                'output_prefix': 'email_pii',
            },
            {
                'name': 'mrn',
                'module_path': 'pii.mrn.generate_mrn_pii',
                'class_name': 'MRNPIIGenerator',
                'sentences_per_format': 20000,
                'num_formats': 5,
                'output_prefix': 'mrn_pii',
            },
            {
                'name': 'ip_address',
                'module_path': 'pii.ip.generate_ip_pii',
                'class_name': 'IPAddressGenerator',
                'sentences_per_format': 50000,
                'num_formats': 1,
                'output_prefix': 'ip_pii',
            },
            {
                'name': 'account_number',
                'module_path': 'pii.account_no.generate_account_number_pii',
                'class_name': 'AccountNumberGenerator',
                'sentences_per_format': 16667,
                'num_formats': 3,
                'output_prefix': 'account_number_pii',
            },
            {
                'name': 'physical_address',
                'module_path': 'pii.phy_address.generate_address_pii',
                'class_name': 'AddressGenerator',
                'sentences_per_format': 10000,
                'num_formats': 7,
                'output_prefix': 'address_pii',
            },
            {
                'name': 'urls',
                'module_path': 'pii.urls.generate_url_pii',
                'class_name': 'URLGenerator',
                'sentences_per_format': 10000,
                'num_formats': 3,
                'output_prefix': 'url_pii',
            },
            {
                'name': 'vehicle_id',
                'module_path': 'pii.vehicle_no.generate_vehicle_id_pii',
                'class_name': 'VehicleIDGenerator',
                'sentences_per_format': 26667,
                'num_formats': 3,
                'output_prefix': 'vehicle_id_pii',
            },
            {
                'name': 'ssn',
                'module_path': 'pii.ssn.generate_ssn_pii',
                'class_name': 'SSNGenerator',
                'sentences_per_format': 10000,
                'num_formats': 5,
                'output_prefix': 'ssn_pii',
            },
            {
                'name': 'device_id',
                'module_path': 'pii.device_sn.generate_device_id_pii',
                'class_name': 'DeviceIDGenerator',
                'sentences_per_format': 25000,
                'num_formats': 4,
                'output_prefix': 'device_id_pii',
            },
            {
                'name': 'certificates_licenses',
                'module_path': 'pii.cert_license.generate_certlic_pii',
                'class_name': 'CertificateLicenseGenerator',
                'sentences_per_format': 10000,
                'num_formats': 6,
                'output_prefix': 'certlic_pii',
            },
            {
                'name': 'fax',
                'module_path': 'pii.faxs.generate_fax_pii',
                'class_name': 'FAXGenerator',
                'sentences_per_format': 10000,
                'num_formats': 8,
                'output_prefix': 'fax_pii',
            },
            {
                'name': 'location',
                'module_path': 'pii.geo_sub_divs.generate_geo_sub_divs_pii',
                'class_name': 'LocationGenerator',
                'sentences_per_format': 10000,
                'num_formats': 3,
                'output_prefix': 'geo_sub_divs',
            },
            {
                'name': 'phone',
                'module_path': 'pii.phones.generate_phone_pii',
                'class_name': 'PhonePIIGenerator',
                'sentences_per_format': 12500,
                'num_formats': 8,
                'output_prefix': 'phone_pii',
            },
        ]
        
        self.results = {}
    
    def run_all(self, verbose: bool = True):
        """Run all PII generators."""
        print("=" * 70)
        print("PII DATASET GENERATION SYSTEM")
        print("=" * 70)
        print(f"\nOutput Directory: {self.output_dir}")
        print(f"\nGenerators to Execute: {len(self.generators_config)}")
        print("-" * 70)
        
        total_sentences = 0
        failed_generators = []
        
        for idx, config in enumerate(self.generators_config, 1):
            try:
                name = config['name']
                print(f"\n[{idx}/{len(self.generators_config)}] Running {name.upper()} Generator...")
                
                # Create output subdirectory for this generator
                gen_output_dir = self.output_dir / name
                gen_output_dir.mkdir(parents=True, exist_ok=True)
                
                # Dynamically import generator
                module_path = config['module_path']
                class_name = config['class_name']
                
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    GeneratorClass = getattr(module, class_name)
                except (ImportError, AttributeError) as e:
                    raise Exception(f"Could not import {class_name} from {module_path}: {str(e)}")
                
                # Instantiate and run generator
                generator = GeneratorClass()
                
                # Try to set output_dir if method exists
                if hasattr(generator, 'set_output_dir'):
                    generator.set_output_dir(str(gen_output_dir))
                    print(f"    Setting output directory: {gen_output_dir}")
                
                # Run generator
                generator.run(sentences_per_format=config['sentences_per_format'])
                
                # Copy output files to output directory if they weren't already saved there
                self.consolidate_output_files(config, gen_output_dir)
                
                sentences_generated = config['sentences_per_format'] * config['num_formats']
                total_sentences += sentences_generated
                
                self.results[name] = {
                    'status': 'success',
                    'sentences': sentences_generated,
                    'output_dir': str(gen_output_dir)
                }
                
                print(f"    ✓ {name.upper()} generation complete!")
                
            except Exception as e:
                print(f"    ✗ ERROR generating {name}: {str(e)}")
                failed_generators.append((name, str(e)))
                self.results[name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        # Summary Report
        print("\n" + "=" * 70)
        print("GENERATION SUMMARY")
        print("=" * 70)
        print(f"\nTotal Sentences Generated: {total_sentences:,}")
        print(f"Successful Generators: {len(self.generators_config) - len(failed_generators)}/{len(self.generators_config)}")
        
        if failed_generators:
            print(f"\nFailed Generators ({len(failed_generators)}):")
            for name, error in failed_generators:
                print(f"  - {name}: {error}")
        else:
            print("\n✓ All generators completed successfully!")
        
        print(f"\nOutput Directory: {self.output_dir}")
        print("=" * 70)
        
        # Generate summary report
        self.generate_summary_report()
        
        return len(failed_generators) == 0
    
    def consolidate_output_files(self, config, target_dir):
        """
        Copy generated files from source to target directory if they exist in original location.
        """
        name = config['name']
        
        # Mapping of generator names to their source folders and file prefixes
        source_mapping = {
            'names': ('names', 'name_pii'),
            'dates': ('dates', 'date_pii'),
            'emails': ('emails', 'email_pii'),
            'mrn': ('mrn', 'mrn_pii'),
            'ip_address': ('ip', 'ip_pii'),
            'account_number': ('account_no', 'account_number_pii'),
            'physical_address': ('phy_address', 'address_pii'),
            'urls': ('urls', 'url_pii'),
            'vehicle_id': ('vehicle_no', 'vehicle_id_pii'),
            'ssn': ('ssn', 'ssn_pii'),
            'device_id': ('device_sn', 'device_id_pii'),
            'certificates_licenses': ('cert_license', 'certlic_pii'),
            'fax': ('faxs', 'fax_pii'),
            'location': ('geo_sub_divs', 'geo_sub_divs'),
            'phone': ('phones', 'phone_pii'),
        }
        
        if name not in source_mapping:
            return
        
        folder, file_prefix = source_mapping[name]
        source_dir = os.path.join(os.path.dirname(__file__), f'src/pii/{folder}')
        
        # Copy generated files if they exist in source
        for suffix in ['_dataset.json', '_templates.json', '_sentences.json']:
            src_file = os.path.join(source_dir, f'{file_prefix}{suffix}')
            if os.path.exists(src_file):
                dst_file = os.path.join(target_dir, f'{file_prefix}{suffix}')
                shutil.copy2(src_file, dst_file)
    
    def generate_summary_report(self):
        """Generate a summary report of all generated datasets."""
        report_file = self.output_dir / 'GENERATION_REPORT.json'
        
        summary = {
            "output_directory": str(self.output_dir),
            "generators": self.results,
            "total_generators": len(self.generators_config),
            "successful": sum(1 for r in self.results.values() if r['status'] == 'success'),
            "failed": sum(1 for r in self.results.values() if r['status'] == 'failed'),
        }
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nReport saved to: {report_file}")
    
    def list_output_files(self):
        """List all generated output files."""
        print("\n" + "=" * 70)
        print("GENERATED FILES")
        print("=" * 70)
        
        for subdir in sorted(self.output_dir.iterdir()):
            if subdir.is_dir() and subdir.name not in ['.git', '__pycache__']:
                files = list(subdir.glob('*.json'))
                if files:
                    print(f"\n{subdir.name}/")
                    for file in sorted(files):
                        size_mb = file.stat().st_size / (1024 * 1024)
                        print(f"  - {file.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate all HIPAA PII datasets')
    parser.add_argument('--output', '-o', help='Output directory for datasets', default=None)
    parser.add_argument('--list-only', '-l', action='store_true', help='Only list generated files')
    
    args = parser.parse_args()
    
    orchestrator = PIIDatasetOrchestrator(output_dir=args.output)
    
    if args.list_only:
        orchestrator.list_output_files()
    else:
        success = orchestrator.run_all()
        orchestrator.list_output_files()
        sys.exit(0 if success else 1)
