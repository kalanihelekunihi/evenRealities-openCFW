#!/usr/bin/env python3
"""Check complete native 31ca0c callback bytes and genuine relocations."""

import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
native_path = root.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
target_path = root / "target/source.dis"
native_text, target_text = native_path.read_text(), target_path.read_text()


def parse(text):
    result = []
    for line in text.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\t([0-9a-f ]+)\t(\S.*)", line)
        if match:
            result.append((int(match[1], 16), match[2].strip().replace(" ", ""), match[3].split("\t")[0], line))
    return result


native = [row for row in parse(native_text) if 0x31CA0C <= row[0] < 0x31CA26]
target = [row for row in parse(target_text) if row[0] < 0x1A]
assert len(native) == len(target) == 9
assert sum(len(row[1]) // 2 for row in native) == 26
assert sum(len(row[1]) // 2 for row in target) == 26
children = {0x31CA18: (0x33301C, "opencfw_em9305_memset"),
            0x31CA1E: (0x31CEB4, "opencfw_em9305_dispatch_callback_31ceb4")}
for original, built in zip(native, target):
    assert original[0] - 0x31CA0C == built[0]
    assert original[2] == built[2]
    if original[0] in children:
        address, symbol = children[original[0]]
        assert original[3].rstrip().endswith(f"0x{address:x}")
        assert f"{built[0]:x}: R_ARC_S25W_PCREL\t{symbol}" in target_text
    else:
        assert original[1] == built[1]

receipt = {"status": "pass", "instruction_count": 9, "body_bytes": 26,
           "source_sha256": hashlib.sha256((root / "source.c").read_bytes()).hexdigest(),
           "native_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
           "target_disassembly_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
           "child_relocations": {f"0x{key:x}": symbol for key, (_, symbol) in children.items()},
           "scope": "Full native body, all non-call bytes exact; two genuine BL relocations."}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
