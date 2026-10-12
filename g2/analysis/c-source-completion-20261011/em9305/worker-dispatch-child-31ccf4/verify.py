#!/usr/bin/env python3
"""Verify the complete native 31ccf4 body and its symbolic relocations."""

import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
native_path = root.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
target_path = root / "target/source.dis"
native_text, target_text = native_path.read_text(), target_path.read_text()
BASE, END = 0x31CCF4, 0x31CE0E
EXPANSIONS = (0x31CD60, 0x31CD80, 0x31CDF4)
BRANCHES = {0x31CDEE: 0x31CE0C, 0x31CE0A: 0x31CDC0}
CHILDREN = {
    0x31CD0A: (0x33301C, "opencfw_em9305_memset"),
    0x31CD18: (0x33301C, "opencfw_em9305_memset"),
    0x31CD48: (0x332FC4, "opencfw_em9305_memcpy"),
    0x31CD5A: (0x312BC0, "opencfw_em9305_dispatch_child_312bc0"),
    0x31CDC2: (0x317EBC, "opencfw_em9305_init_secondary_time_317ebc"),
    0x31CDDE: (0x3257F4, "opencfw_em9305_dispatch_child_3257f4"),
    0x31CDE8: (0x312DA4, "opencfw_em9305_associated_schedule_insert_312da4"),
}
POINTERS = {
    0x31CD38: (0x31CA0C, "opencfw_em9305_dispatch_callback_31ca0c", "st.as"),
    0x31CD40: (0x31CEB4, "opencfw_em9305_dispatch_callback_31ceb4", "st.as"),
    0x31CDA2: (0x31D43C, "opencfw_em9305_dispatch_callback_31d43c", "st"),
    0x31CDAA: (0x31CBB0, "opencfw_em9305_dispatch_callback_31cbb0", "st"),
}


def parse(content):
    lines, found = content.splitlines(), []
    for index, line in enumerate(lines):
        match = re.match(r"^\s*([0-9a-f]+):\t([0-9a-f ]+)\t(.*)$", line)
        if not match:
            continue
        address = int(match[1], 16)
        if not (BASE <= address < END or 0 <= address < 288):
            continue
        mnemonic = match[3].split("\t")[0].strip()
        if not mnemonic:
            mnemonic = next((part.strip().split("\t")[0] for part in lines[index + 1:index + 5]
                             if "mpywh" in part), "")
        assert mnemonic
        found.append((address, match[2].strip().replace(" ", ""), mnemonic, line))
    return found


native = [row for row in parse(native_text) if BASE <= row[0] < END]
target = [row for row in parse(target_text) if row[0] < 288]
assert len(native) == len(target) == 93
assert sum(len(row[1]) // 2 for row in native) == 282
assert sum(len(row[1]) // 2 for row in target) == 288

for original, built in zip(native, target):
    address = original[0]
    shift = 2 * sum(point < address for point in EXPANSIONS)
    assert built[0] == address - BASE + shift, (original, built)
    if address in EXPANSIONS:
        assert original[2] == "ld_s" and built[2] == "ld"
        old_operand = re.search(r"r(\d+),\[r(\d+),(0x[0-9a-f]+|\d+)\]", original[3])
        new_operand = re.search(r"r(\d+),\[r(\d+),(0x[0-9a-f]+|\d+)\]", built[3])
        assert old_operand and new_operand
        assert (old_operand[1], old_operand[2], int(old_operand[3], 0)) == (new_operand[1], new_operand[2], int(new_operand[3], 0))
    else:
        assert original[2] == built[2], (original, built)
    if address in CHILDREN:
        child_address, symbol = CHILDREN[address]
        assert original[3].rstrip().endswith(f"0x{child_address:x}")
        assert f"{built[0]:x}: R_ARC_S25W_PCREL\t{symbol}" in target_text
    elif address in POINTERS:
        pointer, symbol, mode = POINTERS[address]
        assert original[2] == built[2] == mode
        assert original[1][:8] == built[1][:8]
        assert original[1][8:] == f"{pointer:08x}"
        assert built[1][8:] == "00000000"
        assert f"{built[0] + 4:x}: R_ARC_32_ME\t{symbol}" in target_text
    elif address in BRANCHES:
        destination = BRANCHES[address]
        assert original[3].rstrip().endswith(f"0x{destination:x}")
        assert f"<L{destination:x}>" in built[3]
    elif address not in EXPANSIONS:
        assert original[1] == built[1], (original, built)

receipt = {
    "status": "pass",
    "source_sha256": hashlib.sha256((root / "source.c").read_bytes()).hexdigest(),
    "native_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
    "target_disassembly_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
    "instruction_count": 93,
    "native_body_bytes": 282,
    "target_body_bytes": 288,
    "baseline_ld_expansions": [f"0x{address:x}" for address in EXPANSIONS],
    "child_relocations": {f"0x{address:x}": symbol for address, (_, symbol) in CHILDREN.items()},
    "pointer_relocations": {f"0x{address:x}": symbol for address, (_, symbol, _) in POINTERS.items()},
    "scope": "Full instruction sequence; genuine child and callback relocations; three baseline LD expansions.",
}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
