#!/usr/bin/env python3
"""Recheck every native 322c94 instruction against the pinned ARC object."""

import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
native_path = root.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
target_path = root / "target/source.dis"
native_text, target_text = native_path.read_text(), target_path.read_text()
BASE, END = 0x322C94, 0x322D66
EXPANSIONS = (0x322CD0, 0x322CD2, 0x322CE2, 0x322CEC, 0x322D4A)
BRANCH_SHIFTS = {0x322CD6: 0x322CE6, 0x322CE4: 0x322CEE}
CHILDREN = {
    0x322CCA: (0x302748, "opencfw_em9305_sleep_sync_divide"),
    0x322D20: (0x332FC4, "opencfw_em9305_memcpy"),
    0x322D32: (0x332FC4, "opencfw_em9305_memcpy"),
    0x322D40: (0x317334, "opencfw_em9305_radio_encrypt_seed_317334"),
    0x322D5A: (0x317EA4, "opencfw_em9305_mode_callback_child_317ea4"),
}


def instructions(text):
    lines = text.splitlines()
    found = []
    for index, line in enumerate(lines):
        match = re.match(r"^\s*([0-9a-f]+):\t([0-9a-f ]+)\t(.*)$", line)
        if not match:
            continue
        address = int(match[1], 16)
        if not (BASE <= address < END or 0 <= address < 220):
            continue
        mnemonic = match[3].split("\t")[0].strip()
        if not mnemonic:
            mnemonic = next((part.strip().split("\t")[0] for part in lines[index + 1:index + 5]
                             if "mpywhl" in part), "")
        assert mnemonic
        found.append((address, match[2].strip().replace(" ", ""), mnemonic, line))
    return found


native = [item for item in instructions(native_text) if BASE <= item[0] < END]
target = [item for item in instructions(target_text) if item[0] < 220]
assert len(native) == len(target) == 77
assert sum(len(item[1]) // 2 for item in native) == 210
assert sum(len(item[1]) // 2 for item in target) == 220
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
    elif address in BRANCH_SHIFTS:
        destination = BRANCH_SHIFTS[address]
        assert original[3].rstrip().endswith(f"0x{destination:x}")
        assert f"<L{destination:x}>" in built[3]
    elif address not in EXPANSIONS:
        assert original[1] == built[1], (original, built)

receipt = {
    "status": "pass",
    "source_sha256": hashlib.sha256((root / "source.c").read_bytes()).hexdigest(),
    "native_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
    "target_disassembly_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
    "instruction_count": 77,
    "native_body_bytes": 210,
    "target_body_bytes": 220,
    "baseline_ld_expansions": [f"0x{address:x}" for address in EXPANSIONS],
    "child_relocations": {f"0x{address:x}": symbol for address, (_, symbol) in CHILDREN.items()},
    "scope": "All named ISA instructions, child targets and non-relocated bytes; five full baseline LDs expand by ten bytes.",
}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
