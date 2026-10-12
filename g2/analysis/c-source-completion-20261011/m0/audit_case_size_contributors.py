#!/usr/bin/env python3
"""Bounded CASE source/native function-size crosswalk; no firmware output."""
from pathlib import Path
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ELF = HERE / "case_semantic_corrected_optimized.elf"
CATALOGS = (
    ROOT / "g2/research/corpus/case/ghidra/open-2026-09-29/functions-000.jsonl",
    ROOT / "g2/research/corpus/case/ghidra/final-frontier/functions.jsonl",
)

native = {}
for catalog in CATALOGS:
    for line in catalog.read_text().splitlines():
        row = json.loads(line)
        if row.get("address") is not None:
            native[int(row["address"])] = int(row["size"])

nm = subprocess.check_output(("arm-none-eabi-nm", "-S", "--size-sort", "-r", str(ELF)), text=True)
matched = []
source_text_bytes = 0
source_text_count = 0
for line in nm.splitlines():
    match = re.match(r"^[0-9a-fA-F]+\s+([0-9a-fA-F]+)\s+[tT]\s+(\S+)$", line)
    if not match:
        continue
    size = int(match.group(1), 16)
    name = match.group(2)
    source_text_bytes += size
    source_text_count += 1
    suffix = re.search(r"_([0-9a-fA-F]{4,8})$", name)
    if suffix is None:
        continue
    native_address = 0x08000000 + int(suffix.group(1), 16)
    if native_address in native:
        matched.append({"name": name, "native_address": f"0x{native_address:08x}",
                        "source_bytes": size, "native_bytes": native[native_address],
                        "delta_bytes": size - native[native_address]})

matched.sort(key=lambda row: (-row["delta_bytes"], row["name"]))
result = {
    "status": "PASS_BOUNDED_SIZE_CROSSWALK",
    "elf": str(ELF.relative_to(ROOT)),
    "native_catalog_functions": len(native),
    "source_text_symbols": source_text_count,
    "source_text_symbol_bytes": source_text_bytes,
    "exact_address_matches": len(matched),
    "matches": matched,
    "limit": "Native catalogs cover a subset of functions. Symbol suffixes are native addresses only for exact matches; function boundaries and source composition can differ. This is not a whole-image byte budget or permission to remove bodies.",
}
output = HERE / "case-size-contributors-receipt.json"
output.write_text(json.dumps(result, indent=2) + "\n")
print(f"{len(matched)} exact native/source size matches; largest delta {matched[0]['delta_bytes']:+d} bytes")
