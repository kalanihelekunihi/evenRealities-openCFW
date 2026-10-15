#!/usr/bin/env python3
"""Measure a fresh experimental CASE C ELF against stock payload geometry."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_box.bin"
STOCK_SHA = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
READELF = Path("/opt/homebrew/bin/arm-none-eabi-readelf")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", type=Path, default=HERE / "case_absolute_current_round.elf")
    parser.add_argument("--output", type=Path, default=HERE / "case-absolute-layout-audit.json")
    args = parser.parse_args()
    elf_path = args.elf.resolve()
    assert digest(STOCK) == STOCK_SHA
    stock_payload_bytes = len(STOCK.read_bytes()) - 32
    listing = subprocess.check_output([str(READELF), "-l", str(elf_path)], text=True)
    entry = re.search(r"Entry point (0x[0-9a-fA-F]+)", listing)
    assert entry is not None
    loads = re.findall(
        r"(?m)^\s*LOAD\s+0x[0-9a-fA-F]+\s+(0x[0-9a-fA-F]+)\s+"
        r"0x[0-9a-fA-F]+\s+(0x[0-9a-fA-F]+)\s+(0x[0-9a-fA-F]+)",
        listing,
    )
    assert len(loads) == 1, loads
    load_address, file_size, memory_size = (int(part, 16) for part in loads[0])
    assert load_address == 0x08000000 and file_size == memory_size
    undefined = subprocess.check_output(
        ["/opt/homebrew/bin/arm-none-eabi-nm", "-u", str(elf_path)], text=True).strip()
    assert not undefined, undefined
    overflow = file_size - stock_payload_bytes
    result = {
        "status": "EXPERIMENTAL_LAYOUT_OVERFLOW" if overflow > 0 else "EXPERIMENTAL_LAYOUT_FITS",
        "source_elf": str(elf_path.relative_to(ROOT)),
        "source_elf_sha256": digest(elf_path),
        "stock_wrapper_sha256": STOCK_SHA,
        "stock_payload_bytes": stock_payload_bytes,
        "stock_reset_entry": "0x08000145",
        "experimental_elf_entry": entry.group(1),
        "experimental_load_address": hex(load_address),
        "experimental_load_bytes": file_size,
        "overflow_bytes": overflow,
        "undefined_symbols": [],
        "source_complete": False,
        "limits": [
            "Absolute source link proves relocation resolution under the experimental script only.",
            "Startup entry, native section placements, checksums and packaging are unqualified.",
            "No executable-byte equality, initialized-data or physical-device proof.",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in
                      ("status", "experimental_load_bytes", "overflow_bytes",
                       "experimental_elf_entry")}))


if __name__ == "__main__":
    main()
