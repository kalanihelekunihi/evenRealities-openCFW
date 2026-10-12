#!/usr/bin/env python3
"""Compare named ARC callback bodies against the authenticated native listing."""

import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
NATIVE = ROOT.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
TARGET = ROOT / "target/source.dis"
BASE = 0x31CB20
END = 0x31CB82
CHILDREN = {
    0x31CB26: (0x322F08, "opencfw_em9305_ll_record_error_322f08"),
    0x31CB2E: (0x322E80, "opencfw_em9305_dispatch_child_322e80"),
    0x31CB34: (0x31AC84, "opencfw_em9305_radio_record_release_31ac84"),
    0x31CB3A: (0x30E48C, "opencfw_em9305_command_count_down_30e48c"),
    0x31CB44: (0x304588, "opencfw_em9305_common_release_304588"),
    0x31CB68: (0x323574, "opencfw_em9305_dispatch_child_323574"),
    0x31CB70: (0x322F08, "opencfw_em9305_ll_record_error_322f08"),
    0x31CB76: (0x31AC84, "opencfw_em9305_radio_record_release_31ac84"),
    0x31CB7C: (0x30E48C, "opencfw_em9305_command_count_down_30e48c"),
}


def instructions(content):
    found = []
    for line in content.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}(?:\s+|$)){1,2})\s*(\S.*)", line)
        if match:
            found.append((int(match[1], 16), match[2].strip().replace(" ", ""), match[3].split("\t")[0]))
    return found


native_text = NATIVE.read_text()
target_text = TARGET.read_text()
native = [item for item in instructions(native_text) if BASE <= item[0] < END]
target = [item for item in instructions(target_text) if item[0] < END - BASE]
assert len(native) == len(target) == 35
assert [item[0] for item in native] == [item[0] + BASE for item in target]
assert sum(len(item[1]) // 2 for item in native) == 98
assert sum(len(item[1]) // 2 for item in target) == 98

for source, built in zip(native, target):
    address = source[0]
    assert source[2] == built[2], (hex(address), source[2], built[2])
    if address in CHILDREN:
        expected_address, expected_symbol = CHILDREN[address]
        assert source[2].startswith("bl")
        native_line = next(line for line in native_text.splitlines() if re.match(rf"\s*{address:x}:", line))
        assert native_line.rstrip().endswith(f"0x{expected_address:x}")
        assert f"{built[0]:x}: R_ARC_S25W_PCREL\t{expected_symbol}" in target_text
    else:
        assert source[1] == built[1], (hex(address), source[1], built[1])

receipt = {
    "status": "pass",
    "source_sha256": hashlib.sha256((ROOT / "source.c").read_bytes()).hexdigest(),
    "native_listing_sha256": hashlib.sha256(NATIVE.read_bytes()).hexdigest(),
    "target_disassembly_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    "instruction_count": 35,
    "body_byte_count": 98,
    "child_relocation_count": 9,
    "child_relocations": {f"0x{addr:x}": symbol for addr, (_, symbol) in CHILDREN.items()},
    "scope": "Two full named ARC callback bodies; all non-call bytes exact. BL operands remain genuine relocations.",
}
(ROOT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
