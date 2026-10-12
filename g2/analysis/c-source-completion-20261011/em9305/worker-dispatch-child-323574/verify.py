#!/usr/bin/env python3
"""Verify the complete native callback encoding against the ARC object."""

import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
native_path = root.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
target_path = root / "target/source.dis"
native_text, target_text = native_path.read_text(), target_path.read_text()


def parse(text):
    out = []
    for line in text.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}(?:\s+|$)){1,2})\s*(\S.*)", line)
        if match:
            out.append((int(match[1], 16), match[2].strip().replace(" ", ""), match[3].split("\t")[0], line))
    return out


native = [item for item in parse(native_text) if 0x323574 <= item[0] < 0x323592]
target = [item for item in parse(target_text) if item[0] < 0x1E]
assert len(native) == len(target) == 11
assert sum(len(item[1]) // 2 for item in native) == 30
assert sum(len(item[1]) // 2 for item in target) == 30
for original, built in zip(native, target):
    assert original[0] == 0x323574 + built[0]
    assert original[2] == built[2]
    if original[0] == 0x323586:
        assert original[3].rstrip().endswith("0x30e79c")
        assert "12: R_ARC_S25W_PCREL\topencfw_em9305_ll_event_callback_30e79c" in target_text
    else:
        assert original[1] == built[1]

receipt = {
    "status": "pass",
    "source_sha256": hashlib.sha256((root / "source.c").read_bytes()).hexdigest(),
    "native_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
    "target_disassembly_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
    "instruction_count": 11,
    "body_bytes": 30,
    "child_relocation": "0x323586 -> opencfw_em9305_ll_event_callback_30e79c",
    "scope": "All bytes exact except one genuine BL relocation; trailing alignment nop excluded.",
}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
