#!/usr/bin/env python3
"""Check the full named ARC callback against native instructions and child calls."""

import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
NATIVE = ROOT.parents[3] / "build/c-firmware/20261011/em-inspection-full.arcem.txt"
TARGET = ROOT / "target/source.dis"
BASE, END = 0x31CA28, 0x31CB1E
CHILDREN = {
    0x31CA36: (0x322C94, "opencfw_em9305_dispatch_child_322c94"),
    0x31CA3E: (0x322BAC, "opencfw_em9305_dispatch_child_322bac"),
    0x31CA8A: (0x316AD4, "opencfw_em9305_radio_stream_allocate_316ad4"),
    0x31CAA4: (0x327718, "opencfw_em9305_radio_stream_setup_327718"),
    0x31CAF8: (0x31CCF4, "opencfw_em9305_dispatch_child_31ccf4"),
    0x31CB02: (0x3142F8, "opencfw_em9305_wsf_timer_start_ms"),
    0x31CB0E: (0x31CB40, "opencfw_em9305_dispatch_callback_31cb40"),
    0x31CB16: (0x322E80, "opencfw_em9305_dispatch_child_322e80"),
}
BASELINE_EXPANSION = 0x31CAF4


def instructions(content):
    found = []
    for line in content.splitlines():
        match = re.match(r"\s*([0-9a-f]+):\s+((?:[0-9a-f]{4}(?:\s+|$)){1,2})\s*(\S.*)", line)
        if match:
            found.append((int(match[1], 16), match[2].strip().replace(" ", ""), match[3].split("\t")[0], line))
    return found


native_text = NATIVE.read_text()
target_text = TARGET.read_text()
native = [row for row in instructions(native_text) if BASE <= row[0] < END]
target = [row for row in instructions(target_text) if row[0] < 0xF8]
assert len(native) == len(target) == 81
assert sum(len(row[1]) // 2 for row in native) == 244
assert sum(len(row[1]) // 2 for row in target) == 246

for original, built in zip(native, target):
    address = original[0]
    offset = 2 if address > BASELINE_EXPANSION else 0
    assert built[0] == address - BASE + offset, (original, built)
    if address == BASELINE_EXPANSION:
        assert original[2] == "ld_s" and built[2] == "ld"
        assert "r0,[r15,0]" in re.sub(r"\s+", "", original[3])
        assert "r0,[r15]" in re.sub(r"\s+", "", built[3])
    else:
        assert original[2] == built[2], (original, built)
    if address in CHILDREN:
        child_address, symbol = CHILDREN[address]
        assert original[3].rstrip().endswith(f"0x{child_address:x}")
        assert f"{built[0]:x}: R_ARC_S25W_PCREL\t{symbol}" in target_text
    elif address == BASELINE_EXPANSION:
        pass
    elif address in (0x31CA90, 0x31CB0C):
        destination = 0x31CB0E if address == 0x31CA90 else 0x31CB16
        assert original[3].rstrip().endswith(f"0x{destination:x}")
        assert f"<L{destination:x}>" in built[3]
    else:
        assert original[1] == built[1], (original, built)

receipt = {
    "status": "pass",
    "source_sha256": hashlib.sha256((ROOT / "source.c").read_bytes()).hexdigest(),
    "native_listing_sha256": hashlib.sha256(NATIVE.read_bytes()).hexdigest(),
    "target_disassembly_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
    "instruction_count": 81,
    "native_body_bytes": 244,
    "target_body_bytes": 246,
    "baseline_expansion": "31caf4 native ld_s r0,[r15,0] -> target full ld r0,[r15,0]",
    "child_relocations": {f"0x{address:x}": symbol for address, (_, symbol) in CHILDREN.items()},
    "scope": "Full named ISA body and genuine children; baseline LD shifts two internal branch encodings.",
}
(ROOT / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps(receipt, indent=2))
