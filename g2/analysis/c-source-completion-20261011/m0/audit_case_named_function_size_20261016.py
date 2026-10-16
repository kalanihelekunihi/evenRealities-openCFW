#!/usr/bin/env python3
"""Compare named CASE C function sizes with authenticated Ghidra envelopes."""
import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
ELF = G2 / "build/c-firmware/20261015/case-gc-size-frontier/case-current-oz-mixed-fixed-reset.elf"
BASE_RECEIPT = ELF.parent / "mixed-oz-receipt.json"
CATALOGUE = G2 / "tools/manifests/g2-box-ghidra-functions.tsv"
STOCK = G2 / "blobs/official/g2-2.2.6.10/firmware_box.bin"
OUT = G2 / "build/c-firmware/20261016/case-named-function-size"
PIN = "773b6d4cfdaf0a5a74a557e3babe8222a0ae813436b76a7437c1096d2c60d677"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    base = json.loads(BASE_RECEIPT.read_text())
    if base["status"] != "PASS_EXPERIMENTAL_CASE_MIXED_OZ_FIXED_RESET_FRONTIER" or \
            base["elf_sha256"] != sha(ELF) or base["overflow_bytes"] != 7851:
        raise RuntimeError("CASE mixed-Oz baseline changed")
    payload = STOCK.read_bytes()[32:]
    if hashlib.sha256(payload).hexdigest() != PIN:
        raise RuntimeError("CASE stock payload changed")
    native = {}
    with CATALOGUE.open(newline="") as stream:
        for row in csv.DictReader(stream, delimiter="\t"):
            address = int(row["entry"], 16)
            if address in native:
                raise RuntimeError(f"duplicate native entry {address:#x}")
            native[address] = int(row["size"])
    with ELF.open("rb") as stream:
        image = ELFFile(stream)
        section = image.get_section_by_name(".text")
        start = section["sh_addr"]
        end = start + section["sh_size"]
        ranges = []
        function_symbols = 0
        for symbol in image.get_section_by_name(".symtab").iter_symbols():
            if symbol["st_info"]["type"] != "STT_FUNC" or not symbol["st_size"]:
                continue
            address = symbol["st_value"]
            if start <= address < end:
                ranges.append((address, min(address + symbol["st_size"], end)))
                function_symbols += 1
    ranges.sort()
    union = []
    for start_address, end_address in ranges:
        if union and start_address <= union[-1][1]:
            union[-1] = (union[-1][0], max(union[-1][1], end_address))
        else:
            union.append((start_address, end_address))
    function_union_bytes = sum(b - a for a, b in union)
    nonfunction_text_bytes = section["sh_size"] - function_union_bytes
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only",
                                      "--print-size", "-S", str(ELF)], text=True)
    matched = []
    named_unmatched = []
    for line in output.splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[2] not in ("T", "t"):
            continue
        name = parts[3]
        suffix = re.search(r"_([0-9a-f]{4,5})$", name)
        if suffix is None:
            continue
        address = 0x08000000 + int(suffix.group(1), 16)
        compiled = int(parts[1], 16)
        if address not in native:
            named_unmatched.append({"symbol": name, "native_address": hex(address),
                                    "compiled_bytes": compiled})
            continue
        stock = native[address]
        matched.append({"symbol": name, "native_address": hex(address),
                        "compiled_bytes": compiled, "catalogue_bytes": stock,
                        "delta_bytes": compiled - stock})
    matched.sort(key=lambda row: (-row["delta_bytes"], row["native_address"]))
    if len(matched) != 38 or sum(row["delta_bytes"] for row in matched) != -4898:
        raise RuntimeError("CASE named function size frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    result = {"status": "PASS_EXPERIMENTAL_CASE_NAMED_FUNCTION_SIZE_TRIAGE",
              "case_payload_sha256": PIN, "baseline_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
              "baseline_receipt_sha256": sha(BASE_RECEIPT),
              "experimental_elf": str(ELF.relative_to(ROOT)), "experimental_elf_sha256": sha(ELF),
              "catalogue": str(CATALOGUE.relative_to(ROOT)), "catalogue_sha256": sha(CATALOGUE),
              "native_catalogue_functions": len(native),
              "native_catalogue_envelope_bytes": sum(native.values()),
              "candidate_text_bytes": section["sh_size"],
              "candidate_function_symbols": function_symbols,
              "candidate_function_union_bytes": function_union_bytes,
              "candidate_text_bytes_outside_function_symbols": nonfunction_text_bytes,
              "matched_function_count": len(matched),
              "matched_net_delta_bytes": sum(row["delta_bytes"] for row in matched),
              "experimental_payload_overflow_bytes": base["overflow_bytes"],
              "matched": matched, "named_without_catalogue_entry": named_unmatched,
              "limits": ["Ghidra function envelopes and C symbol sizes are diagnostic, not byte-identical body proof.",
                         "The native catalogue may omit or misclassify functions; unmatched source symbols are not automatically excess code.",
                         "Only names ending in a native address are compared; this is not full function coverage.",
                         "The unmatched sections, linker padding and placement must be examined before attributing overflow."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], len(matched), result["matched_net_delta_bytes"], sha(path))

if __name__ == "__main__":
    main()
