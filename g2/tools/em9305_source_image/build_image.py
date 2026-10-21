#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build an EM9305 record-table image from an explicit source-record layout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from record_package import Record, RecordPackageError, build_package, parse_package


def load_layout(path: Path) -> tuple[tuple[Record, ...], tuple[int, ...]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != {"records", "erase_sectors"}:
        raise RecordPackageError("layout must contain only records and erase_sectors")
    raw_records = value["records"]
    raw_sectors = value["erase_sectors"]
    if not isinstance(raw_records, list) or not isinstance(raw_sectors, list):
        raise RecordPackageError("layout records and erase_sectors must be arrays")
    records = []
    for index, item in enumerate(raw_records):
        if not isinstance(item, dict) or set(item) != {"address", "path"}:
            raise RecordPackageError(f"layout record {index} has an invalid shape")
        address = item["address"]
        if isinstance(address, str):
            address = int(address, 0)
        if type(address) is not int:
            raise RecordPackageError(f"layout record {index} address is invalid")
        record_name = item["path"]
        if not isinstance(record_name, str) or not record_name:
            raise RecordPackageError(f"layout record {index} path is invalid")
        relative_path = Path(record_name)
        if relative_path.is_absolute():
            raise RecordPackageError(f"layout record {index} path must be relative")
        record_path = (path.parent / relative_path).resolve()
        try:
            record_path.relative_to(path.parent)
        except ValueError as error:
            raise RecordPackageError(
                f"layout record {index} path escapes the layout directory") from error
        records.append(Record(address, record_path.read_bytes()))
    return tuple(records), tuple(raw_sectors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    records, erase_sectors = load_layout(args.layout.resolve())
    package = build_package(records, erase_sectors)
    parsed = parse_package(package)
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != package:
            raise SystemExit("EM9305 source image is missing or stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(package)
    print(json.dumps({
        "status": "em9305-record-package-built",
        "records": len(parsed.records),
        "erase_sectors": len(parsed.erase_sectors),
        "metadata_size": parsed.metadata_size,
        "payload_size": parsed.payload_size,
        "package_size": len(package),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as error:
        raise SystemExit(f"EM9305 source-image build failed: {error}") from error
