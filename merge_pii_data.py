#!/usr/bin/env python3
"""
Merge PII datasets from contributor folders.

- Discovers contributor data in data/*_extracted/PHI(*)/ automatically
- Deduplicates by (sentence, start, end, label)
- Skips regeneration if source files unchanged (idempotent)
"""

import json
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Set, Tuple

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = DATA_DIR / "final_pii"
STATE_FILE = OUTPUT_DIR / ".merge_state.json"

# PII type -> candidate subpaths (tried in order until one exists)
PII_PATH_CANDIDATES: Dict[str, List[str]] = {
    "names": ["Names/name_pii_dataset.json", "names/name_pii_dataset.json"],
    "dates": ["Dates/date_pii_dataset.json", "dates/date_pii_dataset.json"],
    "emails": ["Emails/email_pii_dataset.json", "emails/email_pii_dataset.json"],
    "ssn": [
        "Social-Security-Numbers/ssn_pii_dataset.json",
        "ssn/ssn_pii_dataset.json",
    ],
    "mrn": [
        "Medical-Record-Numbers/mrn_pii_dataset.json",
        "mrn/mrn_pii_dataset.json",
    ],
    "account_numbers": [
        "Account-Numbers/account_number_pii_dataset.json",
        "account_number/account_number_pii_dataset.json",
    ],
    "addresses": [
        "Phy-Addresses/address_pii_dataset.json",
        "physical_address/address_pii_dataset.json",
    ],
    "urls": ["urls/url_pii_dataset.json"],
    "vehicle_ids": [
        "vehicle-no/vehicle_id_pii_dataset.json",
        "vehicle_id/vehicle_id_pii_dataset.json",
    ],
    "device_ids": [
        "Device-Serial-Number/device_id_pii_dataset.json",
        "device_id/device_id_pii_dataset.json",
    ],
    "certificates_licenses": [
        "certificate-license/certlic_pii_dataset.json",
        "certificates_licenses/certlic_pii_dataset.json",
    ],
    "fax": ["Fax-Numbers/fax_pii_dataset.json", "fax/fax_pii_dataset.json"],
    "locations": [
        "Geo-Sub-Divisions/geo_sub_divs_dataset.json",
        "location/geo_sub_divs_dataset.json",
    ],
    "phones": [
        "Phone-Numbers/phone_pii_dataset.json",
        "phone/phone_pii_dataset.json",
    ],
    "ip_addresses": [
        "IP-Addresses/ip_pii_dataset.json",
        "ip_address/ip_pii_dataset.json",
    ],
}


def discover_contributor_bases() -> List[Path]:
    """Find PHI(*) folders under data/*_extracted/."""
    bases: List[Path] = []
    if not DATA_DIR.exists():
        return bases
    for extracted_dir in DATA_DIR.glob("*_extracted"):
        if not extracted_dir.is_dir():
            continue
        phi_dirs = list(extracted_dir.glob("PHI(*)"))
        for phi in phi_dirs:
            if phi.is_dir():
                bases.append(phi)
    return sorted(bases)


def find_source_files(pii_name: str, contributor_bases: List[Path]) -> List[Path]:
    """Resolve source file paths for a PII type across all contributors."""
    candidates = PII_PATH_CANDIDATES.get(pii_name, [])
    found: List[Path] = []
    for base in contributor_bases:
        for subpath in candidates:
            path = base / subpath
            if path.exists():
                found.append(path)
                break
    return found


def file_fingerprint(path: Path) -> Tuple[float, int]:
    """Return (mtime, size) for change detection."""
    stat = path.stat()
    return (stat.st_mtime, stat.st_size)


