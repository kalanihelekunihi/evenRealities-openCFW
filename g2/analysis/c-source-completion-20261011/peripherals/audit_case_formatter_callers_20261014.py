#!/usr/bin/env python3
"""Classify retained Ghidra CASE formatter call expressions and ROM strings."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
DECOMP = G2 / "tools/manifests/g2-box-ghidra-decomp.c"
FIRMWARE = G2 / "blobs/official/g2-2.2.6.10/firmware_box.bin"
ORACLE_RECEIPT = G2 / "build/c-firmware/20261014/case-vformat-current/receipt.json"
RECEIPT = G2 / "build/c-firmware/20261014/case-vformat-current/caller-census.json"
FW_SHA = "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert sha(FIRMWARE) == FW_SHA
    oracle = json.loads(ORACLE_RECEIPT.read_text())
    assert oracle["status"] == "PASS_SELECTED_CASE_VFORMAT_EXTENDED_NATIVE_C"
    assert oracle["retained_native_caller_formats"] == 116
    payload = FIRMWARE.read_bytes()[32:]
    rows = []
    formats = set()
    pattern = re.compile(r"FUN_08009170\(([^,)]+)")
    for line_number, line in enumerate(DECOMP.read_text().splitlines(), 1):
        for match in pattern.finditer(line):
            expression = match.group(1).strip()
            address = re.search(r"0800([0-9a-fA-F]{4})", expression)
            row = {"line": line_number, "expression": expression}
            if not address:
                row["classification"] = ("prototype" if expression.startswith("undefined4 ")
                                         else "dynamic_or_local")
            else:
                offset = int(address.group(1), 16) + (1 if "+ 1" in expression else 0)
                row["rom_address"] = hex(0x08000000 + offset)
                end = payload.find(b"\0", offset, min(len(payload), offset + 160))
                if offset >= len(payload) or end < 0:
                    row["classification"] = "out_of_span_or_unterminated"
                else:
                    value = payload[offset:end]
                    if value and all(byte in (9, 10, 13) or 32 <= byte <= 126 for byte in value):
                        row["classification"] = "printable_stock_format"
                        row["format_hex"] = value.hex()
                        formats.add(value)
                    else:
                        row["classification"] = "nonprintable_or_empty"
            rows.append(row)
    counts = Counter(row["classification"] for row in rows)
    assert len(rows) == 255
    assert counts == {"printable_stock_format": 229, "dynamic_or_local": 19,
                      "nonprintable_or_empty": 6, "prototype": 1}
    assert len(formats) == oracle["retained_native_caller_formats"] == 116
    receipt = {
        "status": "PASS_BOUNDED_CASE_FORMATTER_CALLER_CENSUS",
        "decomp": str(DECOMP.relative_to(ROOT)),
        "decomp_sha256": sha(DECOMP),
        "stock_firmware_sha256": FW_SHA,
        "formatter_oracle_receipt": str(ORACLE_RECEIPT.relative_to(ROOT)),
        "formatter_oracle_receipt_sha256": sha(ORACLE_RECEIPT),
        "call_expressions": len(rows),
        "classifications": dict(counts),
        "unique_printable_formats": len(formats),
        "rows": rows,
        "whole_callsite_coverage": False,
        "whole_case_image_complete": False,
        "hardware_proof": False,
        "limits": ["Retained Ghidra expressions are a source inventory, not a native reachability proof.",
                   "Nineteen dynamic/local expressions and six nonprintable address expressions need caller-specific argument evidence.",
                   "The independent linear Thumb BL count is not mapped one-to-one to this decomp expression census."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(rows), len(formats), sha(RECEIPT))


if __name__ == "__main__":
    main()
