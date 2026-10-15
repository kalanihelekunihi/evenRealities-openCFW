#!/usr/bin/env python3
"""Inventory observed ROM assignments feeding CASE's local formatter arguments."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "g2/build/c-firmware/20261014/case-vformat-current"
DECOMP = ROOT / "g2/tools/manifests/g2-box-ghidra-decomp.c"
FW = ROOT / "g2/blobs/official/g2-2.2.6.10/firmware_box.bin"
OUT = BASE / "dynamic-assignment-census.json"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sha(FW) == "36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374"
    census = json.loads((BASE / "caller-census.json").read_text())
    assert census["status"] == "PASS_BOUNDED_CASE_FORMATTER_CALLER_CENSUS"
    lines = DECOMP.read_text().splitlines()
    payload = FW.read_bytes()[32:]
    out = []
    for call in census["rows"]:
        if call["classification"] != "dynamic_or_local":
            continue
        line_no = call["line"]
        var = call["expression"]
        function_start = max(i + 1 for i in range(line_no) if re.search(r"\bFUN_0800[0-9a-fA-F]{4}\s*\(", lines[i]) and not lines[i].lstrip().startswith("FUN_"))
        assignments = []
        for index in range(function_start, line_no - 1):
            # Exclude writes through the pointer (for example *pcVar1 = '\0').
            match = re.search(r"(?<![\w*])" + re.escape(var) + r"\s*=\s*([^;]+);", lines[index])
            if not match:
                continue
            expr = match.group(1).strip()
            item = {"line": index + 1, "expression": expr}
            # A Ghidra _DAT_ label without '&' denotes a loaded pointer, not
            # a string resident at the address embedded in its label.
            address = re.search(r"0800([0-9a-fA-F]{4})", expr)
            is_direct_rom = bool(re.match(r"(?:s_|&DAT_)", expr))
            if address and is_direct_rom:
                offset = int(address.group(1), 16) + (1 if "+ 1" in expr else 0)
                end = payload.find(b"\0", offset, min(offset + 160, len(payload)))
                if end > offset:
                    value = payload[offset:end]
                    if all(c in (9, 10, 13) or 32 <= c <= 126 for c in value):
                        item.update(rom_address=hex(0x08000000 + offset), format_hex=value.hex(), classification="printable_rom_assignment")
                    else:
                        item["classification"] = "nonprintable_rom_assignment"
                else:
                    item["classification"] = "empty_or_unterminated_rom_assignment"
            else:
                item["classification"] = ("runtime_pointer_assignment" if address
                                          else "nonliteral_assignment")
            assignments.append(item)
        out.append({"call_line": line_no, "variable": var, "function_start_line": function_start,
                    "observed_prior_assignments": assignments,
                    "control_flow_exhaustive": False})
    assert len(out) == 19
    receipt = {"status": "PASS_BOUNDED_CASE_DYNAMIC_ASSIGNMENT_CENSUS",
               "decomp_sha256": sha(DECOMP), "stock_firmware_sha256": sha(FW),
               "parent_census_sha256": sha(BASE / "caller-census.json"),
               "calls": out, "whole_callsite_coverage": False, "whole_case_image_complete": False,
               "limits": ["Textual preceding assignments are candidates, not reaching definitions or control-flow proof.",
                          "Loaded _DAT_ pointers are runtime values, not literal ROM strings; direct ROM labels can still point into data."]}
    OUT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(out), sha(OUT))


if __name__ == "__main__":
    main()
