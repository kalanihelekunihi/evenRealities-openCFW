#!/usr/bin/env python3
"""Verify the full native 3257f4 body and child call relocations."""

import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
native_path = root.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
target_path = root / "target/source.dis"
native_text, target_text = native_path.read_text(), target_path.read_text()


def parse(text):
    rows = []
    for line in text.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\t([0-9a-f ]+)\t(\S.*)", line)
        if match:
            rows.append((int(match[1], 16), match[2].strip().replace(" ", ""), match[3].split("\t")[0], line))
    return rows


native = [row for row in parse(native_text) if 0x3257F4 <= row[0] < 0x325854]
target = [row for row in parse(target_text) if row[0] < 98]
assert len(native) == len(target) == 33
assert sum(len(row[1]) // 2 for row in native) == 96
assert sum(len(row[1]) // 2 for row in target) == 98
children = (0x325812, 0x32582E)
for original, built in zip(native, target):
    address = original[0]
    assert built[0] == address - 0x3257F4 + (2 if address > 0x325848 else 0)
    if address == 0x325848:
        assert original[2] == "ld_s" and built[2] == "ld"
        assert "r0,[r0,0]" in original[3] and "r0,[r0]" in built[3]
    else:
        assert original[2] == built[2], (original, built)
    if address in children:
        assert original[3].rstrip().endswith("0x30e5a4")
        assert f"{built[0]:x}: R_ARC_S25W_PCREL\topencfw_em9305_dispatch_child_30e5a4" in target_text
    elif address != 0x325848:
        assert original[1] == built[1], (original, built)

receipt = {
    "status": "pass",
    "source_sha256": hashlib.sha256((root / "source.c").read_bytes()).hexdigest(),
    "native_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
    "target_disassembly_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
    "instruction_count": 33,
    "native_body_bytes": 96,
    "target_body_bytes": 98,
    "baseline_expansion": "325848 native ld_s r0,[r0,0] -> target full ld r0,[r0]",
    "branch_hint": "Source backward brlo.t assembles to the native brlo.nt encoding at 325822",
    "child_relocations": {"0x325812": "opencfw_em9305_dispatch_child_30e5a4",
                          "0x32582e": "opencfw_em9305_dispatch_child_30e5a4"},
    "scope": "All native instructions and non-call bytes except one baseline LD; child 30e5a4 remains genuine unresolved.",
}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