class PIIRecordExtractor:
    """Extract normalized records from contributor dataset schemas."""

    @staticmethod
    def _get_text(record: Dict[str, Any]) -> Optional[str]:
        return record.get("text") or record.get("sentence")

    @staticmethod
    def _get_entity(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        entities = record.get("entities")
        if entities and len(entities) > 0:
            return entities[0]
        entity = record.get("entity")
        if entity:
            return entity
        return None

    @classmethod
    def extract_record(cls, record: Dict[str, Any]) -> Optional[Tuple[str, int, int, str, str]]:
        """
        Extract (sentence, start, end, label, value) from a record.
        Returns None if record is invalid.
        """
        text = cls._get_text(record)
        if not text:
            return None
        entity = cls._get_entity(record)
        if not entity:
            return None
        start = entity.get("start")
        end = entity.get("end")
        label = entity.get("label")
        value = entity.get("value", "")
        if start is None or end is None or not label:
            return None
        return (text, start, end, label, value)

    @classmethod
    def iter_sentences(cls, filepath: Path) -> Generator[Tuple[str, int, int, str, str], None, None]:
        """Yield (sentence, start, end, label, value) from a dataset file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        records_iter = cls._iter_records(data)
        for record in records_iter:
            extracted = cls.extract_record(record)
            if extracted:
                yield extracted

    @staticmethod
    def _iter_records(data: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """Iterate over records from either formats or data structure."""
        for format_data in data.get("formats", {}).values():
            for record in format_data.get("sentences", []):
                yield record
        for record in data.get("data", []):
            yield record


class MergeStateManager:
    """Track source fingerprints to skip redundant merges."""

    def __init__(self, state_path: Path = STATE_FILE):
        self.state_path = state_path
        self._state: Dict[str, List[Dict[str, Any]]] = {}

    def load(self) -> None:
        """Load state from disk if it exists."""
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._state = {}

    def save(self, pii_name: str, source_paths: List[Path]) -> None:
        """Save fingerprints for a PII type."""
        self._state[pii_name] = []
        for path in source_paths:
            mtime, size = file_fingerprint(path)
            self._state[pii_name].append(
                {"path": str(path), "mtime": mtime, "size": size}
            )
        self._state[pii_name].sort(key=lambda x: x["path"])
        self._write()

    def _write(self) -> None:
        """Persist state to disk."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2)

    def is_unchanged(self, pii_name: str, source_paths: List[Path]) -> bool:
        """Return True if sources match stored fingerprints."""
        stored = self._state.get(pii_name)
        if not stored:
            return False
        if len(stored) != len(source_paths):
            return False
        stored_paths = sorted(s["path"] for s in stored)
        current_paths = sorted(str(p) for p in source_paths)
        if stored_paths != current_paths:
            return False
        for path in source_paths:
            mtime, size = file_fingerprint(path)
            match = next(
                (s for s in stored if s["path"] == str(path)),
                None,
            )
            if not match or match["mtime"] != mtime or match["size"] != size:
                return False
        return True


class PIIMerger:
    """Merge contributor datasets with deduplication and change detection."""

    def __init__(
        self,
        output_dir: Path = OUTPUT_DIR,
        state_file: Path = STATE_FILE,
        force: bool = False,
    ):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = PIIRecordExtractor()
        self.state = MergeStateManager(state_file)
        self.force = force
        self._contributor_bases: Optional[List[Path]] = None

    def _get_contributor_bases(self) -> List[Path]:
        if self._contributor_bases is None:
            self._contributor_bases = discover_contributor_bases()
        return self._contributor_bases

    def _load_records(self, filepath: Path) -> List[Dict[str, Any]]:
        records = []
        for sentence, start, end, label, value in self.extractor.iter_sentences(filepath):
            records.append(
                {
                    "sentence": sentence,
                    "start": start,
                    "end": end,
                    "label": label,
                    "value": value,
                }
            )
        return records

    def _deduplicate_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates by (sentence, start, end, label)."""
        seen: Set[Tuple[str, int, int, str]] = set()
        unique: List[Dict[str, Any]] = []
        for rec in records:
            key = (rec["sentence"], rec["start"], rec["end"], rec["label"])
            if key not in seen:
                seen.add(key)
                unique.append(rec)
        return unique

    def merge_pii_type(self, pii_name: str) -> Tuple[int, bool]:
        """
        Merge all contributor data for one PII type.
        Returns (count, was_written). was_written=False if skipped (unchanged).
        """
        contributor_bases = self._get_contributor_bases()
        source_paths = find_source_files(pii_name, contributor_bases)
        output_filename = f"{pii_name}.json"
        out_path = self.output_dir / output_filename

        if not source_paths:
            return 0, False

        self.state.load()
        if (
            not self.force
            and out_path.exists()
            and self.state.is_unchanged(pii_name, source_paths)
        ):
            with open(out_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            return len(existing), False

        records: List[Dict[str, Any]] = []
        for path in source_paths:
            records.extend(self._load_records(path))
        records = self._deduplicate_records(records)

        output_data = []
        for idx, rec in enumerate(records, start=1):
            output_data.append(
                {
                    "id": idx,
                    "sentence": rec["sentence"],
                    "start": rec["start"],
                    "end": rec["end"],
                    "label": rec["label"],
                    "value": rec["value"],
                }
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        self.state.save(pii_name, source_paths)
        return len(output_data), True

    def run_all(self) -> Dict[str, Tuple[int, bool]]:
        """Merge all PII types. Returns {(name): (count, was_written)}."""
        self.state.load()
        results = {}
        for pii_name in PII_PATH_CANDIDATES:
            count, written = self.merge_pii_type(pii_name)
            results[pii_name] = (count, written)
        return results


def main() -> None:
    """Run merger and print summary."""
    import argparse

    parser = argparse.ArgumentParser(description="Merge PII datasets from contributors")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Regenerate output even if sources unchanged",
    )
    args = parser.parse_args()

    merger = PIIMerger(force=args.force)
    results = merger.run_all()
    total = sum(r[0] for r in results.values())
    written = sum(1 for r in results.values() if r[1])
    skipped = len(results) - written

    print("PII datasets:")
    for name, (count, was_written) in results.items():
        status = "(unchanged)" if not was_written and count > 0 else ""
        print(f"  {name}: {count:,} {status}")
    print(f"  Total: {total:,}")
    print(f"Output: {OUTPUT_DIR}")
    if skipped > 0:
        print(f"Skipped {skipped} types (no changes); use --force to regenerate")


if __name__ == "__main__":
    main()
