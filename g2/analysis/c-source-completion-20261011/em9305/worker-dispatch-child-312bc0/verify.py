#!/usr/bin/env python3
"""Full native selector byte and instruction review."""

import hashlib
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
native_path = root.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
target_path = root / "target/source.dis"


def parse(text):
    rows = []
    for line in text.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\t([0-9a-f ]+)\t(\S.*)", line)
        if match:
            rows.append((int(match[1], 16), match[2].strip().replace(" ", ""), match[3].split("\t")[0]))
    return rows


native = [row for row in parse(native_path.read_text()) if 0x312BC0 <= row[0] < 0x312BE4]
target = [row for row in parse(target_path.read_text()) if row[0] < 36]
assert len(native) == len(target) == 14
assert sum(len(row[1]) // 2 for row in native) == 36
assert sum(len(row[1]) // 2 for row in target) == 36
for original, built in zip(native, target):
    assert original[0] - 0x312BC0 == built[0]
    assert original[1:] == built[1:]

receipt = {"status": "pass", "instruction_count": 14, "body_bytes_exact": 36,
           "source_sha256": hashlib.sha256((root / "source.c").read_bytes()).hexdigest(),
           "native_sha256": hashlib.sha256(native_path.read_bytes()).hexdigest(),
           "target_disassembly_sha256": hashlib.sha256(target_path.read_bytes()).hexdigest(),
           "scope": "Complete body exact bytes, branch targets and delay slots; no child imports."}
(root / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
