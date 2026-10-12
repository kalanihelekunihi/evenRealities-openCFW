#!/usr/bin/env python3
"""Independent complete-instruction review of root's native 322bac source."""

import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
candidate = root.parent / "root-setup-322bac"
native_path, target_path = candidate / "native.txt", candidate / "target.txt"
native_text, target_text = native_path.read_text(), target_path.read_text()
BASE, END = 0x322BAC, 0x322C94
CHILDREN = {
    0x322BC0: (0x3188B8, "opencfw_em9305_radio_access_mix_3188b8"),
    0x322BE6: (0x30E3FC, "opencfw_em9305_radio_channel_transform_30e3fc"),
    0x322C1C: (0x332FC4, "opencfw_em9305_memcpy"),
    0x322C68: (0x332FC4, "opencfw_em9305_memcpy"),
}
BRANCHES = {0x322BFE: 0x322C92, 0x322C7A: 0x322C92}


def parse(content):
    result = []
    for line in content.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\t([0-9a-f ]+)\t(\S.*)", line)
        if match:
            result.append((int(match[1], 16), match[2].strip().replace(" ", ""), match[3].split("\t")[0], line))
    return result


native = [row for row in parse(native_text) if BASE <= row[0] < END]
target = [row for row in parse(target_text) if row[0] < 0xEA]
assert len(native) == len(target) == 72
assert sum(len(row[1]) // 2 for row in native) == 232
assert sum(len(row[1]) // 2 for row in target) == 234
for original, built in zip(native, target):
    address = original[0]
    assert built[0] == address - BASE + (2 if address > 0x322C82 else 0)
    if address == 0x322C82:
        assert original[2] == "ld_s" and built[2] == "ld"
        assert "r0,[r0,0]" in original[3] and "r0,[r0]" in built[3]
    else:
        assert original[2] == built[2], (original, built)
    if address in CHILDREN:
        child_address, symbol = CHILDREN[address]
        assert original[3].rstrip().endswith(f"0x{child_address:x}")
        assert f"{built[0]:x}: R_ARC_S25W_PCREL\t{symbol}" in target_text
    elif address in BRANCHES:
        assert original[3].rstrip().endswith(f"0x{BRANCHES[address]:x}")
        assert f"<L{BRANCHES[address]:x}>" in built[3]
    elif address != 0x322C82:
        assert original[1] == built[1], (original, built)

receipt = {
    "status": "pass",
    "source_sha256": hashlib.sha256((candidate / "source.c").read_bytes()).hexdigest(),
    "native_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
    "target_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
    "instruction_count": 72,
    "native_body_bytes": 232,
    "target_body_bytes": 234,
    "baseline_expansion": "322c82 native ld_s r0,[r0,0] -> target full ld r0,[r0]",
    "child_relocations": {f"0x{address:x}": symbol for address, (_, symbol) in CHILDREN.items()},
    "native_indirect_callback": "322c8e jl_s.d [r3]; 322c90 delay slot mov_s r0,r14",
    "scope": "Full instruction sequence and bytes outside child relocations and one LD expansion; indirect callback contract remains open.",
}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
